import streamlit as st
from google import genai
from dotenv import load_dotenv
import os

# Load API Key

load_dotenv()

API_KEY = os.getenv("API_KEY")

client = genai.Client(api_key=st.secrets["API_KEY"])

# Page Config
st.set_page_config(
    page_title="AI Mock Interview",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 AI Mock Interview & Placement Readiness Analyzer")

with st.expander("💡 Interview Tips"):

    st.write("""
✅ Answer confidently.

✅ Explain your thought process.

✅ Give practical examples.

✅ Don't leave answers blank.
""")

st.write("Practice interviews with AI and check your placement readiness.")

# Session State
defaults = {
    "interview_started": False,
    "interview_completed": False,
    "question": "",
    "question_no": 1,
    "total_questions": 5,
    "answers": [],
    "report": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# Sidebar
st.sidebar.header("Candidate Details")

name = st.sidebar.text_input("Name")

role = st.sidebar.selectbox(
    "Target Role",
    [
        "Data Engineer",
        "Data Analyst",
        "Python Developer",
        "AI/ML Engineer",
        "Backend Developer"
    ]
)

experience = st.sidebar.selectbox(
    "Experience",
    [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]
)

# Buttons
col1, col2 = st.sidebar.columns(2)

with col1:
    start = st.button("▶ Start")

with col2:
    new = st.button("🔄 New")


# Start Interview

if start:

    st.session_state.interview_started = True
    st.session_state.interview_completed = False
    st.session_state.question = ""
    st.session_state.question_no = 1
    st.session_state.answers = []
    st.session_state.report = ""


# New Interview
if new:

    st.session_state.interview_started = False
    st.session_state.interview_completed = False
    st.session_state.question = ""
    st.session_state.question_no = 1
    st.session_state.answers = []
    st.session_state.report = ""

    st.rerun()
if new:

    for key, value in defaults.items():
        st.session_state[key] = value

    st.rerun()

# Waiting Screen

if not st.session_state.interview_started:

    st.info("👈 Enter your details and click **Start**.")

    st.stop()
    
# Generate Question

if st.session_state.question == "":

    previous_questions = "\n".join(
        [item["question"] for item in st.session_state.answers]
    )

    prompt = f"""
You are an experienced technical interviewer.

Candidate Name: {name}

Target Role: {role}

Experience Level: {experience}

This is Question {st.session_state.question_no} of {st.session_state.total_questions}.

Previously asked questions:

{previous_questions}

Rules:
1. Ask ONLY ONE interview question.
2. Do NOT repeat previous questions.
3. Make the question suitable for the candidate level.
4. Do NOT provide hints or answers.
"""

    with st.spinner("🤖 AI is preparing your question..."):

      
try:
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

except Exception:
    st.error(
        "⚠️ Gemini AI is temporarily experiencing high demand."
    )
    st.info(
        "Please wait a few minutes and try again."
    )
    st.stop()


    st.session_state.question = response.text.strip()

# Display Question

progress = st.session_state.question_no / st.session_state.total_questions
st.progress(progress)

st.subheader(
    f"Question {st.session_state.question_no} / {st.session_state.total_questions}"
)

st.write(st.session_state.question)

answer = st.text_area(
    "Your Answer",
    height=180,
    key=f"answer_{st.session_state.question_no}"
)


# Buttons

if st.session_state.question_no < st.session_state.total_questions:
    submit = st.button("Next Question ➜")
else:
    submit = st.button("Finish Interview ✅")



# Save Answer

if submit:

    if answer.strip() == "":
        st.warning("Please answer the question before continuing.")
        st.stop()

    st.session_state.answers.append({
        "question": st.session_state.question,
        "answer": answer
    })

    if st.session_state.question_no < st.session_state.total_questions:

        st.session_state.question_no += 1
        st.session_state.question = ""

        st.rerun()
        
# Final Evaluation


if (
    st.session_state.question_no == st.session_state.total_questions
    and len(st.session_state.answers) == st.session_state.total_questions
    and not st.session_state.interview_completed
):

    analysis_prompt = f"""
You are a Senior Technical Interviewer.

Candidate Name:
{name}

Target Role:
{role}

Experience Level:
{experience}

Below are the interview questions and candidate answers.

{st.session_state.answers}

Evaluate the COMPLETE interview.

Return in this exact format.

Overall Score: __/10

Placement Readiness: __%

Technical Knowledge:
- ...

Communication:
- ...

Strengths:
- ...

Weaknesses:
- ...

Learning Roadmap:
- ...

Final Verdict:
- ...
"""

    with st.spinner("📊 AI is evaluating your interview..."):
        
        result = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=analysis_prompt
        )

        st.session_state.report = result.text
        st.session_state.interview_completed = True

        st.rerun()


# Show Final Report


if st.session_state.interview_completed:

    st.success("🎉 Interview Completed!")
    
    st.balloons()
    
    st.subheader("📊 Final Report")

    st.write(st.session_state.report)

    st.info("Click 🔄 New to start another interview.")
