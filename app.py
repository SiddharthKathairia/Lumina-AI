import streamlit as st
import pymupdf as fitz
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
import streamlit.components.v1 as components

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Lumina AI Pro", page_icon="✨", layout="wide")

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

button[kind="primary"] {
    border-radius: 30px !important;
    font-weight: bold !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- API CONFIG ---------------- #
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- PDF PARSER ---------------- #
def extract_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    pages = []
    for i, page in enumerate(doc):
        content = page.get_text()
        pages.append((i+1, content))
        text += content
    return text, pages

# ---------------- CHUNKING ---------------- #
def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    return splitter.split_text(text)

# ---------------- VECTOR STORE ---------------- #
def create_vector_store(chunks):
    embeddings = embedder.encode(chunks)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index

# ---------------- RETRIEVAL ---------------- #
def retrieve(query, chunks, index, top_k=3):
    q_embed = embedder.encode([query])
    distances, indices = index.search(np.array(q_embed), top_k)
    return [chunks[i] for i in indices[0]]

# ---------------- AI FUNCTIONS ---------------- #

def generate_notes(text, mode, q_count):
    prompt = f"""
    You are Lumina AI.

    Style: {mode}

    1. Structured notes
    2. 3 important Q&A
    3. {q_count} MCQs
    4. Answer key

    TEXT:
    {text}
    """
    return model.generate_content(prompt).text


def generate_graph(text):
    prompt = f"""
    Create Mermaid graph (graph TD)

    RULES:
    - IDs A, B, C
    - Labels in quotes
    - No special chars

    TEXT:
    {text}
    """
    return model.generate_content(prompt).text


def chat_with_context(query, chunks, index):
    context = retrieve(query, chunks, index)
    prompt = f"""
    Answer using ONLY context.

    CONTEXT:
    {context}

    QUESTION:
    {query}
    """
    return model.generate_content(prompt).text


def detect_confusions(text):
    return model.generate_content(f"""
    Identify confusing parts and explain simply.

    TEXT:
    {text}
    """).text


def find_misconceptions(text):
    return model.generate_content(f"""
    List misconceptions and correct them.

    TEXT:
    {text}
    """).text


def predict_exam(text):
    return model.generate_content(f"""
    Predict exam questions with probability.

    TEXT:
    {text}
    """).text


def knowledge_gap(text):
    return model.generate_content(f"""
    Identify learning gaps and roadmap.

    TEXT:
    {text}
    """).text


def debate_mode(text):
    return model.generate_content(f"""
    Critically analyze and argue.

    TEXT:
    {text}
    """).text


def persona_explain(text, persona):
    return model.generate_content(f"""
    Explain as a {persona}.

    TEXT:
    {text}
    """).text

# ---------------- MERMAID RENDER ---------------- #
def render_mermaid(code):
    components.html(f"""
    <div class="mermaid">{code}</div>
    <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{startOnLoad:true}});
    </script>
    """, height=500)

# ---------------- SESSION ---------------- #
for key in [
    "chunks","index","notes","graph","confusion",
    "misconception","exam","gap","debate","persona_text"
]:
    if key not in st.session_state:
        st.session_state[key] = None

# ---------------- UI ---------------- #
st.title("✨ Lumina AI Pro")
st.caption("AI Learning Intelligence Engine")

file = st.file_uploader("Upload PDF", type=["pdf"])

col1, col2 = st.columns(2)

with col1:
    mode = st.selectbox("Mode", [
        "Academic Deep Dive",
        "Exam Revision",
        "Explain Like I'm 5"
    ])

with col2:
    persona = st.selectbox("Persona", [
        "Professor","Beginner","CEO","Researcher"
    ])

q_count = st.slider("MCQs", 3, 15, 5)

# ---------------- PROCESS ---------------- #
if file:
    if st.button("🚀 Analyze", use_container_width=True):
        with st.spinner("Processing..."):

            text, _ = extract_pdf(file)
            chunks = chunk_text(text)
            index = create_vector_store(chunks)

            st.session_state.chunks = chunks
            st.session_state.index = index

            preview = " ".join(chunks[:5])

            st.session_state.notes = generate_notes(preview, mode, q_count)
            st.session_state.graph = generate_graph(preview)
            st.session_state.confusion = detect_confusions(preview)
            st.session_state.misconception = find_misconceptions(preview)
            st.session_state.exam = predict_exam(preview)
            st.session_state.gap = knowledge_gap(preview)
            st.session_state.debate = debate_mode(preview)
            st.session_state.persona_text = persona_explain(preview, persona)

# ---------------- OUTPUT ---------------- #
if st.session_state.notes:

    tabs = st.tabs([
        "📝 Notes","🧠 Graph","💬 Chat",
        "🤯 Confusion","❌ Misconception",
        "🎯 Exam","🧠 Gap","⚔️ Debate","🎭 Persona"
    ])

    with tabs[0]:
        st.markdown(st.session_state.notes)

    with tabs[1]:
        render_mermaid(st.session_state.graph)

    with tabs[2]:
        query = st.text_input("Ask anything")

        if query:
            res = chat_with_context(
                query,
                st.session_state.chunks,
                st.session_state.index
            )
            st.write(res)

    with tabs[3]:
        st.markdown(st.session_state.confusion)

    with tabs[4]:
        st.markdown(st.session_state.misconception)

    with tabs[5]:
        st.markdown(st.session_state.exam)

    with tabs[6]:
        st.markdown(st.session_state.gap)

    with tabs[7]:
        st.markdown(st.session_state.debate)

    with tabs[8]:
        st.markdown(st.session_state.persona_text)
