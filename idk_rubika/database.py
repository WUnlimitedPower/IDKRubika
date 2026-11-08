import sqlite3
from typing import Any, Optional


class Database:
    """کلاس ساده برای کار با دیتابیس SQLite3"""

    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    # ---------------------------------------------------------------
    # اجرای دستور خام
    # ---------------------------------------------------------------
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor

    # ---------------------------------------------------------------
    # ساخت جدول
    # مثال: db.create_table("users", {"id": "INTEGER PRIMARY KEY", "name": "TEXT"})
    # ---------------------------------------------------------------
    def create_table(self, table: str, columns: dict[str, str]) -> None:
        # ستون‌های عادی
        normal = []
        constraints = []
        for name, ctype in columns.items():
            if name.upper().startswith(("PRIMARY KEY", "UNIQUE", "FOREIGN KEY", "CHECK")):
                constraints.append(name)
            else:
                normal.append(f"{name} {ctype}".strip())

        parts = normal + constraints
        cols = ", ".join(parts)
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({cols})")
        self.connection.commit()

    # ---------------------------------------------------------------
    # set: درج یا به‌روزرسانی یک رکورد
    # اولین کلید دیکشنری به عنوان شناسه (کلید یکتا) استفاده می‌شود
    # db.set("users", {"id": 1, "name": "Ali"})
    # ---------------------------------------------------------------
    def set(self, table: str, data: dict[str, Any]) -> None:
        key = next(iter(data))
        key_value = data[key]

        if self.exist(table, {key: key_value}):
            assignments = ", ".join(f"{k} = ?" for k in data if k != key)
            values = tuple(v for k, v in data.items() if k != key) + (key_value,)
            self.cursor.execute(
                f"UPDATE {table} SET {assignments} WHERE {key} = ?", values
            )
        else:
            keys = ", ".join(data.keys())
            placeholders = ", ".join("?" for _ in data)
            self.cursor.execute(
                f"INSERT INTO {table} ({keys}) VALUES ({placeholders})",
                tuple(data.values()),
            )
        self.connection.commit()

    # ---------------------------------------------------------------
    # get: گرفتن رکورد(ها) بر اساس شرط
    # db.get("users", {"id": 1})            -> یک رکورد یا None
    # db.get("users")                       -> همه رکوردها
    # db.get("users", {"name": "Ali"}, many=True) -> همه رکوردهای مطابق
    # ---------------------------------------------------------------
    def get(
        self,
        table: str,
        conditions: Optional[dict[str, Any]] = None,
        many: bool = False,
    ) -> Any:
        query = f"SELECT * FROM {table}"
        params: tuple = ()

        if conditions:
            where = " AND ".join(f"{k} = ?" for k in conditions)
            query += f" WHERE {where}"
            params = tuple(conditions.values())

        self.cursor.execute(query, params)

        if many or not conditions:
            return [dict(row) for row in self.cursor.fetchall()]

        row = self.cursor.fetchone()
        return dict(row) if row else None

    # ---------------------------------------------------------------
    # remove: حذف رکورد(ها) بر اساس شرط
    # db.remove("users", {"id": 1})
    # db.remove("users")  -> حذف همه رکوردها
    # ---------------------------------------------------------------
    def remove(self, table: str, conditions: Optional[dict[str, Any]] = None) -> None:
        query = f"DELETE FROM {table}"
        params: tuple = ()

        if conditions:
            where = " AND ".join(f"{k} = ?" for k in conditions)
            query += f" WHERE {where}"
            params = tuple(conditions.values())

        self.cursor.execute(query, params)
        self.connection.commit()

    # ---------------------------------------------------------------
    # exist: بررسی وجود رکورد
    # db.exist("users", {"id": 1})  -> True / False
    # ---------------------------------------------------------------
    def exist(self, table: str, conditions: dict[str, Any]) -> bool:
        where = " AND ".join(f"{k} = ?" for k in conditions)
        query = f"SELECT 1 FROM {table} WHERE {where} LIMIT 1"
        self.cursor.execute(query, tuple(conditions.values()))
        return self.cursor.fetchone() is not None

    # ---------------------------------------------------------------
    # بستن اتصال
    # ---------------------------------------------------------------
    def close(self) -> None:
        self.connection.close()

    # ---------------------------------------------------------------
    # پشتیبانی از with
    # ---------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()