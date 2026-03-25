import streamlit as st
import PyPDF2
import google.generativeai as genai
import re
import streamlit.components.v1 as components

# 1. Page Config
st.set_page_config(page_title="Lumina AI", page_icon="✨", layout="centered")

# 2. THE EXTREME CSS OVERRIDE
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Outfit', sans-serif;
}

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

#MainMenu, footer, header {visibility: hidden !important;}

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

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 24px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
}
.stTabs [aria-selected="true"] {
    background-color: rgba(138, 43, 226, 0.2);
    border-bottom: 2px solid #8A2BE2;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Connect to AI
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# Helper function to render Mermaid graphs
def mermaid(code: str):
    components.html(
        f"""
        <div class="mermaid" style="display: flex; justify-content: center; background-color: rgba(255,255,255,0.9); padding: 20px; border-radius: 10px;">
            {code}
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        </script>
        """,
        height=500
    )

# 4. CUSTOM HERO SECTION
st.markdown("<div class='lumina-title'>Lumina</div>", unsafe_allow_html=True)
st.markdown("<div class='lumina-subtitle'>Upload. Process. Dominate your exams.</div><br><br>", unsafe_allow_html=True)

# 5. INITIALIZE MEMORY
if 'pdf_content' not in st.session_state:
    st.session_state['pdf_content'] = ""
if 'generated_notes' not in st.session_state:
    st.session_state['generated_notes'] = ""
if 'mermaid_code' not in st.session_state:
    st.session_state['mermaid_code'] = ""

# 6. UPLOAD & SETTINGS
with st.container():
    st.markdown("### 📄 1. Feed the AI")
    uploaded_file = st.file_uploader("Drop your dense lecture material here", type=["pdf"], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

with st.container():
    st.markdown("### 🎛️ 2. Tune the Engine")
    c1, c2 = st.columns(2)
    with c1:
        study_mode = st.selectbox("Intelligence Mode", ["Academic Deep-Dive", "Explain Like I'm 5", "Exam Crash Course"])
    with c2:
        quiz_count = st.number_input("Target Quiz Questions", min_value=1, max_value=10, value=5)

st.markdown("<br>", unsafe_allow_html=True)

# 7. GENERATION LOGIC
if uploaded_file:
    if st.button("✨ IGNITE NEURAL NETWORK", type="primary", use_container_width=True):
        with st.spinner("Decoding document structure and mapping knowledge graph..."):
            
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            raw_text = "".join([page.extract_text() for page in pdf_reader.pages])
            st.session_state['pdf_content'] = raw_text 
            
            # The Ultimate Prompt with the Graph Command
            prompt = f"""
            You are Lumina, an elite AI teaching assistant. Style: '{study_mode}'.
            
            Task 1: Highly structured study guide (Markdown, emojis, bullet points).
            Task 2: Top 3 Exam Q&A.
            Task 3: {quiz_count} Practice MCQs (A, B, C, D on separate lines).
            Task 4: Answer Key with explanations.
            Task 5: Knowledge Graph. Create a Mermaid.js flowchart (graph TD) connecting the core concepts of the text. Keep node text very short and concise. Wrap the code EXACTLY in a ```mermaid ... ``` block.
            
            Text: {raw_text}
            """
            
            response = model.generate_content(prompt)
            full_response = response.text
            
            # Extract the Mermaid code using Regex
            mermaid_match = re.search(r'```mermaid\n(.*?)\n```', full_response, re.DOTALL)
            if mermaid_match:
                st.session_state['mermaid_code'] = mermaid_match.group(1)
                # Remove the mermaid block from the standard notes so it doesn't look messy
                st.session_state['generated_notes'] = re.sub(r'```mermaid\n.*?\n```', '', full_response, flags=re.DOTALL)
            else:
                st.session_state['mermaid_code'] = ""
                st.session_state['generated_notes'] = full_response
                
            st.rerun()

# 8. THE APP-LIKE INTERFACE (TABS)
if st.session_state['generated_notes']:
    st.markdown("### 🎓 Knowledge Extracted")
    
    # Create Sleek Navigation Tabs
    tab1, tab2, tab3 = st.tabs(["📝 Study Guide & Quiz", "🧠 Knowledge Graph", "💬 Chat w/ PDF"])
    
    with tab1:
        with st.container():
            st.download_button("📥 Download Study Guide (.md)", data=st.session_state['generated_notes'], file_name="Lumina_Guide.md", use_container_width=True)
            st.markdown("---")
            st.markdown(st.session_state['generated_notes'])
            
    with tab2:
        with st.container():
            st.markdown("#### 🗺️ Concept Architecture")
            st.caption("Auto-generated visual map of the document's core concepts.")
            if st.session_state['mermaid_code']:
                # Render the extracted code
                mermaid(st.session_state['mermaid_code'])
            else:
                st.warning("Could not generate a clean graph for this specific document. Try a different PDF.")
                
    with tab3:
        with st.container():
            st.markdown("#### 💬 Ask Lumina")
            st.caption("Query the AI directly about this document.")
            user_question = st.chat_input("E.g., Can you explain the main idea in simpler terms?")
            if user_question:
                st.chat_message("user").write(user_question)
                with st.spinner("Analyzing memory..."):
                    chat_prompt = f"Answer based strictly on this text:\n{st.session_state['pdf_content']}\n\nUser: {user_question}"
                    chat_response = model.generate_content(chat_prompt)
                    st.chat_message("ai").write(chat_response.text)
