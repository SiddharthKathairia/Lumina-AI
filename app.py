import streamlit as st
import PyPDF2
import google.generativeai as genai

# 1. Page Config
st.set_page_config(page_title="Lumina AI", page_icon="✨", layout="centered")

# 2. THE EXTREME CSS OVERRIDE
# This completely rewrites Streamlit's default UI rules
custom_css = """
<style>
/* Import a modern AI-startup font */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Outfit', sans-serif;
}

/* Animated Gradient Background */
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #0f0c29, #24243e);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Hide Default Streamlit Junk */
#MainMenu, footer, header {visibility: hidden !important;}

/* Glassmorphism Cards */
div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    transition: transform 0.3s ease;
}

/* Hover effect for the cards */
div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"]:hover {
    transform: translateY(-5px);
    border: 1px solid rgba(138, 43, 226, 0.3);
}

/* Customizing the big button */
button[kind="primary"] {
    background: linear-gradient(90deg, #8A2BE2, #FF4B4B) !important;
    border: none !important;
    color: white !important;
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    border-radius: 50px !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s ease !important;
}

button[kind="primary"]:hover {
    box-shadow: 0 0 20px rgba(138, 43, 226, 0.6) !important;
    transform: scale(1.02) !important;
}

/* Glowing Title */
.lumina-title {
    font-size: 5rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(to right, #b92b27, #1565C0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
    padding-bottom: 0px;
    filter: drop-shadow(0px 0px 10px rgba(138, 43, 226, 0.3));
}

.lumina-subtitle {
    text-align: center;
    color: #A0AEC0;
    font-size: 1.2rem;
    font-weight: 300;
    margin-top: 0px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Connect to AI (REPLACE WITH YOUR st.secrets KEY!)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 4. CUSTOM HERO SECTION
st.markdown("<div class='lumina-title'>Lumina</div>", unsafe_allow_html=True)
st.markdown("<div class='lumina-subtitle'>Upload. Process. Dominate your exams.</div><br><br>", unsafe_allow_html=True)

# 5. THE GLASSMORPHIC UPLOAD CARD
with st.container():
    st.markdown("### 📄 1. Feed the AI")
    uploaded_file = st.file_uploader("Drop your dense lecture material here", type=["pdf"], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

# 6. THE GLASSMORPHIC SETTINGS CARD
with st.container():
    st.markdown("### 🎛️ 2. Tune the Engine")
    c1, c2 = st.columns(2)
    with c1:
        study_mode = st.selectbox("Intelligence Mode", ["Academic Deep-Dive", "Explain Like I'm 5", "Exam Crash Course"])
    with c2:
        quiz_count = st.number_input("Target Quiz Questions", min_value=1, max_value=10, value=5)

st.markdown("<br>", unsafe_allow_html=True)

# 7. THE ENGINE LOGIC
if uploaded_file:
    # A massive centered button
    if st.button("✨ IGNITE NEURAL NETWORK", type="primary", use_container_width=True):
        with st.spinner("Decoding document structure..."):
            
            # Read PDF
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            raw_text = "".join([page.extract_text() for page in pdf_reader.pages])
            
            # Master Prompt
            prompt = f"""
            You are Lumina, an elite AI teaching assistant. The user requested the '{study_mode}' style.
            
            Task 1: Study Guide
            - Create a highly structured guide using Markdown headers (##), bold text, and emojis.
            - Break down concepts into extremely digestible bullet points.
            
            Task 2: High-Yield Exam Q&A
            - Format strictly:
              **Q: [Question]**
              *A: [Answer]*
            
            Task 3: {quiz_count} Practice MCQs
            - Format strictly:
              **1. [Question]**
              A) [Option]
              B) [Option]
              C) [Option]
              D) [Option]
              
            Task 4: Answer Key with 1-sentence logic explanations.
            
            Text: {raw_text}
            """
            
            # Execute
            response = model.generate_content(prompt)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 8. THE RESULTS CARD
            with st.container():
                st.markdown("### 🎓 Knowledge Extracted")
                st.markdown("---")
                st.markdown(response.text)
            st.balloons()
