"""Streamlit interface for the Student Feedback Management System."""

import sqlite3

import streamlit as st

from database import (
    get_all_feedback,
    get_average_rating,
    get_course_summary,
    get_highest_rated_course,
    init_db,
    insert_feedback,
)


RATING_LABELS = {
    1: "Poor",
    2: "Fair",
    3: "Good",
    4: "Very good",
    5: "Excellent",
}


st.set_page_config(
    page_title="Student Feedback",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #f5f7fb;
    }
    .main .block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .app-header {
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        border: 1px solid #e6eaf2;
        border-radius: 18px;
        background: linear-gradient(120deg, #ffffff 15%, #edf4ff 100%);
    }
    .app-header h1 {
        margin: 0;
        color: #172554;
        font-size: 2rem;
        letter-spacing: -0.035em;
    }
    .app-header p {
        margin: 0.45rem 0 0;
        color: #64748b;
        font-size: 1rem;
    }
    div[data-testid="stMetric"] {
        padding: 1.15rem 1.25rem;
        border: 1px solid #e6eaf2;
        border-radius: 14px;
        background: #ffffff;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.035);
    }
    div[data-testid="stMetricLabel"] {
        color: #64748b;
    }
    div[data-testid="stMetricValue"] {
        color: #172554;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-header">
        <h1>Student Feedback Management</h1>
        <p>Collect feedback, explore course ratings, and track student experience.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    init_db()
    feedback = get_all_feedback()
    average_rating = get_average_rating()
    highest_rated_course = get_highest_rated_course()
except sqlite3.Error as error:
    st.error(f"Could not load feedback data from SQLite: {error}")
    st.stop()

metric_columns = st.columns(3)
metric_columns[0].metric("Total Feedback", f"{len(feedback):,}")
metric_columns[1].metric(
    "Overall Average Rating",
    f"{average_rating:.2f} / 5" if not feedback.empty else "—",
)
metric_columns[2].metric(
    "Highest Rated Course",
    highest_rated_course if highest_rated_course is not None else "—",
)

submit_tab, records_tab, summary_tab = st.tabs(
    ["Submit Feedback", "View Feedback Records", "Course-wise Rating Summary"]
)

with submit_tab:
    st.subheader("Share your feedback")
    st.caption("Your feedback helps instructors improve the learning experience.")

    if st.session_state.pop("feedback_submitted", False):
        st.success("Thank you — your feedback has been submitted.")

    with st.form("feedback_form", clear_on_submit=True):
        student_name = st.text_input("Student Name", max_chars=120)
        course_name = st.text_input("Course Name", max_chars=120)
        rating = st.select_slider(
            "Rating",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda value: f"{value} — {RATING_LABELS[value]}",
        )
        comments = st.text_area(
            "Comments (optional)",
            max_chars=2000,
            placeholder="What went well? What could be improved?",
        )
        submitted = st.form_submit_button(
            "Submit Feedback",
            type="primary",
            width="stretch",
        )

    if submitted:
        if not student_name.strip() or not course_name.strip():
            st.error("Please enter both a student name and a course name.")
        else:
            try:
                insert_feedback(
                    student_name=student_name.strip(),
                    course_name=course_name.strip(),
                    rating=int(rating),
                    comments=comments.strip() or None,
                )
            except ValueError as error:
                st.error(f"Please check your submission: {error}")
            except sqlite3.Error as error:
                st.error(f"Feedback could not be saved: {error}")
            else:
                st.session_state["feedback_submitted"] = True
                st.rerun()

with records_tab:
    st.subheader("Feedback records")
    if feedback.empty:
        st.info("No feedback has been submitted yet.")
    else:
        courses = sorted(
            feedback["course_name"].dropna().unique().tolist(),
            key=str.casefold,
        )
        selected_course = st.selectbox(
            "Filter by course",
            options=["All courses", *courses],
        )
        filtered_feedback = feedback
        if selected_course != "All courses":
            filtered_feedback = feedback.loc[
                feedback["course_name"] == selected_course
            ]

        display_feedback = filtered_feedback.rename(
            columns={
                "feedback_id": "Feedback ID",
                "student_name": "Student Name",
                "course_name": "Course Name",
                "rating": "Rating",
                "comments": "Comments",
            }
        )
        st.dataframe(
            display_feedback,
            hide_index=True,
            width="stretch",
            column_config={
                "Rating": st.column_config.NumberColumn(
                    "Rating",
                    format="%d / 5",
                )
            },
        )
        st.caption(f"Showing {len(filtered_feedback):,} feedback record(s).")

with summary_tab:
    st.subheader("Course-wise rating summary")
    try:
        course_summary = get_course_summary()
    except sqlite3.Error as error:
        st.error(f"Could not load the course summary: {error}")
    else:
        if course_summary.empty:
            st.info("Course analytics will appear after feedback is submitted.")
        else:
            display_summary = course_summary.rename(
                columns={
                    "course_name": "Course Name",
                    "feedback_count": "Feedback Count",
                    "average_rating": "Average Rating",
                }
            )
            table_column, chart_column = st.columns([1, 1.25])

            with table_column:
                st.dataframe(
                    display_summary,
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "Feedback Count": st.column_config.NumberColumn(
                            "Feedback Count",
                            format="%d",
                        ),
                        "Average Rating": st.column_config.NumberColumn(
                            "Average Rating",
                            format="%.2f / 5",
                        ),
                    },
                )

            with chart_column:
                st.bar_chart(
                    course_summary.set_index("course_name")["average_rating"],
                    y_label="Average rating (out of 5)",
                    x_label="Course",
                    color="#356AE6",
                )
