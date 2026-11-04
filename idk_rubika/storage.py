import json
import logging
import os
from pathlib import Path
from typing import Optional


class OffsetStore:
    """
    ذخیره و بازیابی آخرین offset_id برای هر بات، بر اساس username بات.
    فایل‌ها در پوشه‌ی offsets/ با نام {username}.json ذخیره می‌شن.
    توکن بات هیچ‌جا ذخیره نمی‌شه.
    """

    def __init__(self, base_dir: str = "offsets"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _file_path(self, username: str) -> Path:
        # جلوگیری از کاراکترهای خطرناک توی نام فایل
        safe_username = "".join(
            c for c in username if c.isalnum() or c in ("_", "-", ".")
        )
        if not safe_username:
            safe_username = "unknown_bot"
        return self.base_dir / f"{safe_username}.json"

    def load(self, username: str) -> str:
        """آخرین offset_id ذخیره‌شده رو برمی‌گردونه، یا رشته خالی اگه نبود."""
        path = self._file_path(username)
        if not path.exists():
            return ""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return str(data.get("offset_id", ""))
        except (json.JSONDecodeError, OSError) as error:
            logging.warning("Could not load offset for %s: %s", username, error)
            return ""

    def save(self, username: str, offset_id: str) -> None:
        """آخرین offset_id رو ذخیره می‌کنه."""
        path = self._file_path(username)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"offset_id": offset_id}, f)
        except OSError as error:
            logging.error("Could not save offset for %s: %s", username, error)