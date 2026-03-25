import streamlit as st
import pymupdf as fitz
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import streamlit.components.v1 as components

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="Lumina AI Pro", page_icon="✨", layout="wide")

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

# ---------------- CHUNK ---------------- #
def chunk_text(text, size=800, overlap=150):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+size])
        i += size - overlap
    return chunks

# ---------------- VECTOR ---------------- #
def create_vector_store(chunks):
    emb = embedder.encode(chunks)
    index = faiss.IndexFlatL2(emb.shape[1])
    index.add(np.array(emb))
    return index

def retrieve(q, chunks, index, k=3):
    e = embedder.encode([q])
    _, idx = index.search(np.array(e), k)
    return [chunks[i] for i in idx[0]]

# ---------------- AI ---------------- #
def ask_ai(prompt):
    return model.generate_content(prompt).text

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
for k in ["chunks","index","preview","notes"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ---------------- UI ---------------- #
st.title("✨ Lumina AI Pro")
st.caption("AI Learning Intelligence Engine")

file = st.file_uploader("Upload PDF", type=["pdf"])

mode = st.selectbox("Mode", ["Deep Dive","Exam","Simple"])
persona = st.selectbox("Persona", ["Professor","Beginner","CEO","Researcher"])

# ---------------- PROCESS ---------------- #
if file:
    if st.button("🚀 Analyze"):
        with st.spinner("Processing..."):

            text = extract_pdf(file)
            chunks = chunk_text(text)
            index = create_vector_store(chunks)

            st.session_state.chunks = chunks
            st.session_state.index = index
            st.session_state.preview = " ".join(chunks[:5])

            # ONLY ONE CALL HERE
            st.session_state.notes = ask_ai(f"""
            Style: {mode}
            Create structured notes.

            TEXT:
            {st.session_state.preview}
            """)

# ---------------- OUTPUT ---------------- #
if st.session_state.notes:

    tabs = st.tabs([
        "📝 Notes","🧠 Graph","💬 Chat",
        "🤯 Confusion","❌ Misconception",
        "🎯 Exam","🧠 Gap","⚔️ Debate","🎭 Persona"
    ])

    # NOTES
    with tabs[0]:
        st.markdown(st.session_state.notes)

    # GRAPH (on demand)
    with tabs[1]:
        if st.button("Generate Graph"):
            res = ask_ai(f"""
            Create Mermaid graph.

            TEXT:
            {st.session_state.preview}
            """)
            render_mermaid(res)

    # CHAT
    with tabs[2]:
        q = st.text_input("Ask")
        if q:
            ctx = retrieve(q, st.session_state.chunks, st.session_state.index)
            res = ask_ai(f"Context: {ctx}\nQ: {q}")
            st.write(res)

    # CONFUSION
    with tabs[3]:
        if st.button("Detect Confusion"):
            st.write(ask_ai(f"Find confusing parts:\n{st.session_state.preview}"))

    # MISCONCEPTION
    with tabs[4]:
        if st.button("Find Misconceptions"):
            st.write(ask_ai(f"Find misconceptions:\n{st.session_state.preview}"))

    # EXAM
    with tabs[5]:
        if st.button("Predict Exam"):
            st.write(ask_ai(f"Predict exam questions:\n{st.session_state.preview}"))

    # GAP
    with tabs[6]:
        if st.button("Analyze Gaps"):
            st.write(ask_ai(f"Find knowledge gaps:\n{st.session_state.preview}"))

    # DEBATE
    with tabs[7]:
        if st.button("Debate"):
            st.write(ask_ai(f"Critically analyze:\n{st.session_state.preview}"))

    # PERSONA
    with tabs[8]:
        if st.button("Explain"):
            st.write(ask_ai(f"Explain as {persona}:\n{st.session_state.preview}"))
