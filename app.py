import streamlit as st
import PyPDF2
import google.generativeai as genai
import re
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(page_title="Lumina AI", page_icon="✨", layout="centered")

# 2. ULTRA-PREMIUM CSS OVERRIDE
# This handles the background animation, glassmorphism, and custom typography
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

/* Glassmorphism Effect for containers */
div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 2rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

/* Custom Primary Button */
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
    box-shadow: 0 0 25px rgba(138, 43, 226, 0.6) !important;
    transform: scale(1.02) !important;
}

.lumina-title {
    font-size: 5rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(to right, #b92b27, #1565C0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0px 0px 10px rgba(138, 43, 226, 0.3));
}

.lumina-subtitle {
    text-align: center;
    color: #A0AEC0;
    font-size: 1.2rem;
    font-weight: 300;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(138, 43, 226, 0.2) !important;
    border-bottom: 2px solid #8A2BE2 !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. AI CONFIGURATION
# Pulls the key safely from Streamlit Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# Helper function to render Mermaid.js graphs
def mermaid_render(code: str):
    components.html(
        f"""
        <div class="mermaid" style="display: flex; justify-content: center; background-color: white; padding: 30px; border-radius: 15px;">
            {code}
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
        </script>
        """,
        height=550
    )

# 4. INITIALIZE APP MEMORY
if 'pdf_text' not in st.session_state:
    st.session_state['pdf_text'] = ""
if 'notes' not in st.session_state:
    st.session_state['notes'] = ""
if 'graph_code' not in st.session_state:
    st.session_state['graph_code'] = ""

# 5. HERO UI
st.markdown("<div class='lumina-title'>Lumina</div>", unsafe_allow_html=True)
st.markdown("<div class='lumina-subtitle'>Artificial Intelligence Study Engine</div><br>", unsafe_allow_html=True)

# 6. INPUT SECTION
with st.container():
    st.markdown("### 📄 1. Load Material")
    file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

with st.container():
    st.markdown("### 🎛️ 2. Strategy")
    c1, c2 = st.columns(2)
    with c1:
        mode = st.selectbox("Style", ["Academic Deep-Dive", "Explain Like I'm 5", "Exam Revision"])
    with c2:
        count = st.number_input("Questions", 1, 10, 5)

st.markdown("<br>", unsafe_allow_html=True)

# 7. CORE LOGIC
if file:
    if st.button("✨ IGNITE INTELLIGENCE", type="primary", use_container_width=True):
        with st.spinner("Processing document & mapping knowledge..."):
            
            # Extract Text
            reader = PyPDF2.PdfReader(file)
            text = "".join([p.extract_text() for p in reader.pages])
            st.session_state['pdf_text'] = text
            
            # THE BULLETPROOF PROMPT
            prompt = f"""
            You are Lumina, an elite AI teaching assistant. Style: '{mode}'.
            
            Task 1: Structured study guide (Markdown headers, bold terms, emojis).
            Task 2: Top 3 Critical Exam Q&A.
            Task 3: {count} Practice MCQs (Format: A, B, C, D on new lines).
            Task 4: Answer Key with 1-sentence logic.
            
            Task 5: Knowledge Graph. Create a Mermaid.js flowchart (graph TD).
            STRICT SYNTAX:
            - IDs must be simple letters (A, B, C).
            - ALL labels must be in double quotes: A["Concept Name"]
            - NO parentheses or brackets inside quotes.
            - Wrap code EXACTLY in ```mermaid ... ```
            
            Source Text: {text}
            """
            
            res = model.generate_content(prompt).text
            
            # Extract Graph Code
            match = re.search(r'```mermaid\n(.*?)\n```', res, re.DOTALL)
            if match:
                st.session_state['graph_code'] = match.group(1)
                st.session_state['notes'] = re.sub(r'```mermaid\n.*?\n```', '', res, flags=re.DOTALL)
            else:
                st.session_state['graph_code'] = ""
                st.session_state['notes'] = res
            
            st.rerun()

# 8. THE INTERACTIVE TABS
if st.session_state['notes']:
    st.markdown("---")
    t1, t2, t3 = st.tabs(["📝 Study Notes", "🧠 Knowledge Graph", "💬 Document Chat"])
    
    with t1:
        st.download_button("📥 Download Notes", data=st.session_state['notes'], file_name="Lumina_Notes.md", use_container_width=True)
        st.markdown(st.session_state['notes'])
        
    with t2:
        if st.session_state['graph_code']:
            mermaid_render(st.session_state['graph_code'])
        else:
            st.warning("Diagram could not be rendered for this text. Try a different section.")
            
    with t3:
        st.markdown("#### 💬 Ask anything about the PDF")
        chat_input = st.chat_input("Ask a question...")
        if chat_input:
            st.chat_message("user").write(chat_input)
            with st.spinner("Analyzing..."):
                chat_res = model.generate_content(f"Context: {st.session_state['pdf_text']}\nUser: {chat_input}")
                st.chat_message("ai").write(chat_res.text)
