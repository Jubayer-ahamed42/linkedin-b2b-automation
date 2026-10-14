import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from src.config import HISTORY_FILE, get_current_bst_time

logger = logging.getLogger(__name__)

class HistoryManager:
    def __init__(self, history_file: Path = HISTORY_FILE):
        self.history_file = history_file

    def load_history(self) -> List[Dict[str, Any]]:
        """Loads previous LinkedIn posts history."""
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Failed to read history file: {e}. Starting fresh.")
            return []

    def save_history(self, history: List[Dict[str, Any]]) -> None:
        """Saves history atomically to prevent corruption."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            trimmed = history[-200:]
            temp_file = self.history_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(trimmed, f, ensure_ascii=False, indent=2)
            temp_file.replace(self.history_file)
        except Exception as e:
            logger.error(f"Failed to write history file: {e}")

    def record_post(self, theme_id: str, headline: str, summary: str, post_urn: str = "", card_path: str = "") -> None:
        """Records a new published post."""
        history = self.load_history()
        now_str = get_current_bst_time().strftime("%Y-%m-%d %H:%M:%S BST")
        record = {
            "timestamp": now_str,
            "theme_id": theme_id,
            "headline": headline,
            "summary": summary,
            "post_urn": post_urn,
            "card_path": card_path
        }
        history.append(record)
        self.save_history(history)
        logger.info(f"Recorded new LinkedIn post to history: '{headline}'")

    def is_already_posted_today(self) -> Tuple[bool, str]:
        """
        Ensures strict 1-post-per-day cadence.
        Returns (already_posted: bool, last_post_time: str).
        """
        history = self.load_history()
        if not history:
            return False, ""

        now_bst = get_current_bst_time().date()
        for item in reversed(history):
            ts_str = item.get("timestamp", "")
            try:
                dt_part = ts_str.split(" BST")[0].strip()
                post_date = datetime.strptime(dt_part, "%Y-%m-%d %H:%M:%S").date()
                if post_date == now_bst:
                    return True, ts_str
            except Exception:
                pass
        return False, ""

    def get_recent_summary(self, limit: int = 15) -> str:
        """Returns summary of recent topics to avoid repetition in AI generation."""
        history = self.load_history()
        if not history:
            return "No previous LinkedIn posts yet. Start with a fresh high-converting angle."

        recent = history[-limit:]
        lines = []
        for i, item in enumerate(recent, 1):
            h = item.get("headline", "").strip()
            s = item.get("summary", "").strip()
            lines.append(f"{i}. [Past Post]: {h} — ({s})")
        return "\n".join(lines)

    def check_similarity(self, new_headline: str, new_summary: str, threshold: float = 0.55) -> Tuple[bool, str]:
        """Anti-duplicate check comparing token overlap."""
        history = self.load_history()
        if not history:
            return False, ""

        new_tokens = self._extract_tokens(f"{new_headline} {new_summary}")
        if not new_tokens:
            return False, ""

        for past_item in history:
            past_h = past_item.get("headline", "")
            past_s = past_item.get("summary", "")
            past_tokens = self._extract_tokens(f"{past_h} {past_s}")
            if not past_tokens:
                continue

            intersection = new_tokens.intersection(past_tokens)
            union = new_tokens.union(past_tokens)
            sim = len(intersection) / len(union) if union else 0.0

            if sim >= threshold:
                logger.warning(f"Similar topic detected! Matches past post: '{past_h}' (Score: {sim:.2f})")
                return True, past_h

        return False, ""

    def _extract_tokens(self, text: str) -> set:
        clean = re.sub(r"[^\w\s\u0980-\u09FF]", " ", text.lower())
        words = clean.split()
        stop_words = {
            "the", "and", "for", "with", "this", "that", "how", "what", "why", "are", "you",
            "এই", "সেই", "কি", "কী", "কেন", "করে", "করা", "হবে", "হলে", "থেকে", "দিয়ে", "জন্য"
        }
        return {w for w in words if len(w) >= 3 and w not in stop_words}
