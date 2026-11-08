from .database import Database


class ChatDataSaver:
    """
    ذخیره‌سازی اطلاعات چت‌ها (خصوصی، گروه، کانال، ناشناخته) در دیتابیس SQLite.

    همه‌ی جدول‌ها ساختار یکسانی دارند (مطابق مدل Chat):
        chat_id (PK), chat_type, user_id, first_name, last_name, title, username
    """

    def __init__(self) -> None:
        self.database: Database = Database("chats_data.db")
        self.private_table: str = "private_table"
        self.group_table: str = "group_table"
        self.channel_table: str = "channel_table"
        self.unknown_table: str = "unknown_table"
        self._create_tables()

    # ---------------------------------------------------------
    # ساخت جدول‌ها
    # ---------------------------------------------------------

    @staticmethod
    def _schema() -> dict:
        """ساختار یکسان برای همه‌ی جدول‌ها (مطابق مدل Chat)."""
        return {
            "chat_id": "TEXT PRIMARY KEY",
            "chat_type": "TEXT",
            "user_id": "TEXT",
            "first_name": "TEXT",
            "last_name": "TEXT",
            "title": "TEXT",
            "username": "TEXT",
        }

    def _create_tables(self) -> None:
        for table in (
            self.private_table,
            self.group_table,
            self.channel_table,
            self.unknown_table,
        ):
            self.database.create_table(table, self._schema())

    # ---------------------------------------------------------
    # نگاشت نوع چت به جدول
    # ---------------------------------------------------------

    @staticmethod
    def _chat_type_to_table(chat_type) -> str:
        """بر اساس ChatTypeEnum یا رشته، نام جدول را برمی‌گرداند."""
        value = getattr(chat_type, "value", chat_type)
        if not isinstance(value, str):
            return "unknown_table"
        value = value.strip().lower()

        if value in ("user", "private", "bot"):
            return "private_table"
        if value == "group":
            return "group_table"
        if value == "channel":
            return "channel_table"
        return "unknown_table"

    # ---------------------------------------------------------
    # ذخیره (set)
    # ---------------------------------------------------------

    def set(self, chat: dict) -> bool:
        """
        یک چت را ذخیره یا به‌روزرسانی می‌کند.
        ورودی: دیکشنری با فیلدهای مدل Chat.
        خروجی: True اگر موفق، False اگر chat_id نداشته باشد.
        """
        chat_id = chat.get("chat_id")
        if not chat_id:
            return False

        chat_type = chat.get("chat_type")
        table = self._chat_type_to_table(chat_type)

        # chat_type را به صورت رشته ذخیره می‌کنیم (اگر Enum بود، value)
        chat_type_value = getattr(chat_type, "value", chat_type) or ""

        data = {
            "chat_id": chat_id,
            "chat_type": chat_type_value,
            "user_id": chat.get("user_id"),
            "first_name": chat.get("first_name"),
            "last_name": chat.get("last_name"),
            "title": chat.get("title"),
            "username": chat.get("username"),
        }

        try:
            self.database.set(table, data)
            return True
        except Exception:
            return False

    # ---------------------------------------------------------
    # خواندن (get)
    # ---------------------------------------------------------

    def get(self, chat_id: str, chat_type=None) -> dict | None:
        """
        اطلاعات یک چت را برمی‌گرداند.
        - اگر chat_type بدی، فقط همان جدول را چک می‌کند.
        - اگر ندادی، همه‌ی جدول‌ها را به ترتیب چک می‌کند.
        """
        if not chat_id:
            return None

        if chat_type is not None:
            table = self._chat_type_to_table(chat_type)
            return self.database.get(table, {"chat_id": chat_id})

        for table in (
            self.private_table,
            self.group_table,
            self.channel_table,
            self.unknown_table,
        ):
            row = self.database.get(table, {"chat_id": chat_id})
            if row:
                return row
        return None

    # ---------------------------------------------------------
    # بررسی وجود (exist)
    # ---------------------------------------------------------

    def exist(self, chat_id: str, chat_type=None) -> bool:
        """آیا این چت (در جدول مشخص یا هر جدولی) ذخیره شده است؟"""
        return self.get(chat_id, chat_type) is not None

    # ---------------------------------------------------------
    # حذف (اختیاری)
    # ---------------------------------------------------------

    def delete(self, chat_id: str, chat_type=None) -> bool:
        """
        چت را حذف می‌کند.
        خروجی: True اگر حداقل یک ردیف حذف شده باشد.
        """
        if not chat_id:
            return False

        tables = (
            [self._chat_type_to_table(chat_type)]
            if chat_type is not None
            else [
                self.private_table,
                self.group_table,
                self.channel_table,
                self.unknown_table,
            ]
        )

        deleted = False
        for table in tables:
            try:
                self.database.remove(table, {"chat_id": chat_id})
                deleted = True
            except Exception:
                pass
        return deleted