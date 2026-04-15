import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class BotState:
    def __init__(self, database_url: str) -> None:
        self.db_path = self._extract_sqlite_path(database_url)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @staticmethod
    def _extract_sqlite_path(database_url: str) -> Path:
        prefix = "sqlite:///"
        if not database_url.startswith(prefix):
            raise ValueError("Only sqlite URLs are supported in this starter")
        raw = database_url[len(prefix):]
        return Path(raw).resolve()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_state (
                    user_id TEXT PRIMARY KEY,
                    step_index INTEGER,
                    last_comment_id TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_events (
                    event_id TEXT PRIMARY KEY,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def has_processed_event(self, event_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT event_id FROM processed_events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
            return row is not None

    def mark_event_processed(self, event_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO processed_events(event_id) VALUES (?)",
                (event_id,),
            )

    def get_user_step(self, user_id: str) -> int | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT step_index FROM conversation_state WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            if row is None:
                return None
            return row["step_index"]

    def set_user_step(self, user_id: str, step_index: int, last_comment_id: str | None = None) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO conversation_state(user_id, step_index, last_comment_id)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    step_index = excluded.step_index,
                    last_comment_id = COALESCE(excluded.last_comment_id, conversation_state.last_comment_id),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, step_index, last_comment_id),
            )

    def reset_user(self, user_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM conversation_state WHERE user_id = ?", (user_id,))
