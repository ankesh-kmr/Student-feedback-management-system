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
PAGES = ["Give feedback", "Responses", "Course insights"]

st.set_page_config(
    page_title="Course feedback | Student Experience",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
      --ink: #1d302f;
      --muted: #687875;
      --green: #1e6257;
      --green-dark: #173c37;
      --line: #e1e8e4;
      --paper: #ffffff;
      --canvas: #f5f7f4;
    }
    .stApp { background: var(--canvas); color: var(--ink); }
    div[data-testid="stMainBlockContainer"] {
      max-width: 1380px;
      padding: 2rem 2.5rem 3.5rem;
    }
    h1, h2, h3, h4 { color: var(--ink); }
    h1 { font-family: Georgia, "Times New Roman", serif; font-weight: 500; letter-spacing: -.035em; }
    h2, h3, h4 { letter-spacing: -.02em; }

    /* Quiet, persistent navigation */
    section[data-testid="stSidebar"] {
      background: var(--green-dark);
      border-right: 1px solid rgba(255,255,255,.08);
    }
    section[data-testid="stSidebar"] * { color: #edf4f0; }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #b9ccc5; }
    .brand-lockup { display:flex; align-items:center; gap:.75rem; padding:.25rem .1rem 1.3rem; }
    .brand-mark { display:grid; place-items:center; width:2.25rem; height:2.25rem;
      border:1px solid rgba(255,255,255,.35); border-radius:7px; color:#fff;
      font-family:Georgia,serif; font-size:1.2rem; }
    .brand-name { color:#fff; font-size:.95rem; font-weight:700; letter-spacing:.015em; }
    .brand-caption { color:#a9c0b8; font-size:.68rem; letter-spacing:.11em; text-transform:uppercase; }
    section[data-testid="stSidebar"] div[role="radiogroup"] { gap:.3rem; }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
      padding:.56rem .72rem; border-radius:7px; transition:background .15s ease;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:rgba(255,255,255,.08); }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p { color:#edf4f0; font-weight:550; }
    section[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.15); }
    .sidebar-foot { border-top:1px solid rgba(255,255,255,.15); padding-top:1rem;
      margin-top:1.1rem; color:#a9c0b8; font-size:.78rem; line-height:1.55; }

    /* Page heading and status */
    .page-heading { display:flex; align-items:flex-end; justify-content:space-between; gap:1.5rem;
      border-bottom:1px solid var(--line); padding-bottom:1.25rem; margin-bottom:1.25rem; }
    .eyebrow { color:var(--green); font-size:.68rem; font-weight:750; letter-spacing:.15em;
      text-transform:uppercase; margin-bottom:.5rem; }
    .page-heading h1 { font-size:2.45rem; line-height:1.08; margin:0 0 .45rem; }
    .page-heading p { color:var(--muted); margin:0; font-size:.98rem; }
    .portal-status { display:flex; align-items:center; gap:.5rem; white-space:nowrap;
      color:var(--green); background:#e8f0eb; border:1px solid #d5e3da;
      border-radius:99px; padding:.42rem .72rem; font-size:.75rem; font-weight:650; }
    .portal-status span { width:.43rem; height:.43rem; background:#4c8a67; border-radius:50%; }

    /* Compact overview measures */
    div[data-testid="stMetric"] {
      background:var(--paper); border:1px solid var(--line); border-radius:10px;
      padding:.82rem 1rem; box-shadow:none;
    }
    div[data-testid="stMetricLabel"] { color:var(--muted); font-size:.8rem; font-weight:600; }
    div[data-testid="stMetricValue"] { color:var(--ink); font-family:Georgia,"Times New Roman",serif; font-size:1.65rem; }
    div[data-testid="stMetricDelta"] { font-size:.72rem; }

    /* Navigation and content surfaces */
    div[data-testid="stTabs"] button { font-weight:600; }
    div[data-testid="stForm"] {
      background:var(--paper); border:1px solid var(--line); border-radius:11px;
      padding:1.25rem 1.35rem; box-shadow:0 4px 18px rgba(25,49,43,.035);
    }
    div[data-testid="stFormSubmitButton"] button {
      background:var(--green); border:1px solid var(--green); border-radius:7px;
      font-weight:650; min-height:2.7rem;
    }
    div[data-testid="stFormSubmitButton"] button:hover { background:#174e45; border-color:#174e45; }
    div[data-testid="stDataFrame"] { background:#fff; border:1px solid var(--line); border-radius:9px; overflow:hidden; }
    div[data-testid="stAlert"] { border-radius:8px; }
    .support-title { color:var(--ink); font-family:Georgia,"Times New Roman",serif;
      font-size:1.2rem; margin:0 0 .6rem; }
    .support-copy { color:var(--muted); font-size:.9rem; line-height:1.6; }
    .eyebrow-small { color:var(--green); font-size:.66rem; font-weight:750;
      letter-spacing:.12em; text-transform:uppercase; margin-bottom:.55rem; }
    .quiet-note { color:var(--muted); font-size:.82rem; }

    @media (max-width: 760px) {
      div[data-testid="stMainBlockContainer"] { padding:1.2rem 1rem 2.2rem; }
      .page-heading { align-items:flex-start; flex-direction:column; gap:.8rem; }
      .page-heading h1 { font-size:2rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    """
    <div class="brand-lockup">
      <div class="brand-mark">S</div>
      <div>
        <div class="brand-name">Student Experience</div>
        <div class="brand-caption">Course feedback</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.markdown("<div class='brand-caption'>Workspace</div>", unsafe_allow_html=True)
page = st.sidebar.radio(
    "Workspace navigation",
    PAGES,
    label_visibility="collapsed",
    key="active_page",
)
st.sidebar.markdown(
    """
    <div class="sidebar-foot">
      A considered feedback process helps teaching teams understand what is
      working and where a course can improve.
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    init_db()
    feedback = get_all_feedback()
    average_rating = get_average_rating()
    highest_rated_course = get_highest_rated_course()
    course_summary = get_course_summary()
except sqlite3.Error as error:
    st.error(f"Could not load feedback data from SQLite: {error}")
    st.stop()

page_descriptions = {
    "Give feedback": (
        "Your perspective matters.",
        "Share a thoughtful course rating and help make the learning experience better.",
    ),
    "Responses": (
        "Student responses.",
        "Review submitted feedback and find responses by course, student, or comment.",
    ),
    "Course insights": (
        "A view across courses.",
        "Compare course ratings and response volume in one place.",
    ),
}
title, description = page_descriptions[page]
st.markdown(
    f"""
    <div class="page-heading">
      <div>
        <div class="eyebrow">Academic experience&nbsp; / &nbsp;Feedback portal</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <div class="portal-status"><span></span> Portal open</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "Give feedback":
    metric_columns = st.columns(3, gap="medium")
    metric_columns[0].metric("Responses received", f"{len(feedback):,}")
    metric_columns[1].metric(
        "Average course rating",
        f"{average_rating:.2f} / 5" if not feedback.empty else "—",
    )
    metric_columns[2].metric("Courses represented", f"{len(course_summary):,}")
    st.write("")

    form_column, guidance_column = st.columns([1.75, 1], gap="large")
    with form_column:
        st.markdown("### Submit course feedback")
        st.markdown(
            '<p class="quiet-note">Complete the short form below. Fields marked with an asterisk are required.</p>',
            unsafe_allow_html=True,
        )
        if st.session_state.pop("feedback_submitted", False):
            st.success("Your feedback has been submitted. Thank you for taking the time.")

        with st.form("feedback_form", clear_on_submit=True):
            student_column, course_column = st.columns(2, gap="medium")
            with student_column:
                student_name = st.text_input(
                    "Student name *", max_chars=120, placeholder="Your name"
                )
            with course_column:
                course_name = st.text_input(
                    "Course name *", max_chars=120, placeholder="Course you are reviewing"
                )
            st.markdown("**Overall course rating**")
            rating = st.select_slider(
                "Choose a rating",
                options=[1, 2, 3, 4, 5],
                value=4,
                format_func=lambda value: f"{value} · {RATING_LABELS[value]}",
                label_visibility="collapsed",
            )
            comments = st.text_area(
                "Comments (optional)",
                max_chars=2000,
                placeholder="What has helped your learning? What could be improved?",
                height=120,
            )
            submitted = st.form_submit_button(
                "Submit response", type="primary", width="stretch"
            )

        if submitted:
            if not student_name.strip() or not course_name.strip():
                st.error("Please enter your name and course name before submitting.")
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

    with guidance_column:
        st.write("")
        st.write("")
        with st.container(border=True):
            st.markdown('<div class="eyebrow-small">Writing a useful response</div>', unsafe_allow_html=True)
            st.markdown('<div class="support-title">A little detail goes a long way.</div>', unsafe_allow_html=True)
            st.markdown(
                """
                <div class="support-copy">
                  <p><strong>Be specific.</strong> Mention a lecture, project, or resource that stood out.</p>
                  <p><strong>Think about learning.</strong> Share what made a concept easier or harder to understand.</p>
                  <p><strong>Offer a suggestion.</strong> A practical idea can help instructors decide what to try next.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.caption("Your comments are optional. A rating on its own is still helpful.")

elif page == "Responses":
    st.markdown("### Feedback record")
    if feedback.empty:
        st.info("There are no feedback responses yet.")
    else:
        filter_column, search_column = st.columns([1, 1.4], gap="medium")
        courses = sorted(
            feedback["course_name"].dropna().unique().tolist(), key=str.casefold
        )
        with filter_column:
            selected_course = st.selectbox("Course", ["All courses", *courses])
        with search_column:
            search_text = st.text_input(
                "Search name or comment", placeholder="Type to filter responses"
            )

        filtered_feedback = feedback
        if selected_course != "All courses":
            filtered_feedback = filtered_feedback.loc[
                filtered_feedback["course_name"] == selected_course
            ]
        if search_text.strip():
            term = search_text.strip()
            matches = (
                filtered_feedback["student_name"].str.contains(
                    term, case=False, regex=False, na=False
                )
                | filtered_feedback["comments"].fillna("").str.contains(
                    term, case=False, regex=False, na=False
                )
            )
            filtered_feedback = filtered_feedback.loc[matches]

        display_feedback = filtered_feedback.iloc[::-1].rename(
            columns={
                "feedback_id": "ID",
                "student_name": "Student",
                "course_name": "Course",
                "rating": "Rating",
                "comments": "Comments",
            }
        )
        st.dataframe(
            display_feedback,
            hide_index=True,
            width="stretch",
            column_config={
                "Rating": st.column_config.NumberColumn("Rating", format="%d / 5")
            },
        )
        st.caption(
            f"Showing {len(filtered_feedback):,} of {len(feedback):,} responses"
        )

else:
    st.markdown("### Course performance")
    if course_summary.empty:
        st.info("Course insights will appear here after feedback has been submitted.")
    else:
        leader_rating = None
        leader_count = None
        if highest_rated_course:
            leader = course_summary.loc[
                course_summary["course_name"] == highest_rated_course
            ]
            if not leader.empty:
                leader_rating = float(leader.iloc[0]["average_rating"])
                leader_count = int(leader.iloc[0]["feedback_count"])

        insight_columns = st.columns(3, gap="medium")
        insight_columns[0].metric(
            "Highest-rated course", highest_rated_course or "—"
        )
        insight_columns[1].metric(
            "Leading course average",
            f"{leader_rating:.2f} / 5" if leader_rating is not None else "—",
        )
        insight_columns[2].metric(
            "Responses for leading course",
            f"{leader_count:,}" if leader_count is not None else "—",
        )
        st.write("")
        table_column, chart_column = st.columns([1, 1.35], gap="large")
        with table_column:
            st.markdown("#### Course summary")
            display_summary = course_summary.rename(
                columns={
                    "course_name": "Course",
                    "feedback_count": "Responses",
                    "average_rating": "Average rating",
                }
            )
            st.dataframe(
                display_summary,
                hide_index=True,
                width="stretch",
                column_config={
                    "Responses": st.column_config.NumberColumn(
                        "Responses", format="%d"
                    ),
                    "Average rating": st.column_config.NumberColumn(
                        "Average rating", format="%.2f / 5"
                    ),
                },
            )
        with chart_column:
            st.markdown("#### Average rating by course")
            st.bar_chart(
                course_summary.set_index("course_name")["average_rating"],
                y_label="Average rating (out of 5)",
                x_label="Course",
                color="#1e6257",
            )
