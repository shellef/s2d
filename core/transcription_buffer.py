"""
Transcription Buffer - Manages speech-to-text transcription with overlapping windows.

This module provides overlapping window extraction for LLM processing,
ensuring continuity and context for understanding corrections and references.
"""


class TranscriptionBuffer:
    """
    Manages transcription history with overlapping window extraction.

    Consecutive calls to get_tail() return overlapping windows to provide
    context continuity for the LLM. This helps the LLM understand corrections
    like "actually, change that to..." and maintain coherent updates.
    """

    def __init__(self, window_size: int = 250):
        """
        Initialize the transcription buffer.

        Args:
            window_size: Number of words to include in the overlapping window.
                        Default is 250 words, which provides sufficient context
                        while keeping token usage reasonable.
        """
        self.full_text: str = ""  # Complete accumulated transcription
        self.window_size: int = window_size

    def append(self, text: str) -> bool:
        """
        Add new transcription text to the buffer.

        Args:
            text: Newly transcribed text from Whisper API

        Returns:
            True if new non-empty text was added (triggers GPT processing),
            False if text was empty or whitespace only
        """
        if not text or not text.strip():
            return False

        # Add space before appending if buffer already has content
        if self.full_text:
            self.full_text += " " + text.strip()
        else:
            self.full_text = text.strip()

        return True

    def get_tail(self) -> str:
        """
        Get overlapping window of recent transcription.

        Always returns the last window_size words, regardless of what's been
        "processed" before. This creates overlapping context between consecutive
        LLM calls, helping the model understand corrections and references.

        Returns:
            String containing the last window_size words from the transcription.
            Returns the full text if it's shorter than window_size.
        """
        if not self.full_text:
            return ""

        words = self.full_text.split()

        # If we have fewer words than window_size, return everything
        if len(words) <= self.window_size:
            return self.full_text

        # Return last window_size words
        tail_words = words[-self.window_size:]
        return " ".join(tail_words)

    def get_full_text(self) -> str:
        """
        Get the complete transcription.

        Returns:
            All accumulated transcription text
        """
        return self.full_text

    def clear(self) -> None:
        """
        Clear all transcription data.

        Useful for starting a new session or resetting state.
        """
        self.full_text = ""

    def word_count(self) -> int:
        """
        Get the total number of words in the buffer.

        Returns:
            Number of words in the full transcription
        """
        if not self.full_text:
            return 0
        return len(self.full_text.split())
