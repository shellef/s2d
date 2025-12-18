"""
LLM Service - OpenAI LLM integration for document processing.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from backend.config import get_settings
from core.prompt_builder import build_update_prompt
from core.patch_generator import parse_llm_response, validate_patch

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for processing transcription with LLM and generating JSON Patch operations.

    Handles prompt construction, API communication, and response parsing.
    """

    def __init__(self):
        """Initialize LLM service with OpenAI client."""
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.gpt_model
        self.verbose_logging = settings.verbose_llm_logging

    async def process_transcription(
        self,
        transcription_tail: str,
        current_document: Dict[str, Any],
        patch_history: Optional[List[List[Dict[str, Any]]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process transcription tail with LLM and return JSON Patch operations.

        Args:
            transcription_tail: Overlapping window of recent transcription (typically 250 words)
            current_document: Current document state for context
            patch_history: Optional history of recent patch operations to prevent repetition

        Returns:
            List of JSON Patch operations to apply to the document

        Raises:
            Exception: If LLM processing fails or response is invalid
        """
        if not transcription_tail or not transcription_tail.strip():
            logger.warning("Empty transcription tail received")
            return []

        try:
            # Build prompt with current document and transcription tail
            messages = build_update_prompt(transcription_tail, current_document, patch_history)

            logger.info(f"Processing {len(transcription_tail)} chars with LLM")

            # Log full context if verbose logging is enabled
            if self.verbose_logging:
                logger.info("=" * 80)
                logger.info("LLM CONTEXT - FULL PROMPT")
                logger.info("=" * 80)
                for i, msg in enumerate(messages):
                    logger.info(f"\n[Message {i+1} - {msg['role']}]:")
                    logger.info(msg['content'])

            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000  # Sufficient for patch operations
            )

            # Extract content
            content = response.choices[0].message.content

            if not content:
                logger.warning("Empty response from LLM")
                return []

            # Log full response if verbose logging is enabled
            if self.verbose_logging:
                logger.info("=" * 80)
                logger.info("LLM RESPONSE - FULL CONTENT")
                logger.info("=" * 80)
                logger.info(content)
                logger.info("=" * 80)
            else:
                logger.debug(f"LLM response: {content[:200]}...")

            # Parse JSON Patch operations
            try:
                patch_ops = parse_llm_response(content)
            except ValueError as e:
                logger.error(f"Failed to parse LLM response: {e}")
                logger.error(f"Raw response: {content}")
                raise Exception(f"Failed to parse LLM response: {str(e)}")

            # Validate patch operations
            is_valid, error = validate_patch(patch_ops, current_document)
            if not is_valid:
                logger.error("=" * 80)
                logger.error("PATCH VALIDATION FAILED")
                logger.error("=" * 80)
                logger.error(f"Error: {error}")
                logger.error(f"Patch operations that failed:")
                logger.error(json.dumps(patch_ops, indent=2))
                logger.error(f"Current document state:")
                logger.error(json.dumps(current_document, indent=2))
                logger.error("=" * 80)
                # Return empty list instead of raising error (graceful degradation)
                return []

            logger.info(f"Generated {len(patch_ops)} valid patch operations")
            if self.verbose_logging:
                logger.info("Patch validation PASSED - patches will be applied")
            return patch_ops

        except Exception as e:
            logger.error(f"LLM processing failed: {e}", exc_info=True)
            # Return empty list for graceful degradation (don't break the flow)
            return []


# Global service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get the global LLM service instance.

    Returns:
        LLMService instance
    """
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService()

    return _llm_service
