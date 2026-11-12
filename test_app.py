"""Unit tests for feedback database operations."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database


class FeedbackDatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        database_path = Path(temporary_directory.name) / "feedback_test.db"

        database_path_patch = patch.object(database, "DATABASE_PATH", database_path)
        database_path_patch.start()
        self.addCleanup(database_path_patch.stop)

        database.init_db()

    def test_empty_database_returns_empty_analytics(self) -> None:
        self.assertEqual(database.get_average_rating(), 0.0)
        self.assertIsNone(database.get_highest_rated_course())
        self.assertTrue(database.get_all_feedback().empty)

        course_summary = database.get_course_summary()
        self.assertTrue(course_summary.empty)
        self.assertEqual(
            list(course_summary.columns),
            ["course_name", "feedback_count", "average_rating"],
        )

    def test_insertions_produce_accurate_analytics(self) -> None:
        database.insert_feedback("Alex", "Computer Science", 5, "Excellent")
        database.insert_feedback("Jordan", "Computer Science", 4, "Engaging")
        database.insert_feedback("Taylor", "Mathematics", 3, "Good pace")
        database.insert_feedback("Morgan", "Mathematics", 5, "Helpful examples")

        self.assertEqual(len(database.get_all_feedback()), 4)
        self.assertEqual(database.get_average_rating(), 4.25)
        self.assertEqual(database.get_highest_rated_course(), "Computer Science")

        summary = database.get_course_summary().set_index("course_name")
        self.assertEqual(summary.loc["Computer Science", "feedback_count"], 2)
        self.assertEqual(summary.loc["Computer Science", "average_rating"], 4.5)
        self.assertEqual(summary.loc["Mathematics", "feedback_count"], 2)
        self.assertEqual(summary.loc["Mathematics", "average_rating"], 4.0)


if __name__ == "__main__":
    unittest.main()
