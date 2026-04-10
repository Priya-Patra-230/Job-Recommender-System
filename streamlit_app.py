import streamlit as st
import os
import json
from resume_parser import extract_text_from_file, parse_resume_fields
from nlp_utils import build_job_index, match_resume_to_jobs, summarize_profile

st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: #f5f7fb;
}

/* Buttons */
div.stButton > button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
    border: none;
}

div.stButton > button:hover {
    background-color: #45a049;
}

/* Section Headers */
h2, h3 {
    color: #2c3e50;
}

/* Card style */
.card {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.title("📄 Resume Analyzer & Job Matcher")
st.progress(100)
        
JOB_FILE = "jobs.json"

# Load jobs
if os.path.exists(JOB_FILE):
    with open(JOB_FILE, "r", encoding="utf-8") as f:
        jobs = json.load(f)
else:
    jobs = []

job_index = build_job_index(jobs)

# File upload
uploaded_file = st.file_uploader("Upload your Resume", type=["pdf", "docx"])

if uploaded_file:
    os.makedirs("tmp_uploads", exist_ok=True)
    file_path = os.path.join("tmp_uploads", "uploaded_resume." + uploaded_file.name.split(".")[-1])

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info("Processing resume...")

    # Extract text
    text = extract_text_from_file(file_path)

    # Parse profile
    profile = parse_resume_fields(text)
    profile["summary"] = summarize_profile(profile)

    # Match jobs
    matches = match_resume_to_jobs(text, job_index, threshold=0.25)

    # Remove temp file
    try:
        os.remove(file_path)
    except:
        pass

    # Display results
    
    #  st.subheader("👤 Profile Details")
    #  st.json(profile)
    
    st.subheader("👤 Profile Details")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Name:**", profile.get("name", "N/A"))
        st.write("**Email:**", profile.get("email", "N/A"))
        st.write("**Phone:**", profile.get("phone", "N/A"))

    with col2:
        st.write("**Skills:**")
        if profile.get("skills"):
            for skill in profile["skills"]:
                st.markdown(f"- {skill}")
        else:
            st.write("No skills found")

    st.write("**Summary:**")
    st.info(profile.get("summary", "No summary available"))
    
    # st.markdown("## 👤 Profile Details")

    # st.markdown(f"""
    # <div class="card">
    # <b>Name:</b> {profile.get("name", "N/A")} <br>
    # <b>Email:</b> {profile.get("email", "N/A")} <br>
    # <b>Phone:</b> {profile.get("phone", "N/A")} <br>
    # </div>
    # """, unsafe_allow_html=True)

    # st.markdown("### 🛠 Skills")
    # if profile.get("skills"):
    #     st.markdown(f"""
    #     <div class="card">
    #     {", ".join(profile["skills"])}
    #     </div>
    #     """, unsafe_allow_html=True)

    # st.markdown("### 📌 Summary")
    # st.markdown(f"""
    # <div class="card">
    # {profile.get("summary", "No summary available")}
    # </div>
    # """, unsafe_allow_html=True)

    # st.subheader("💼 Job Matches")
    # if matches:
    #     for job in matches:
    #         st.write(job)
    # else:
    #     st.warning("No matching jobs found.")

    # st.subheader("💼 Job Matches")
    # if matches:
    #     for job in matches:
    #         with st.container():
    #             st.markdown(f"### {job.get('title', 'No Title')}")
    #             st.write(f"**Company:** {job.get('company', 'N/A')}")
    #             st.write(f"**Match Score:** {job.get('score', 0)}%")

    #             if job.get("description"):
    #                 st.write("**Description:**")
    #                 st.write(job["description"])

    #             if job.get("skills"):
    #                 st.write("**Required Skills:**")
    #                 st.write(", ".join(job["skills"]))
    #             st.divider()
    # else:
    #     st.warning("No matching jobs found.")
    
    st.markdown("## 💼 Job Matches")
    if matches:
        for job in matches:
            
            score = job.get("score", 0)

            st.markdown(f"""
            <div class="card">
            <h3>{job.get("title", "No Title")}</h3>
            <b>Company:</b> {job.get("company", "N/A")} <br>
            <b>Match Score:</b> <span style="color:green; font-weight:bold;">{score}%</span><br><br>

            <b>Description:</b><br>
            {job.get("description", "N/A")}<br><br>

            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No matching jobs found.")

# Show all jobs
if st.button("📋 Show All Jobs"):
    st.success("Showing available jobs")
    st.json(jobs)
    
# if st.button("Show All Jobs"):
#     st.subheader("📋 Available Jobs")
#     st.json(jobs)
