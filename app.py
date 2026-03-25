import streamlit as st
import PyPDF2
import google.generativeai as genai
import base64

# 1. Page Config (Must be first)
st.set_page_config(page_title="Lumina AI", page_icon="✨", layout="centered")

# 2. THE BACKGROUND IMAGE & FADE (The Magic CSS)
# I have chosen a subtle, dark neural network pattern to fit the AI theme.

# ALTERNATIVE IMAGE OPTIONS (Copy the URL and paste into Line 19):
# Subtle Stars: https://www.transparenttextures.com/patterns/stardust.png
# Abstract Waves: https://i.imgur.com/8QG3F3Q.png
# Clean Geometric: https://www.transparenttextures.com/patterns/hexellence.png

bg_img_url = "https://www.transparenttextures.com/patterns/nice-snow.png" # Subtle, clean texture

# This CSS creates a "ghost layer" behind your content.
# We apply the image and the fade (opacity) ONLY to this layer.
bg_css = f"""
<style>
[data-testid="stAppViewContainer"]::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    
    # THE IMAGE
    background-image: url("{bg_img_url}");
    background-size: cover;
    background-repeat: repeat;
    
    # THE FADE (0.0 means invisible, 1.0 means full bright). 
    # 0.05 is the perfect "subtle hint" of an image.
    opacity: 0.1; 
    
    z-index: -1; /* Keeps it behind text */
}}

# Also styling the main container to have a slight glow effect
.block-container {{
    background-color: rgba(17, 25, 40, 0.75); /* Translucent dark blue */
    backdrop-filter: blur(10px); /* Blurs the background image slightly behind the text for premium look */
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 2rem;
    margin-top: 2rem;
}}

/* Hide standard Streamlit elements */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
</style>
"""
st.markdown(bg_css, unsafe_allow_html=True)

# 3. Connect to AI (REPLACE YOUR KEY!)
genai.configure(api_key=st.secrets["AIzaSyAYJA8lSjuR4reKoro0_FpTFXPV7lB0BP8"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 4. HERO SECTION (Centered and clean)
st.markdown("<h1 style='text-align: center; font-size: 4.5em; color: #8A2BE2; font-weight: 900; margin-bottom: 0;'>Lumina</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3em; color: #A0AEC0; margin-top: 0;'>Igniting Knowledge. Instantly.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# 5. UPLOAD CARDS
with st.container():
    st.markdown("### 📥 1. Load Your Material")
    uploaded_file = st.file_uploader("Drop your PDF here", type=["pdf"], label_visibility="collapsed")

# 6. SETTINGS ROW
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### ⚙️ 2. Configure Your Session")
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        study_mode = st.selectbox("🧠 Teaching Style", ["Academic", "Explain Like I'm 5", "Crash Course"], label_visibility="visible")
with c2:
    with st.container(border=True):
        quiz_count = st.number_input("🎯 Quiz Questions", min_value=1, max_value=10, value=3, label_visibility="visible")

# 7. THE MAGIC BUTTON
if uploaded_file:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 IGNITE LEARNING", type="primary", use_container_width=True):
        with st.spinner("🧠 AI Tutor is analyzing..."):

            # Read PDF
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            raw_text = "".join([page.extract_text() for page in pdf_reader.pages])

            # Master Prompt
            prompt = f"""
            You are an elite AI tutor. The user requested the '{study_mode}' style.
            
            Task 1: Study Guide
            - Create a highly structured guide using Markdown headers (##), bold text, and emojis.
            - Break down concepts. No dense paragraphs.
            
            Task 2: Top 3 Exam Q&A
            - Format strictly:
              **Q: [Question]**
              *A: [Answer]*
            
            Task 3: {quiz_count} Multiple-Choice Questions
            - Format strictly:
              **1. [Question]**
              A) [Option]
              B) [Option]
              C) [Option]
              D) [Option]
              
            Task 4: Answer Key with 1-sentence explanations.
            
            Text: {raw_text}
            """

            # Generate and Display Output
            response = model.generate_content(prompt)
            st.markdown("<br>", unsafe_allow_html=True)
            st.success("✅ Analysis Complete!")

            # Display results
            st.markdown("### 🎓 3. Your AI Study Guide")
            with st.container(border=True):
                st.markdown(response.text)
            st.balloons()