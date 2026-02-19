"""Text Analysis Skill - Example skill for OpenClaw."""

import re
from typing import Any

from openclaw_python_skill.skill import Skill


class TextAnalyzerSkill(Skill):
    """Analyze text for statistics, sentiment, and patterns.

    Provides actions for:
    - text_stats: Word count, character count, sentence count
    - text_sentiment: Basic sentiment classification
    - text_patterns: Find URLs, emails, phone numbers
    """

    def __init__(self):
        super().__init__(name="text-analyzer", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Process text analysis actions.

        Args:
            action: One of 'text_stats', 'text_sentiment', 'text_patterns'
            parameters: Action parameters including 'text'

        Returns:
            Analysis results

        Raises:
            ValueError: If action is unknown or parameters missing
        """
        if not parameters.get("text"):
            raise ValueError("Missing required parameter: text")

        text = parameters["text"]

        if action == "text_stats":
            return self._analyze_stats(text)
        elif action == "text_sentiment":
            return self._analyze_sentiment(text)
        elif action == "text_patterns":
            return self._find_patterns(text)
        else:
            raise ValueError(f"Unknown action: {action}")

    def _analyze_stats(self, text: str) -> dict[str, Any]:
        """Analyze text statistics."""
        words = text.split()
        sentences = re.split(r"[.!?]+", text)

        return {
            "word_count": len(words),
            "char_count": len(text),
            "char_count_no_spaces": len(text.replace(" ", "")),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "avg_words_per_sentence": len(words) / max(len([s for s in sentences if s.strip()]), 1),
        }

    def _analyze_sentiment(self, text: str) -> dict[str, Any]:
        """Simple sentiment analysis."""
        positive_words = {"good", "great", "excellent", "nice", "love", "happy", "awesome"}
        negative_words = {"bad", "terrible", "awful", "hate", "sad", "angry", "poor"}

        words_lower = text.lower().split()

        pos_count = sum(1 for w in words_lower if w in positive_words)
        neg_count = sum(1 for w in words_lower if w in negative_words)

        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "positive_words": pos_count,
            "negative_words": neg_count,
            "confidence": (abs(pos_count - neg_count) / max(pos_count + neg_count, 1)),
        }

    def _find_patterns(self, text: str) -> dict[str, Any]:
        """Find patterns in text (URLs, emails, phone numbers)."""
        url_pattern = r"https?://[^\s]+"
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        phone_pattern = r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"

        urls = re.findall(url_pattern, text)
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)

        return {
            "urls": urls,
            "emails": emails,
            "phone_numbers": phones,
            "patterns_found": len(urls) + len(emails) + len(phones),
        }
