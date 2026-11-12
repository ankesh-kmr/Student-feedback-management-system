"""SQLite persistence and analytics for student feedback."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator, Optional

import pandas as pd


DATABASE_PATH = Path(__file__).resolve().with_name("feedback.db")


@contextmanager
def _connection() -> Iterator[sqlite3.Connection]:
    """Provide a transaction-scoped connection and always close it."""
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def init_db() -> None:
    """Create the feedback table if it does not already exist."""
    with _connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                course_name TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                comments TEXT
            )
            """
        )


def insert_feedback(
    student_name: str,
    course_name: str,
    rating: int,
    comments: Optional[str] = None,
) -> int:
    """Insert one feedback record and return its generated ID."""
    if not isinstance(student_name, str) or not student_name.strip():
        raise ValueError("student_name must not be empty.")
    if not isinstance(course_name, str) or not course_name.strip():
        raise ValueError("course_name must not be empty.")
    if isinstance(rating, bool) or not isinstance(rating, int) or not 1 <= rating <= 5:
        raise ValueError("rating must be an integer between 1 and 5.")
    if comments is not None and not isinstance(comments, str):
        raise ValueError("comments must be a string or None.")

    with _connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO feedback (student_name, course_name, rating, comments)
            VALUES (?, ?, ?, ?)
            """,
            (student_name.strip(), course_name.strip(), rating, comments),
        )
        return int(cursor.lastrowid)


def get_all_feedback() -> pd.DataFrame:
    """Return all feedback records in insertion order."""
    with _connection() as connection:
        return pd.read_sql_query(
            """
            SELECT feedback_id, student_name, course_name, rating, comments
            FROM feedback
            ORDER BY feedback_id
            """,
            connection,
        )


def get_average_rating() -> float:
    """Return the average rating, or 0.0 when no feedback exists."""
    with _connection() as connection:
        result = connection.execute(
            "SELECT COALESCE(AVG(rating), 0.0) FROM feedback"
        ).fetchone()
    return float(result[0])


def get_highest_rated_course() -> Optional[str]:
    """Return the highest-average course; ties are broken alphabetically."""
    with _connection() as connection:
        result = connection.execute(
            """
            SELECT course_name
            FROM feedback
            GROUP BY course_name
            ORDER BY AVG(rating) DESC,
                     course_name COLLATE NOCASE ASC,
                     course_name ASC
            LIMIT 1
            """
        ).fetchone()
    return result[0] if result else None


def get_course_summary() -> pd.DataFrame:
    """Return each course's submission count and average rating."""
    feedback = get_all_feedback()
    if feedback.empty:
        return pd.DataFrame(
            columns=["course_name", "feedback_count", "average_rating"]
        )

    summary = (
        feedback.groupby("course_name", as_index=False)
        .agg(
            feedback_count=("feedback_id", "count"),
            average_rating=("rating", "mean"),
        )
        .sort_values(
            "course_name",
            key=lambda names: names.str.casefold(),
            kind="stable",
        )
        .reset_index(drop=True)
    )
    return summary
