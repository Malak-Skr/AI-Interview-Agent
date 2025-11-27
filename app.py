# app.py
import streamlit as st
import google.generativeai as genai
from prompts import SYSTEM_PERSONA
from rag_engine import get_pdf_text, create_vector_db

# Page Setup
st.set_page_config(page_title="AI Mock Interviewer", layout="wide")

# # Check for API key presence
# if not st.secrets["GOOGLE_API_KEY"]:
#     st.error("Please add your GOOGLE_API_KEY to the .env or secrets.toml file.")
#     st.stop()
    
# # Configure Gemini Model
# genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])


import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)


st.title("🎤 AI Interview Agent")
st.markdown("Upload your resume + job description, and I will conduct an interview with you!")

# 1. Sidebar: File Uploads and Job Description
with st.sidebar:
    st.header("1. Interview Data")
    # Streamlit handles uploaded files as UploadedFile objects
    resume_pdf = st.file_uploader("Upload Resume (PDF)", type="pdf")
    jd_text = st.text_area("Paste Job Description here")
    
    start_btn = st.button("Start Interview")

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# 2. Processing Logic (RAG) and Starting the Interview
if start_btn:
    if resume_pdf and jd_text:
        with st.spinner("Analyzing resume and building interview context..."):
            try:
                # 2.1 Build RAG database (or just extract text for this version)
                raw_text = get_pdf_text([resume_pdf])
                # We don't need to store the DB in session_state if we only use it for initial context
                
                # 2.2 Prepare the initial system prompt message
                initial_prompt = SYSTEM_PERSONA.format(
                    resume_context=raw_text[:4000], # Send as much context as possible
                    jd_context=jd_text
                )
                
                # 2.3 Start Chat with Gemini
                model = genai.GenerativeModel('gemini-2.5-flash')
                chat = model.start_chat(history=[])
                
                # Send the initial prompt to set the interviewer persona and the first question
                response = chat.send_message(initial_prompt + "\n\n **Interviewer:** Welcome. Please introduce yourself briefly, and then I will begin with my first question.")
                
                st.session_state.chat_history = [] # Clear any old conversation
                st.session_state.chat_history.append({"role": "ai", "content": response.text})
                st.session_state.chat_session = chat
                
                st.success("Interview started! See the chat below.")
            except Exception as e:
                st.error(f"An error occurred while starting the interview: {e}")
                st.warning("The issue might be the inability to read the PDF file or incorrect API key configuration.")
    else:
        st.warning("Please upload a resume and write a job description to start the interview.")

# 3. Chat Interface and Input
st.divider()

# Display previous conversation
for message in st.session_state.chat_history:
    role_name = "🤖 Interviewer" if message["role"] == "ai" else "👤 You"
    with st.chat_message(message["role"]):
        st.markdown(f"**{role_name}:**")
        st.write(message["content"])

# 4. Process User Input
if "chat_session" in st.session_state and st.session_state.chat_session:
    # Note: To add Speech-to-Text, you would need a library like streamlit-mic-recorder here
    user_answer = st.chat_input("Type your answer here...")

    if user_answer:
        # 4.1 Display user's answer
        st.session_state.chat_history.append({"role": "user", "content": user_answer})
        with st.chat_message("user"):
            st.markdown("**👤 You:**")
            st.write(user_answer)
        
        # 4.2 Call AI response
        with st.spinner("Interviewer is writing the evaluation and the next question..."):
            
            # Since we are using "chat" (continuous context), Gemini remembers all previous questions and answers.
            # We only send the new answer.
            response = st.session_state.chat_session.send_message(user_answer)
            
            st.session_state.chat_history.append({"role": "ai", "content": response.text})
            with st.chat_message("ai"):
                st.markdown("**🤖 Interviewer:**")
                st.write(response.text)