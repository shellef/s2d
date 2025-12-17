"""
Simple LiveKit + AssemblyAI Transcription Agent

This agent connects to LiveKit, captures audio, and sends transcriptions
to your backend via WebSocket.

Run this alongside your FastAPI backend.
"""

import asyncio
import logging
import os
from livekit import rtc, api
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
from livekit.agents.stt import SpeechEventType
from livekit.plugins import assemblyai
import websockets
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def entrypoint(ctx: JobContext):
    """
    Simple transcription agent entrypoint.

    Captures audio from LiveKit room and sends transcriptions to backend.
    """
    logger.info(f"Agent started for room: {ctx.room.name}")

    # Connect to LiveKit room first
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    logger.info("Connected to LiveKit room")

    # Connect to your backend WebSocket
    backend_ws = None
    try:
        backend_ws = await websockets.connect('ws://localhost:8000/ws')
        logger.info("Connected to backend WebSocket")
    except Exception as e:
        logger.error(f"Failed to connect to backend: {e}")
        return

    # Initialize AssemblyAI STT with your API key
    stt = assemblyai.STT(
        api_key=os.getenv("ASSEMBLYAI_API_KEY", "c62f057171f846cba51cf6d27a1d689d")
    )

    # Subscribe to audio tracks
    async def transcribe_track(track: rtc.RemoteAudioTrack):
        """Transcribe audio from a track."""
        logger.info(f"Transcribing track: {track.sid}")

        # Create audio stream from track
        audio_stream = rtc.AudioStream(track)

        # Stream to AssemblyAI
        async with stt.stream() as stream:
            # Handle transcription events in a separate task
            async def handle_events():
                async for event in stream:
                    if event.type == SpeechEventType.INTERIM_TRANSCRIPT:
                        logger.debug(f"Partial: {event.alternatives[0].text}")
                    elif event.type == SpeechEventType.FINAL_TRANSCRIPT:
                        logger.info(f"Final: {event.alternatives[0].text}")

                        # Send to backend
                        if backend_ws and event.alternatives[0].text:
                            try:
                                await backend_ws.send(json.dumps({
                                    "type": "transcription",
                                    "text": event.alternatives[0].text
                                }))
                            except Exception as e:
                                logger.error(f"Failed to send to backend: {e}")

            # Start event handler
            event_task = asyncio.create_task(handle_events())

            # Feed audio to STT - AudioFrameEvent has a 'frame' attribute
            async for event in audio_stream:
                stream.push_frame(event.frame)

            # Wait for event handler to complete
            await event_task

    # Handle new participants
    @ctx.room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, *_):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            asyncio.create_task(transcribe_track(track))

    logger.info("Agent ready, waiting for audio tracks...")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            # Set your LiveKit credentials via environment variables:
            # LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
        )
    )
