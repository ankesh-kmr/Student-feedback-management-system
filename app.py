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


RATING_LABELS = {1: "Poor", 2: "Fair", 3: "Good", 4: "Very good", 5: "Excellent"}

st.set_page_config(
    page_title="Student Feedback",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --ink:#182b35; --muted:#71818a; --teal:#087e78; --line:#e6ecea; --soft:#edf8f6; --glow:rgba(8,126,120,.16); }
    .stApp { background:linear-gradient(180deg,#f5f8f7 0%,#eef6f4 100%); color:var(--ink); }
    .main .block-container { max-width:1240px; padding:2.25rem 2rem 4rem; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    h1,h2,h3 { font-family:'Manrope',sans-serif !important; color:var(--ink); }
    .hero { position:relative; overflow:hidden; padding:2.15rem 2.4rem; border-radius:22px;
      background:linear-gradient(115deg,#123d43 0%,#087e78 62%,#18a38e 100%); color:white;
      box-shadow:0 16px 38px rgba(15,85,79,.18); margin-bottom:1.6rem; }
    .hero:after { content:''; position:absolute; width:250px; height:250px; right:-50px; top:-130px;
      border:1px solid rgba(255,255,255,.17); border-radius:50%; box-shadow:0 0 0 35px rgba(255,255,255,.06),0 0 0 70px rgba(255,255,255,.04); }
    .hero-kicker { text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:700; opacity:.76; }
    .hero h1 { color:white !important; font-size:2.15rem; letter-spacing:-.045em; margin:.35rem 0 .45rem; }
    .hero p { color:rgba(255,255,255,.82); margin:0; font-size:1rem; }
    div[data-testid="stMetric"] { background:white; border:1px solid var(--line); border-radius:16px;
      padding:1.1rem 1.25rem; box-shadow:0 8px 22px rgba(20,50,48,.04); transition:transform .2s ease, box-shadow .2s ease; }
    div[data-testid="stMetric"]:hover { transform:translateY(-2px); box-shadow:0 10px 26px rgba(20,50,48,.08); }
    div[data-testid="stMetricLabel"] { color:var(--muted); font-weight:600; }
    div[data-testid="stMetricValue"] { color:var(--ink); font-family:'Manrope',sans-serif; }
    div[data-testid="stTabs"] button { font-weight:600; border-radius:10px 10px 0 0; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color:var(--teal); background:rgba(8,126,120,.06); }
    div[data-testid="stForm"] { background:white; border:1px solid var(--line); border-radius:18px;
      padding:1.4rem 1.5rem; box-shadow:0 8px 28px rgba(20,50,48,.04); }
    div[data-testid="stFormSubmitButton"] button { border-radius:10px; font-weight:700; background:linear-gradient(135deg,#0a7b75,#0e9d8f); color:white; border:none; }
    div[data-testid="stFormSubmitButton"] button:hover { filter:brightness(1.03); }
    div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
    .section-note { color:var(--muted); margin-top:-.45rem; margin-bottom:1.1rem; }
    .spotlight-card { background:linear-gradient(135deg,rgba(8,126,120,.08),rgba(46,138,168,.06)); border:1px solid rgba(8,126,120,.18); border-radius:20px; padding:1.25rem 1.35rem; box-shadow:0 12px 28px rgba(15,85,79,.08); margin:0 0 1.2rem; }
    .spotlight-badge { display:inline-flex; align-items:center; gap:.45rem; background:rgba(8,126,120,.1); color:var(--teal); border-radius:999px; padding:.38rem .72rem; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
    .spotlight-value { font-family:'Manrope',sans-serif; font-size:2rem; font-weight:800; color:var(--ink); margin:.7rem 0 .2rem; }
    .spotlight-sub { color:var(--muted); }
    .pill-row { display:flex; flex-wrap:wrap; gap:.5rem; margin:0 0 1.1rem; }
    .mini-pill { border:1px solid rgba(8,126,120,.18); background:white; color:var(--ink); border-radius:999px; padding:.45rem .8rem; font-weight:600; font-size:.82rem; box-shadow:0 5px 16px rgba(20,50,48,.03); }
    @media (max-width:700px) { .main .block-container {padding:1.2rem 1rem 2.5rem;} .hero {padding:1.5rem;} .hero h1 {font-size:1.65rem;} .spotlight-value {font-size:1.5rem;} }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
      <div class="hero-kicker">Learning insights</div>
      <h1>Student Feedback</h1>
      <p>A clearer view of what students think, course by course.</p>
    </section>
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

metric_columns = st.columns(3)
metric_columns[0].metric("Feedback received", f"{len(feedback):,}")
metric_columns[1].metric("Average rating", f"{average_rating:.2f} / 5" if not feedback.empty else "—")
metric_columns[2].metric("Top-rated course", highest_rated_course or "—")

show_spotlight = st.toggle("Highlight top-performing course", value=True, help="Show the best-rated course and the overall rating overview.")
if show_spotlight:
    if highest_rated_course:
        spotlight_row = st.columns([1.2, 1.4])
        with spotlight_row[0]:
            st.markdown(
                f"""
                <div class="spotlight-card">
                  <div class="spotlight-badge">⭐ Top course</div>
                  <div class="spotlight-value">{highest_rated_course}</div>
                  <div class="spotlight-sub">Current leading course by average rating</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with spotlight_row[1]:
            st.markdown(
                """
                <div class="spotlight-card">
                  <div class="spotlight-badge">📊 Performance</div>
                  <div class="spotlight-value">{} / 5</div>
                  <div class="spotlight-sub">Overall course sentiment from all submitted feedback</div>
                </div>
                """.format(f"{average_rating:.2f}" if not feedback.empty else "—"),
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="spotlight-card">
              <div class="spotlight-badge">📈 Waiting for feedback</div>
              <div class="spotlight-value">No responses yet</div>
              <div class="spotlight-sub">As soon as students submit ratings, the top course summary will appear here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")
submit_tab, records_tab, summary_tab = st.tabs(
    ["✍️  Submit feedback", "▤  Responses", "▥  Course insights"]
)

with submit_tab:
    st.subheader("Tell us about your experience")
    st.markdown('<p class="section-note">A quick rating and a few words can help improve a course.</p>', unsafe_allow_html=True)

    if st.session_state.pop("feedback_submitted", False):
        st.success("Thanks for sharing your feedback.")

    with st.form("feedback_form", clear_on_submit=True):
        name_col, course_col = st.columns(2)
        with name_col:
            student_name = st.text_input("Student name", max_chars=120, placeholder="e.g. Alex Morgan")
        with course_col:
            course_name = st.text_input("Course name", max_chars=120, placeholder="e.g. Introduction to Biology")
        st.markdown("**How would you rate this course?**")
        rating = st.select_slider(
            "Choose a rating",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda value: f"{value} · {RATING_LABELS[value]}",
            label_visibility="collapsed",
        )
        comments = st.text_area(
            "Comments (optional)", max_chars=2000,
            placeholder="What worked well? What could be better?",
        )
        submitted = st.form_submit_button("Submit feedback", type="primary", width="stretch")

    if submitted:
        if not student_name.strip() or not course_name.strip():
            st.error("Please enter both your name and the course name.")
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
    st.subheader("Student responses")
    st.markdown('<p class="section-note">Browse submitted feedback and filter by course.</p>', unsafe_allow_html=True)
    if feedback.empty:
        st.info("No feedback has been submitted yet.")
    else:
        courses = sorted(feedback["course_name"].dropna().unique().tolist(), key=str.casefold)
        selected_course = st.selectbox("Filter by course", options=["All courses", *courses])
        filtered_feedback = feedback if selected_course == "All courses" else feedback.loc[feedback["course_name"] == selected_course]
        display_feedback = filtered_feedback.rename(
            columns={"feedback_id":"ID", "student_name":"Student", "course_name":"Course", "rating":"Rating", "comments":"Comments"}
        )
        st.dataframe(
            display_feedback,
            hide_index=True,
            width="stretch",
            column_config={"Rating": st.column_config.NumberColumn("Rating", format="%d / 5")},
        )
        st.caption(f"Showing {len(filtered_feedback):,} response(s)")

with summary_tab:
    st.subheader("Course insights")
    st.markdown('<p class="section-note">Compare average ratings and response volume across courses.</p>', unsafe_allow_html=True)
    if course_summary.empty:
        st.info("Course insights will appear after the first feedback is submitted.")
    else:
        display_summary = course_summary.rename(
            columns={"course_name":"Course", "feedback_count":"Responses", "average_rating":"Average rating"}
        )
        table_column, chart_column = st.columns([.9, 1.3], gap="large")
        with table_column:
            st.dataframe(
                display_summary,
                hide_index=True,
                width="stretch",
                column_config={
                    "Responses": st.column_config.NumberColumn("Responses", format="%d"),
                    "Average rating": st.column_config.NumberColumn("Average rating", format="%.2f / 5"),
                },
            )
        with chart_column:
            st.bar_chart(
                course_summary.set_index("course_name")["average_rating"],
                y_label="Average rating (out of 5)",
                x_label="Course",
                color="#087e78",
            )
