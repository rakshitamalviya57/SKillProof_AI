
import re
import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="SkillProof AI",
    page_icon="🎯",
    layout="wide"
)


# ---------------- SKILL DATABASE ----------------

CAREER_SKILLS = {
    "Python Developer": [
        "Python", "SQL", "Git", "Pandas",
        "NumPy", "OOP", "Problem Solving"
    ],

    "Data Analyst": [
        "Python", "SQL", "Excel", "Pandas",
        "NumPy", "Power BI", "Statistics"
    ],

    "Machine Learning Engineer": [
        "Python", "NumPy", "Pandas",
        "Machine Learning", "Scikit-learn",
        "SQL", "Statistics"
    ],

    "Web Developer": [
        "HTML", "CSS", "JavaScript",
        "Python", "SQL", "Git"
    ],

    "AI Engineer": [
        "Python", "NumPy", "Pandas",
        "Machine Learning", "Deep Learning",
        "TensorFlow", "SQL"
    ]
}


# ---------------- SKILL NORMALIZATION ----------------

def normalize_skill(skill):

    aliases = {
        "py": "python",
        "c++": "c++",
        "cpp": "c++",
        "pandas": "pandas",
        "numpy": "numpy",
        "git hub": "github",
        "ml": "machine learning",
        "oop": "oop"
    }

    skill = skill.strip().lower()
    return aliases.get(skill, skill)


def find_skills(text):

    known_skills = [
        "Python", "C++", "C", "Java",
        "SQL", "Git", "GitHub", "Pandas",
        "NumPy", "HTML", "CSS", "JavaScript",
        "Excel", "Power BI", "Machine Learning",
        "Deep Learning", "TensorFlow",
        "Scikit-learn", "Statistics",
        "OOP", "Problem Solving"
    ]

    detected = []

    for skill in known_skills:

        pattern = (
            r"(?<![a-zA-Z0-9+#])"
            + re.escape(skill)
            + r"(?![a-zA-Z0-9+#])"
        )

        if re.search(pattern, text, re.IGNORECASE):
            detected.append(skill)

    return detected


# ---------------- PDF READER ----------------

def extract_resume_text(uploaded_file):

    if PdfReader is None:
        st.error("Please install pypdf using pip install pypdf")
        return ""

    try:
        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    except Exception as error:
        st.error(f"Unable to read PDF: {error}")
        return ""


# ---------------- SKILL ANALYSIS ----------------

def analyze_skills(student_skills, required_skills):

    student = {
        normalize_skill(skill)
        for skill in student_skills
    }

    required = {
        normalize_skill(skill)
        for skill in required_skills
    }

    matched = [
        skill for skill in required
        if skill in student
    ]

    missing = [
        skill for skill in required
        if skill not in student
    ]

    total = len(required)

    percentage = (
        (len(matched) / total) * 100
        if total > 0 else 0
    )

    return matched, missing, percentage


# ---------------- MAIN HEADER ----------------

st.title("🎯 SkillProof AI")

st.subheader("Smart Career & Skill Gap Analyzer")

st.write(
    "Analyze your skills, discover missing skills "
    "and find your career readiness score."
)

st.divider()


# ---------------- STUDENT PROFILE ----------------

st.sidebar.title("Student Profile")

student_name = st.sidebar.text_input(
    "Enter your name",
    placeholder="Enter your name"
)

st.sidebar.info(
    "Upload your resume or enter your skills manually."
)


# ---------------- TABS ----------------

tab1, tab2, tab3 = st.tabs([
    "Skill Analyzer",
    "Career Explorer",
    "About Project"
])


# ==================================================
# TAB 1: SKILL ANALYZER
# ==================================================

with tab1:

    st.header("Analyze Your Skills")

    uploaded_file = st.file_uploader(
        "Upload your Resume (PDF)",
        type=["pdf"]
    )

    detected_skills = []

    if uploaded_file:

        resume_text = extract_resume_text(uploaded_file)

        if resume_text:

            detected_skills = find_skills(resume_text)

            st.success("Resume analyzed successfully!")

            st.write("**Detected Skills:**")

            if detected_skills:
                st.write(", ".join(detected_skills))
            else:
                st.warning(
                    "No known skills detected. "
                    "Please enter your skills manually."
                )

    manual_skills = st.text_input(
        "Enter your skills separated by commas",
        placeholder="Python, Pandas, SQL, Git"
    )

    manual_list = [
        skill.strip()
        for skill in manual_skills.split(",")
        if skill.strip()
    ]

    all_skills = list(dict.fromkeys(
        detected_skills + manual_list
    ))

    st.divider()

    st.subheader("Select Your Target Career")

    target_career = st.selectbox(
        "Choose a career",
        list(CAREER_SKILLS.keys())
    )

    required_skills = CAREER_SKILLS[target_career]

    st.write("**Required Skills:**")

    st.write(", ".join(required_skills))

    analyze_button = st.button(
        "Analyze My Skills",
        type="primary",
        use_container_width=True
    )

    if analyze_button:

        if not student_name.strip():
            st.warning("Please enter your name in Student Profile.")

        elif not all_skills:
            st.warning(
                "Please upload a resume or enter your skills."
            )

        else:

            matched, missing, percentage = analyze_skills(
                all_skills,
                required_skills
            )

            st.session_state["analysis"] = {
                "name": student_name,
                "career": target_career,
                "matched": matched,
                "missing": missing,
                "percentage": percentage,
                "student_skills": all_skills
            }

    # DISPLAY REPORT

    if "analysis" in st.session_state:

        result = st.session_state["analysis"]

        st.divider()

        st.header("Your Career Analysis Report")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Job Readiness",
            f"{result['percentage']:.1f}%"
        )

        col2.metric(
            "Matched Skills",
            len(result["matched"])
        )

        col3.metric(
            "Missing Skills",
            len(result["missing"])
        )

        if result["percentage"] >= 70:
            st.success("Great! You are well prepared for this career.")

        elif result["percentage"] >= 40:
            st.info("Good progress! Improve your missing skills.")

        else:
            st.warning("Keep learning and improving your skills.")

        st.subheader("Skill Matching Analysis")

        chart_data = pd.DataFrame({
            "Skill Category": ["Matched Skills", "Missing Skills"],
            "Count": [
                len(result["matched"]),
                len(result["missing"])
            ]
        })

        fig = px.pie(
            chart_data,
            names="Skill Category",
            values="Count",
            hole=0.5,
            title="Skill Matching Analysis"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Matched Skills")

            if result["matched"]:
                for skill in result["matched"]:
                    st.write(f"✅ {skill}")
            else:
                st.write("No matched skills yet.")

        with col2:
            st.subheader("Missing Skills")

            if result["missing"]:
                for skill in result["missing"]:
                    st.write(f"❌ {skill}")
            else:
                st.write("All required skills matched!")

        st.divider()

        st.subheader("Personalized Learning Suggestions")

        if result["missing"]:

            for skill in result["missing"]:
                st.write(
                    f"📚 Learn and practice **{skill}**"
                )

        else:
            st.success(
                "You have all the skills listed for this career!"
            )

        report = f"""
SkillProof AI - Career Analysis Report

Student Name: {result['name']}
Target Career: {result['career']}
Job Readiness: {result['percentage']:.1f}%

Matched Skills:
{', '.join(result['matched'])}

Missing Skills:
{', '.join(result['missing'])}
"""

        st.download_button(
            "Download Career Report",
            data=report,
            file_name="SkillProof_Career_Report.txt",
            mime="text/plain"
        )


# ==================================================
# TAB 2: CAREER EXPLORER
# ==================================================

with tab2:

    st.header("Explore Different Careers")

    for career, skills in CAREER_SKILLS.items():

        with st.expander(career):

            st.write("**Required Skills:**")

            st.write(", ".join(skills))

            st.write(
                f"Total Required Skills: {len(skills)}"
            )


# ==================================================
# TAB 3: ABOUT PROJECT
# ==================================================

with tab3:

    st.header("About SkillProof AI")

    st.write("""
    SkillProof AI is a Smart Career and Skill Gap Analyzer.

    It helps students understand their current skills
    and compare them with the skills required for
    different career opportunities.

    Main Features:

    1. Resume PDF Upload
    2. Automatic Skill Detection
    3. Manual Skill Entry
    4. Career Selection
    5. Matched and Missing Skills
    6. Job Readiness Percentage
    7. Skill Matching Visualization
    8. Personalized Learning Suggestions
    9. Downloadable Career Report

    Technologies Used:

    - Python
    - Streamlit
    - Pandas
    - Plotly
    - PyPDF
    """)

    st.info(
        "Developed as a student mini-project."
    )

st.divider()

st.caption("SkillProof AI | Smart Career & Skill Gap Analyzer")
