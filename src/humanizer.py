"""
LinkedIn Humanizer V3 Engine
Implements anti-AI detection, vocabulary density scoring, reveal-bridge scrubbing,
em-dash calibration, and tone humanization based on 2026 stylometry research.
"""

import re
import logging
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)

# Forensic leakage markers that should never appear in published posts
FORENSIC_PATTERNS = [
    r"\boaicite\b",
    r"\bcontentReference\b",
    r"\bturn\d+search\d+\b",
    r"\battached_file\b",
    r"\bgrok_card\b",
    r"As of my (last update|knowledge cutoff)[^.]*\.",
    r"\[Your Name\]",
    r"\[Your Company\]",
    r"\[Insert [^]]+\]",
    r"\[Describe [^]]+\]",
]

# Reveal bridges that kill dwell-time and trigger algorithm penalties
REVEAL_BRIDGES = [
    (r"(?im)^The (result|outcome|lesson|catch|truth|kicker)\?\s*", ""),
    (r"(?im)^Plot twist:\s*", ""),
    (r"(?im)^Here'?s (the thing|what happened|the secret|the takeaway|why)[:.]\s*", ""),
    (r"(?im)^The takeaway\?\s*", ""),
    (r"(?im)^Why does this matter\?\s*", ""),
    (r"(?im)^Let that sink in\.?\s*", ""),
]

# 2026 High-frequency AI vocabulary and preferred natural alternatives
AI_VOCAB_MAPPINGS = {
    r"\bdelve into\b": "explore",
    r"\bdelve\b": "look into",
    r"\btapestry\b": "mix",
    r"\brevolutioniz(e|es|ed|ing)\b": "transform",
    r"\bgame[- ]changer\b": "breakthrough",
    r"\bfurthermore\b": "also",
    r"\bit is important to note that\b": "keep in mind,",
    r"\bit is worth noting that\b": "notably,",
    r"\bleverag(e|es|ed|ing)\b": "use",
    r"\bstreamlin(e|es|ed|ing)\b": "simplify",
    r"\bholistic\b": "complete",
    r"\bmultifaceted\b": "varied",
    r"\brobust\b": "strong",
    r"\bseamlessly\b": "smoothly",
    r"\bseamless\b": "smooth",
    r"\bfoster(s|ed|ing)?\b": "build",
    r"\btestament to\b": "proof of",
    r"\blet that sink in\b": "",
    r"\bcrucial\b": "key",
    r"\bsignificant(ly)?\b": "major",
    r"\blandscape\b": "industry",
    r"\belevat(e|es|ed|ing)\b": "improve",
    r"\bempower(s|ed|ing)?\b": "enable",
    r"\becosystem\b": "system",
    r"\bnuanced\b": "detailed",
    r"\bcomprehensive\b": "thorough",
    r"\binsights\b": "takeaways",
    r"\bdive deep\b": "take a closer look",
    r"\bin today's fast[- ]paced (digital )?world\b": "today",
}

class LinkedInHumanizer:
    """Post-processor that transforms AI drafts into authentic, high-converting human posts."""

    def __init__(self, mode: str = "strict"):
        self.mode = mode

    def clean_forensic_markers(self, text: str) -> str:
        """Removes model leakage, AI placeholders, and cutoff disclaimers."""
        for pattern in FORENSIC_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return text

    def clean_reveal_bridges(self, text: str) -> str:
        """Removes formulaic AI reveal bridges and transitions."""
        for pattern, replacement in REVEAL_BRIDGES:
            text = re.sub(pattern, replacement, text)
        return text

    def calibrate_em_dashes(self, text: str, max_allowed: int = 2) -> str:
        """
        Caps em-dashes at max 1-2 per post.
        Excess em-dashes are converted to natural commas or colons.
        """
        em_count = text.count("—")
        if em_count <= max_allowed:
            return text

        parts = text.split("—")
        # Keep the first instance as em-dash, replace subsequent excess with comma/colon
        result = [parts[0]]
        for i, part in enumerate(parts[1:], 1):
            if i < max_allowed:
                result.append("—" + part)
            else:
                # Alternate between colon and comma for natural flow
                sep = ": " if i == max_allowed else ", "
                result.append(sep + part.lstrip())
        return "".join(result)

    def normalize_punctuation(self, text: str) -> str:
        """Normalizes curly quotes, double hyphens, and whitespace."""
        text = text.replace("“", '"').replace("”", '"')
        text = text.replace("‘", "'").replace("’", "'")
        text = re.sub(r"\s*--\s*", ", ", text)
        return text

    def scrub_ai_vocabulary(self, text: str) -> Tuple[str, List[str]]:
        """Replaces AI vocabulary and returns list of cleaned terms."""
        replaced_terms = []
        for pattern, replacement in AI_VOCAB_MAPPINGS.items():
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                replaced_terms.extend([m if isinstance(m, str) else m[0] for m in matches])
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text, replaced_terms

    def format_spacing(self, text: str) -> str:
        """Ensures mobile-optimized spacing (1-2 lines per paragraph)."""
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        # Join with double newlines for mobile readability
        return "\n\n".join(paragraphs)

    def humanize(self, text: str) -> Dict[str, Any]:
        """
        Executes complete multi-pass humanization pipeline on a LinkedIn post.
        Returns cleaned text, metadata, and audit summary.
        """
        original = text
        text = self.clean_forensic_markers(text)
        text = self.clean_reveal_bridges(text)
        text = self.normalize_punctuation(text)
        text, vocab_cleaned = self.scrub_ai_vocabulary(text)
        text = self.calibrate_em_dashes(text)
        text = self.format_spacing(text)

        # Audit indicators
        has_question_opener = bool(re.match(r"^\s*[^.?!]+\?\s*$", text.split("\n\n")[0] if "\n\n" in text else ""))
        char_count = len(text)
        word_count = len(text.split())

        return {
            "humanized_text": text,
            "original_length": len(original),
            "final_length": char_count,
            "word_count": word_count,
            "vocab_cleaned": vocab_cleaned,
            "question_opener_warning": has_question_opener,
            "is_humanized": True
        }


# Global singleton helper
_humanizer = LinkedInHumanizer()

def humanize_linkedin_post(text: str) -> Dict[str, Any]:
    """Helper function to run LinkedIn Humanizer pipeline on post copy."""
    return _humanizer.humanize(text)
