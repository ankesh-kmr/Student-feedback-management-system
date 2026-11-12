# Student Feedback Management System

A lightweight web application for collecting student feedback and reviewing
course ratings. The app uses Streamlit for the interface and SQLite for
persistent local storage.

## Project Overview and Key Features

Students can submit a course rating and optional comments through a validated
feedback form. The app provides:

- KPI cards for total feedback, overall average rating, and highest-rated
  course.
- A filterable table of feedback records.
- A course-wise summary with submission counts and average ratings.
- A bar chart comparing average ratings by course.
- Empty-state messaging when the database has no feedback yet.
- Input validation for student names, course names, and ratings from 1 to 5.

The highest-rated course is based on average rating. If multiple courses tie,
the course name is selected alphabetically, case-insensitively.

## Technology Stack

- **Python** — application and database logic.
- **Streamlit** — interactive web interface.
- **SQLite** — local relational database, accessed through Python's built-in
  `sqlite3` module.
- **pandas** — tabular feedback records and course-wise summaries.

## Database Schema

The SQLite database file is named `feedback.db` and is created in the project
directory when the app initializes the database. Its `feedback` table has the
following schema:

| Column | Type | Constraints | Description |
|---|---|---|---|
| `feedback_id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique ID generated for each feedback record. |
| `student_name` | `TEXT` | `NOT NULL` | Name of the student submitting feedback. |
| `course_name` | `TEXT` | `NOT NULL` | Name of the course being rated. |
| `rating` | `INTEGER` | `NOT NULL`, `CHECK (rating BETWEEN 1 AND 5)` | Course rating from 1 to 5. |
| `comments` | `TEXT` | Nullable | Optional written feedback. |

The table is initialized automatically by `database.init_db()`. The database
file is local application data and is not required in order to start the app.

## Local Setup

Run these commands from the project directory.

### 1. Create a virtual environment

**Windows PowerShell:**

```powershell
py -m venv .venv
```

**macOS or Linux:**

```bash
python3 -m venv .venv
```

### 2. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bat
.venv\Scripts\activate.bat
```

**macOS or Linux:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the app

```bash
streamlit run app.py
```

Streamlit prints a local URL in the terminal (typically
`http://localhost:8501`) where the application can be opened in a browser.

## Running Unit Tests

With the project environment activated, run the built-in `unittest` suite:

```bash
python -m unittest test_app.py
```

The tests use a temporary SQLite database, so they do not add records to the
project's `feedback.db`.
