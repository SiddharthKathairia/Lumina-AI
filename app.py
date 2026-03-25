import streamlit as st
import pymupdf as fitz
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import streamlit.components.v1 as components

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(page_title="Lumina AI Pro", page_icon="✨", layout="wide")

# ---------------- CSS ---------------- #
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

# ---------------- API ---------------- #
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- PDF ---------------- #
def extract_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# ---------------- CHUNKING ---------------- #
def chunk_text(text, chunk_size=800, overlap=150):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# ---------------- VECTOR ---------------- #
def create_vector_store(chunks):
    embeddings = embedder.encode(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index

def retrieve(query, chunks, index, k=3):
    q = embedder.encode([query])
    _, idx = index.search(np.array(q), k)
    return [chunks[i] for i in idx[0]]

# ---------------- AI FUNCTIONS ---------------- #

def generate_notes(text, mode, q_count):
    return model.generate_content(f"""
    Style: {mode}

    1. Structured notes
    2. 3 key Q&A
    3. {q_count} MCQs
    4. Answers

    TEXT:
    {text}
    """).text


def generate_graph(text):
    return model.generate_content(f"""
    Create Mermaid graph (graph TD)

    TEXT:
    {text}
    """).text


def chat(query, chunks, index):
    ctx = retrieve(query, chunks, index)
    return model.generate_content(f"""
    Answer using context only:

    {ctx}

    Question:
    {query}
    """).text


def confusion(text):
    return model.generate_content(f"""
    Find confusing points and explain simply.

    TEXT:
    {text}
    """).text


def misconceptions(text):
    return model.generate_content(f"""
    Find misconceptions and correct them.

    TEXT:
    {text}
    """).text


def exam(text):
    return model.generate_content(f"""
    Predict exam questions with probability.

    TEXT:
    {text}
    """).text


def gaps(text):
    return model.generate_content(f"""
    Find knowledge gaps and roadmap.

    TEXT:
    {text}
    """).text


def debate(text):
    return model.generate_content(f"""
    Critically analyze this.

    TEXT:
    {text}
    """).text


def persona(text, p):
    return model.generate_content(f"""
    Explain as {p}.

    TEXT:
    {text}
    """).text

# ---------------- MERMAID ---------------- #
def render_mermaid(code):
    components.html(f"""
    <div class="mermaid">{code}</div>
    <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{startOnLoad:true}});
    </script>
    """, height=500)

# ---------------- SESSION ---------------- #
keys = ["chunks","index","notes","graph","conf","misc","exam","gap","deb","pers"]
for k in keys:
    if k not in st.session_state:
        st.session_state[k] = None

# ---------------- UI ---------------- #
st.title("✨ Lumina AI Pro")
st.caption("AI Learning Intelligence Engine")

file = st.file_uploader("Upload PDF", type=["pdf"])

col1, col2 = st.columns(2)

with col1:
    mode = st.selectbox("Mode", ["Deep Dive","Exam","Simple"])

with col2:
    p = st.selectbox("Persona", ["Professor","Beginner","CEO","Researcher"])

q = st.slider("MCQs", 3, 15, 5)

# ---------------- RUN ---------------- #
if file:
    if st.button("🚀 Analyze", use_container_width=True):
        with st.spinner("Processing..."):

            text = extract_pdf(file)
            chunks = chunk_text(text)
            index = create_vector_store(chunks)

            st.session_state.chunks = chunks
            st.session_state.index = index

            preview = " ".join(chunks[:5])

            st.session_state.notes = generate_notes(preview, mode, q)
            st.session_state.graph = generate_graph(preview)
            st.session_state.conf = confusion(preview)
            st.session_state.misc = misconceptions(preview)
            st.session_state.exam = exam(preview)
            st.session_state.gap = gaps(preview)
            st.session_state.deb = debate(preview)
            st.session_state.pers = persona(preview, p)

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
        qn = st.text_input("Ask anything")
        if qn:
            st.write(chat(qn, st.session_state.chunks, st.session_state.index))

    with tabs[3]:
        st.markdown(st.session_state.conf)

    with tabs[4]:
        st.markdown(st.session_state.misc)

    with tabs[5]:
        st.markdown(st.session_state.exam)

    with tabs[6]:
        st.markdown(st.session_state.gap)

    with tabs[7]:
        st.markdown(st.session_state.deb)

    with tabs[8]:
        st.markdown(st.session_state.pers)
