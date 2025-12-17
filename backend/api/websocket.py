"""
WebSocket Handler - Real-time communication for speech-to-document.
"""

import base64
import logging
import time
import jsonpatch
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
from backend.services.session_manager import get_session_manager
from backend.services.transcription_service import get_transcription_service
from backend.services.llm_service import get_llm_service
from backend.models.message import (
    parse_client_message,
    create_transcription_message,
    create_document_patch_message,
    create_status_message,
    create_error_message,
)
from core.patch_generator import apply_patch

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: Optional[str] = None):
    """
    WebSocket endpoint for real-time speech-to-document processing.

    Flow:
    1. Client connects and sends audio chunks
    2. Server transcribes with Whisper immediately
    3. Server sends transcription to client
    4. Server processes transcription tail with GPT-4o immediately
    5. Server sends JSON Patch operations to client
    6. Repeat until client stops recording

    Args:
        websocket: WebSocket connection
        session_id: Optional session ID from query params
    """
    # Accept connection
    await websocket.accept()
    logger.info(f"WebSocket connection accepted (session_id={session_id})")

    # Get services
    session_manager = get_session_manager()
    transcription_service = get_transcription_service()
    llm_service = get_llm_service()

    # Create or get session
    try:
        if session_id:
            session = session_manager.get_session(session_id)
            if not session:
                await websocket.send_json(create_error_message("Session not found"))
                await websocket.close()
                return
        else:
            session = session_manager.create_session()
            session_id = session.session_id

        logger.info(f"Using session: {session_id}")

    except Exception as e:
        logger.error(f"Failed to create/get session: {e}")
        await websocket.send_json(create_error_message(f"Session error: {str(e)}"))
        await websocket.close()
        return

    try:
        # Main message loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            try:
                message = parse_client_message(data)
            except ValueError as e:
                logger.warning(f"Invalid message format: {e}")
                await websocket.send_json(create_error_message(f"Invalid message: {str(e)}"))
                continue

            # Handle audio_chunk message
            if message.type == "audio_chunk":
                try:
                    # Send status: processing
                    await websocket.send_json(
                        create_status_message("processing", "Transcribing audio...")
                    )

                    # Decode base64 audio
                    try:
                        audio_data = base64.b64decode(message.data)
                        logger.info(f"Received audio chunk: format={message.format}, size={len(audio_data)} bytes")
                    except Exception as e:
                        logger.error(f"Failed to decode audio: {e}")
                        await websocket.send_json(create_error_message("Invalid audio data"))
                        continue

                    # Transcribe with Whisper immediately
                    try:
                        text = await transcription_service.transcribe_audio(
                            audio_data,
                            audio_format=message.format
                        )
                    except Exception as e:
                        logger.error(f"Transcription failed: {e}")
                        await websocket.send_json(
                            create_error_message(f"Transcription failed: {str(e)}")
                        )
                        continue

                    # Send transcription to client immediately
                    if text:
                        await websocket.send_json(
                            create_transcription_message(text, timestamp=time.time())
                        )

                        # Add to buffer
                        has_new_text = session.add_transcription(text)

                        if has_new_text:
                            # Get overlapping tail for GPT-4o
                            tail = session.get_transcription_tail()

                            # Process with GPT-4o immediately (no delay)
                            try:
                                patch_ops = await llm_service.process_transcription(
                                    tail,
                                    session.document
                                )

                                # Apply patches to session document if we got any
                                if patch_ops:
                                    try:
                                        updated_document = apply_patch(patch_ops, session.document)
                                        session.update_document(updated_document)

                                        # Send patches to client
                                        await websocket.send_json(
                                            create_document_patch_message(patch_ops)
                                        )

                                        logger.info(
                                            f"Session {session_id}: Applied {len(patch_ops)} patches"
                                        )
                                    except Exception as e:
                                        logger.error(f"Failed to apply patches: {e}")
                                        # Continue processing, don't break the flow

                            except Exception as e:
                                logger.error(f"LLM processing failed: {e}")
                                # Continue processing, don't send error to client
                                # (graceful degradation - transcription still works)

                    # Send status: idle
                    await websocket.send_json(
                        create_status_message("idle", "Ready for next audio chunk")
                    )

                except Exception as e:
                    logger.error(f"Error processing audio chunk: {e}", exc_info=True)
                    await websocket.send_json(
                        create_error_message(f"Processing error: {str(e)}")
                    )

            # Handle transcription message (from LiveKit agent)
            elif message.type == "transcription":
                logger.info(f"Session {session_id}: Received transcription: {message.text[:50]}...")

                # Forward transcription to client
                await websocket.send_json(create_transcription_message(message.text))

                # Process with GPT-4o to generate document updates
                await websocket.send_json(
                    create_status_message("processing", "Generating document updates...")
                )

                try:
                    # Get LLM service
                    llm_service = get_llm_service()

                    # Process transcription and get document patches
                    patches = await llm_service.process_transcription(
                        transcription_tail=message.text,
                        current_document=session.document
                    )

                    # Apply patches to session document
                    session.document = jsonpatch.apply_patch(session.document, patches)

                    # Send patches to client
                    await websocket.send_json(create_document_patch_message(patches))

                    # Send idle status
                    await websocket.send_json(create_status_message("idle", "Ready"))

                except Exception as e:
                    logger.error(f"Failed to process transcription: {e}", exc_info=True)
                    await websocket.send_json(
                        create_error_message(f"Processing failed: {str(e)}")
                    )

            # Handle stop_recording message
            elif message.type == "stop_recording":
                logger.info(f"Session {session_id}: Recording stopped")
                session.mark_stopped()
                await websocket.send_json(
                    create_status_message("idle", "Recording stopped")
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        # Clean up session on disconnect
        # Note: For production, you might want to keep the session for a while
        # in case the client reconnects
        logger.info(f"Cleaning up session {session_id}")
        # session_manager.cleanup_session(session_id)  # Commented out - keep session for now
