import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from src.config import HISTORY_FILE, get_current_bst_time

logger = logging.getLogger(__name__)

class HistoryManager:
    def __init__(self, history_file: Path = HISTORY_FILE):
        self.history_file = history_file

    def load_history(self) -> List[Dict[str, Any]]:
        """Loads previous posts history."""
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
        """Saves history with a maximum limit of recent 50 entries."""
        try:
            # Keep up to 50 recent items
            trimmed = history[-50:]
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(trimmed, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to write history file: {e}")

    def record_post(self, slot: str, theme: str, title: str, summary: str, post_id: str = "") -> None:
        """Records a new post in the history."""
        history = self.load_history()
        now_str = get_current_bst_time().strftime("%Y-%m-%d %H:%M:%S BST")
        record = {
            "timestamp": now_str,
            "slot": slot,
            "theme": theme,
            "title": title,
            "summary": summary,
            "post_id": post_id
        }
        history.append(record)
        self.save_history(history)
        logger.info(f"Recorded new post to history: '{title}' ({slot})")

    def get_recent_topics_summary(self, slot: str = None, limit: int = 15) -> str:
        """
        Returns a formatted text list of recent topics to feed into the AI prompt
        to prevent duplicate or repetitive content.
        """
        history = self.load_history()
        if not history:
            return "এখনো কোনো পূর্ববর্তী পোস্ট রেকর্ড নেই।"

        if slot:
            filtered = [item for item in history if item.get("slot") == slot]
        else:
            filtered = history

        recent = filtered[-limit:]
        if not recent:
            return "এই স্লটের জন্য এখনো কোনো পূর্ববর্তী পোস্ট রেকর্ড নেই।"

        lines = []
        for i, item in enumerate(recent, 1):
            title = item.get("title", "")
            summary = item.get("summary", "")
            lines.append(f"{i}. {title} - ({summary})")

        return "\n".join(lines)
