"""
Tests for TranscriptionBuffer - Overlapping window extraction.
"""

import pytest
from core.transcription_buffer import TranscriptionBuffer


class TestTranscriptionBuffer:
    """Test cases for TranscriptionBuffer class."""

    def test_initialization(self):
        """Test buffer initializes with correct default values."""
        buffer = TranscriptionBuffer()
        assert buffer.window_size == 250
        assert buffer.get_full_text() == ""
        assert buffer.word_count() == 0

    def test_initialization_custom_window_size(self):
        """Test buffer initializes with custom window size."""
        buffer = TranscriptionBuffer(window_size=100)
        assert buffer.window_size == 100

    def test_append_single_text(self):
        """Test appending a single piece of text."""
        buffer = TranscriptionBuffer()
        result = buffer.append("Hello world")
        assert result is True
        assert buffer.get_full_text() == "Hello world"
        assert buffer.word_count() == 2

    def test_append_multiple_texts(self):
        """Test appending multiple pieces of text."""
        buffer = TranscriptionBuffer()
        buffer.append("First sentence.")
        buffer.append("Second sentence.")
        buffer.append("Third sentence.")

        assert buffer.get_full_text() == "First sentence. Second sentence. Third sentence."
        assert buffer.word_count() == 6

    def test_append_empty_text(self):
        """Test that appending empty text returns False and doesn't modify buffer."""
        buffer = TranscriptionBuffer()
        buffer.append("Initial text")

        result1 = buffer.append("")
        result2 = buffer.append("   ")
        result3 = buffer.append(None)

        assert result1 is False
        assert result2 is False
        assert result3 is False
        assert buffer.get_full_text() == "Initial text"

    def test_get_tail_short_text(self):
        """Test get_tail returns full text when shorter than window size."""
        buffer = TranscriptionBuffer(window_size=250)
        buffer.append("Short text here")

        tail = buffer.get_tail()
        assert tail == "Short text here"

    def test_get_tail_exact_window_size(self):
        """Test get_tail when text is exactly window_size words."""
        buffer = TranscriptionBuffer(window_size=5)
        buffer.append("one two three four five")

        tail = buffer.get_tail()
        assert tail == "one two three four five"

    def test_get_tail_exceeds_window_size(self):
        """Test get_tail returns only last window_size words."""
        buffer = TranscriptionBuffer(window_size=5)

        # Add 10 words
        buffer.append("one two three four five six seven eight nine ten")

        tail = buffer.get_tail()
        assert tail == "six seven eight nine ten"
        assert len(tail.split()) == 5

    def test_overlapping_windows(self):
        """Test that consecutive get_tail calls produce overlapping windows."""
        buffer = TranscriptionBuffer(window_size=5)

        # First batch
        buffer.append("one two three")
        tail1 = buffer.get_tail()
        assert tail1 == "one two three"

        # Second batch - should overlap with first
        buffer.append("four five six")
        tail2 = buffer.get_tail()
        assert tail2 == "two three four five six"

        # Third batch - should overlap with second
        buffer.append("seven eight")
        tail3 = buffer.get_tail()
        assert tail3 == "four five six seven eight"

        # Verify each tail overlaps with the next
        assert "two three" in tail1
        assert "two three" in tail2
        assert "four five six" in tail2
        assert "four five six" in tail3

    def test_get_tail_empty_buffer(self):
        """Test get_tail returns empty string for empty buffer."""
        buffer = TranscriptionBuffer()
        assert buffer.get_tail() == ""

    def test_clear(self):
        """Test clearing the buffer."""
        buffer = TranscriptionBuffer()
        buffer.append("Some text here")
        assert buffer.word_count() > 0

        buffer.clear()
        assert buffer.get_full_text() == ""
        assert buffer.word_count() == 0
        assert buffer.get_tail() == ""

    def test_word_count(self):
        """Test word counting functionality."""
        buffer = TranscriptionBuffer()
        assert buffer.word_count() == 0

        buffer.append("one")
        assert buffer.word_count() == 1

        buffer.append("two three")
        assert buffer.word_count() == 3

        buffer.append("four five six seven")
        assert buffer.word_count() == 7

    def test_realistic_scenario(self):
        """Test a realistic speech-to-text scenario with multiple chunks."""
        buffer = TranscriptionBuffer(window_size=250)

        # Simulate receiving transcription in chunks
        chunk1 = "The process starts when a customer signs up for our service."
        chunk2 = "Then the sales team receives a notification."
        chunk3 = "Actually, change that - it starts when sales receives a lead."
        chunk4 = "The first step is to verify the customer information."

        buffer.append(chunk1)
        buffer.append(chunk2)
        buffer.append(chunk3)
        buffer.append(chunk4)

        # Get tail should include context about the correction
        tail = buffer.get_tail()
        assert "Actually, change that" in tail
        assert "sales receives a lead" in tail

        # Full text should contain everything
        full = buffer.get_full_text()
        assert chunk1 in full
        assert chunk2 in full
        assert chunk3 in full
        assert chunk4 in full

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        buffer = TranscriptionBuffer()

        buffer.append("  text with spaces  ")
        buffer.append("\t\ttabbed text\t")
        buffer.append("\n\nnewline text\n")

        full = buffer.get_full_text()
        # Should be cleaned and joined with single spaces
        assert "text with spaces" in full
        assert "tabbed text" in full
        assert "newline text" in full

    def test_large_buffer(self):
        """Test buffer with more than 250 words."""
        buffer = TranscriptionBuffer(window_size=10)

        # Generate 100 words
        words = [f"word{i}" for i in range(100)]
        text = " ".join(words)
        buffer.append(text)

        tail = buffer.get_tail()
        tail_words = tail.split()

        # Should have exactly 10 words
        assert len(tail_words) == 10
        # Should be the last 10 words
        assert tail_words == words[-10:]

    def test_state_preservation(self):
        """Test that buffer state is preserved correctly across operations."""
        buffer = TranscriptionBuffer(window_size=5)

        buffer.append("one two")
        state1 = buffer.get_full_text()

        buffer.get_tail()  # Getting tail shouldn't modify state
        state2 = buffer.get_full_text()

        assert state1 == state2

        buffer.append("three four")
        state3 = buffer.get_full_text()

        assert state3 != state1
        assert "one two three four" == state3
