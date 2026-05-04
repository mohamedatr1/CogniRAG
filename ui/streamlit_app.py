"""
CogniRAG v2 — Streamlit UI
Windows-safe, session-isolated, feature-rich RAG assistant.
"""
import os, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="CogniRAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}

/* ── App shell ── */
.stApp { background: #07070f; color: #d4d4e8; }
.block-container { padding: 1.5rem 2rem 4rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0c0c18 !important;
    border-right: 1px solid #16163a !important;
    width: 300px !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span { color: #a0a0c0 !important; }

/* ── Logo ── */
.logo-wrap { padding: 20px 0 16px; border-bottom: 1px solid #16163a; margin-bottom: 20px; }
.logo-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px; font-weight: 600;
    background: linear-gradient(120deg, #818cf8, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.logo-sub { font-size: 10px; letter-spacing: 3px; color: #3a3a5a; text-transform: uppercase; margin-top: 2px; }

/* ── Stat pills ── */
.pill-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
.pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 999px;
    font-family: 'IBM Plex Mono', monospace; font-size: 10px;
    border: 1px solid #1e1e3a; color: #5a5a8a; background: #0f0f20;
}
.pill.on  { color: #34d399; border-color: #1a3a28; }
.pill.off { color: #f87171; border-color: #3a1a1a; }
.pill.blue { color: #818cf8; border-color: #1e1e40; }
.pill-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

/* ── Section label ── */
.sec-label {
    font-size: 9px; letter-spacing: 2.5px; text-transform: uppercase;
    color: #2e2e50; font-family: 'IBM Plex Mono', monospace;
    margin: 18px 0 8px; display: flex; align-items: center; gap: 8px;
}
.sec-label::after { content:''; flex:1; height:1px; background:#16163a; }

/* ── Buttons ── */
.stButton > button {
    background: #0f0f20 !important; border: 1px solid #1e1e3a !important;
    color: #8080a8 !important; border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important; font-size: 12px !important;
    font-weight: 500 !important; padding: 6px 14px !important;
    transition: all 0.12s ease !important; width: 100%;
}
.stButton > button:hover {
    background: #16163a !important; border-color: #818cf8 !important;
    color: #c0c0e8 !important;
}
.btn-primary > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    border: none !important; color: #fff !important; font-weight: 600 !important;
}
.btn-primary > button:hover {
    background: linear-gradient(135deg, #4f52d4, #7c3aed) !important;
    box-shadow: 0 0 20px rgba(99,102,241,0.3) !important;
}
.btn-danger > button {
    background: #1a0a0a !important; border-color: #3a1a1a !important;
    color: #f87171 !important;
}
.btn-danger > button:hover {
    background: #2a1010 !important; border-color: #f87171 !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
textarea, .stChatInput textarea {
    background: #0c0c1c !important; border: 1px solid #1e1e3a !important;
    border-radius: 8px !important; color: #d0d0e8 !important;
    font-family: 'Inter', sans-serif !important; font-size: 13px !important;
}
.stTextInput > div > div > input:focus,
textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}

/* ── Radio ── */
.stRadio > div { flex-direction: row !important; gap: 16px !important; }
.stRadio label { font-size: 12px !important; color: #7070a0 !important; }

/* ── Slider ── */
.stSlider > div > div > div[data-baseweb] { background: #6366f1 !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #0c0c1c !important; border: 1px dashed #1e1e3a !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] p { font-size: 12px !important; color: #5a5a7a !important; }

/* ── Toggle / checkbox ── */
.stCheckbox label { font-size: 12px !important; color: #7070a0 !important; }
input[type="checkbox"]:checked { accent-color: #6366f1 !important; }

/* ── Main header ── */
.main-header {
    display: flex; align-items: center; justify-content: space-between;
    padding-bottom: 20px; border-bottom: 1px solid #12122a; margin-bottom: 24px;
}
.main-logo {
    font-family: 'IBM Plex Mono', monospace; font-size: 26px; font-weight: 600;
    background: linear-gradient(120deg, #818cf8, #c084fc);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.main-sub { font-size: 11px; color: #3a3a5a; letter-spacing: 2px; text-transform: uppercase; }

/* ── Empty state ── */
.empty-state {
    text-align: center; padding: 80px 20px;
    border: 1px dashed #16163a; border-radius: 16px; margin-top: 20px;
}
.empty-icon { font-size: 52px; margin-bottom: 16px; opacity: 0.4; }
.empty-title { font-size: 16px; color: #3a3a5a; font-family: 'IBM Plex Mono', monospace; }
.empty-sub { font-size: 12px; color: #222240; margin-top: 8px; }

/* ── Chat messages ── */
.chat-wrap { display: flex; flex-direction: column; gap: 16px; padding: 8px 0; }

.msg-user-wrap { display: flex; justify-content: flex-end; }
.msg-ai-wrap   { display: flex; justify-content: flex-start; }

.msg-user {
    background: #12122a; border: 1px solid #1e1e40;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px; max-width: 75%;
    font-size: 14px; line-height: 1.65; color: #c8c8e8;
}
.msg-ai {
    background: #0c0c1c; border: 1px solid #14143a;
    border-left: 2px solid #6366f1;
    border-radius: 4px 18px 18px 18px;
    padding: 14px 20px; max-width: 82%;
    font-size: 14px; line-height: 1.75; color: #c0c0dc;
}
.msg-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px; letter-spacing: 1.5px; text-transform: uppercase;
    color: #2e2e50; margin-bottom: 6px;
}

/* ── Source card ── */
.source-card {
    background: #080812; border: 1px solid #12122a; border-radius: 8px;
    padding: 10px 14px; margin: 5px 0;
    font-size: 11px; line-height: 1.6; color: #5a5a7a;
    font-family: 'IBM Plex Mono', monospace;
}
.source-score { float: right; color: #6366f1; font-size: 10px; }
.source-link { color: #818cf8; font-size: 9px; margin-top: 4px; word-break: break-all; }

/* ── Info panel ── */
.info-card {
    background: #0c0c1c; border: 1px solid #14143a; border-radius: 10px;
    padding: 16px; margin-bottom: 10px;
}
.info-label { font-size: 9px; letter-spacing: 2px; color: #2e2e50; text-transform: uppercase; margin-bottom: 10px; }
.info-big { font-family: 'IBM Plex Mono', monospace; font-size: 28px; font-weight: 600; color: #818cf8; }
.info-small { font-size: 10px; color: #3a3a5a; margin-top: 2px; }
.info-green { color: #34d399; }
.info-time { font-family: 'IBM Plex Mono', monospace; font-size: 22px; color: #34d399; font-weight: 600; }

/* ── Source list item ── */
.src-item {
    font-size: 10px; font-family: 'IBM Plex Mono', monospace;
    color: #4a4a6a; padding: 4px 0; border-bottom: 1px solid #0f0f20;
    word-break: break-all;
}
.src-item:last-child { border-bottom: none; }

/* ── Expander ── */
details summary { color: #4a4a6a !important; font-size: 11px !important; }
.streamlit-expanderHeader { background: #0c0c1c !important; }

/* ── Alerts ── */
.stSuccess { background: #081610 !important; border-color: #1a3020 !important; border-radius: 8px !important; }
.stError   { background: #160808 !important; border-color: #3a1010 !important; border-radius: 8px !important; }
.stWarning { background: #160f08 !important; border-color: #3a2a10 !important; border-radius: 8px !important; }
.stInfo    { background: #080e20 !important; border-color: #10183a !important; border-radius: 8px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1e1e3a; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #2e2e50; }

/* ── Chat input ── */
.stChatInput > div { background: #0c0c1c !important; border: 1px solid #1e1e3a !important; border-radius: 12px !important; }

/* ── Selectbox ── */
.stSelectbox > div > div { background: #0c0c1c !important; border: 1px solid #1e1e3a !important; border-radius: 8px !important; color: #a0a0c0 !important; }

/* ── Progress / spinner ── */
.stSpinner > div { border-color: #6366f1 transparent transparent transparent !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  Pipeline (cached — single instance across reruns)
# ═══════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def _get_pipeline():
    from src.rag_pipeline import RAGPipeline
    return RAGPipeline()

pipeline = _get_pipeline()


# ═══════════════════════════════════════════════════════════════════
#  Session state
# ═══════════════════════════════════════════════════════════════════
defaults = {
    "messages": [],
    "last_source": None,
    "total_queries": 0,
    "total_elapsed": 0.0,
    "use_stream": False,
    "use_mmr": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════════
def safe_reset():
    try:
        pipeline.reset()
        st.session_state.messages = []
        st.session_state.last_source = None
        st.session_state.total_queries = 0
        st.session_state.total_elapsed = 0.0
        st.rerun()
    except Exception as e:
        st.error(f"Reset failed: {e}\n\nIf locked, restart the app and try again.")


def ingest_url(url: str) -> int:
    return pipeline.add_document(url.strip(), "url")


def ingest_pdf(path: str) -> int:
    return pipeline.add_document(path, "pdf")


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    doc_count = pipeline.doc_count
    status_cls = "on" if doc_count > 0 else "off"
    status_txt = f"{doc_count:,} chunks" if doc_count > 0 else "empty"

    st.markdown(f"""
    <div class="logo-wrap">
        <div class="logo-text">⚡ CogniRAG</div>
        <div class="logo-sub">Document Intelligence v2</div>
    </div>
    <div class="pill-row">
        <span class="pill {status_cls}"><span class="pill-dot"></span>{status_txt}</span>
        <span class="pill blue">{st.session_state.total_queries} queries</span>
    </div>
    """, unsafe_allow_html=True)

    # ── ADD DOCUMENT ──────────────────────────────────────────────
    st.markdown('<div class="sec-label">Add Document</div>', unsafe_allow_html=True)
    mode = st.radio("type", ["🔗 URL", "📄 PDF"], horizontal=True, label_visibility="collapsed")

    if mode == "🔗 URL":
        url_val = st.text_input(
            "url", placeholder="https://en.wikipedia.org/wiki/...",
            label_visibility="collapsed", key="url_input"
        )
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("⬆  Ingest URL", use_container_width=True, key="btn_url"):
            if url_val and url_val.strip():
                with st.spinner("Fetching & indexing…"):
                    try:
                        n = ingest_url(url_val)
                        if n > 0:
                            st.success(f"✓ {n} chunks indexed")
                            st.session_state.last_source = url_val.strip()
                            st.rerun()
                        else:
                            st.error("Could not extract content. Try another URL.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Enter a URL first.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        pdf_file = st.file_uploader("pdf", type=["pdf"], label_visibility="collapsed", key="pdf_up")
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("⬆  Ingest PDF", use_container_width=True, key="btn_pdf"):
            if pdf_file is not None:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(pdf_file.getvalue())
                    path = tmp.name
                with st.spinner("Parsing & indexing…"):
                    try:
                        n = ingest_pdf(path)
                        os.unlink(path)
                        if n > 0:
                            st.success(f"✓ {n} chunks indexed")
                            st.session_state.last_source = pdf_file.name
                            st.rerun()
                        else:
                            st.error("Could not extract content from PDF.")
                    except Exception as e:
                        if os.path.exists(path):
                            os.unlink(path)
                        st.error(f"Error: {e}")
            else:
                st.warning("Upload a PDF first.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── RETRIEVAL SETTINGS ────────────────────────────────────────
    st.markdown('<div class="sec-label">Retrieval Settings</div>', unsafe_allow_html=True)
    top_k = st.slider("Top-K chunks", 1, 12, 4, help="Chunks retrieved per question")

    use_mmr = st.checkbox(
        "🔀 MMR — diverse results",
        value=st.session_state.use_mmr,
        help="Maximal Marginal Relevance: reduces redundancy in retrieved chunks",
    )
    if use_mmr != st.session_state.use_mmr:
        st.session_state.use_mmr = use_mmr
        pipeline.set_mmr(use_mmr)

    use_stream = st.checkbox(
        "⚡ Streaming mode",
        value=st.session_state.use_stream,
        help="Stream tokens as they're generated (visual only)",
    )
    st.session_state.use_stream = use_stream

    # ── SOURCES ───────────────────────────────────────────────────
    all_srcs = pipeline.all_sources
    if all_srcs:
        st.markdown('<div class="sec-label">Indexed Sources</div>', unsafe_allow_html=True)
        src_html = "".join(
            f'<div class="src-item">{s if len(s)<38 else "…"+s[-35:]}</div>'
            for s in all_srcs
        )
        st.markdown(f'<div style="background:#08080f;border:1px solid #12122a;border-radius:8px;padding:10px 12px;">{src_html}</div>', unsafe_allow_html=True)

    # ── SESSION CONTROLS ──────────────────────────────────────────
    st.markdown('<div class="sec-label">Session</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💬 New Chat", use_container_width=True, help="Clear conversation, keep documents"):
            st.session_state.messages = []
            st.session_state.total_queries = 0
            st.session_state.total_elapsed = 0.0
            st.rerun()
    with c2:
        st.markdown('<div class="btn-danger">', unsafe_allow_html=True)
        if st.button("🗑 Reset All", use_container_width=True, help="Wipe documents + chat"):
            safe_reset()
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  MAIN AREA
# ═══════════════════════════════════════════════════════════════════
col_chat, col_panel = st.columns([4, 1], gap="large")

with col_chat:
    # Header
    mmr_badge = ' <span style="font-size:10px;color:#8b5cf6;background:#1a1040;padding:2px 8px;border-radius:999px;border:1px solid #2e1e6a;">MMR</span>' if st.session_state.use_mmr else ""
    stream_badge = ' <span style="font-size:10px;color:#34d399;background:#081a10;padding:2px 8px;border-radius:999px;border:1px solid #1a4030;">STREAM</span>' if st.session_state.use_stream else ""
    st.markdown(f"""
    <div class="main-header">
        <div>
            <div class="main-logo">⚡ CogniRAG{mmr_badge}{stream_badge}</div>
            <div class="main-sub">Document Intelligence — ask anything</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── EMPTY STATE ───────────────────────────────────────────────
    if pipeline.doc_count == 0:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📭</div>
            <div class="empty-title">Knowledge base is empty</div>
            <div class="empty-sub">Ingest a URL or PDF from the sidebar to begin</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ── CHAT HISTORY ──────────────────────────────────────────
        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            sources = msg.get("sources", [])
            elapsed = msg.get("elapsed", None)

            if role == "user":
                st.markdown(f"""
                <div class="msg-user-wrap">
                    <div>
                        <div class="msg-meta">YOU</div>
                        <div class="msg-user">{content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                time_str = f" · {elapsed}s" if elapsed else ""
                st.markdown(f"""
                <div class="msg-ai-wrap">
                    <div>
                        <div class="msg-meta">COGNIRAG{time_str}</div>
                        <div class="msg-ai">{content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if sources:
                    with st.expander(f"📎 {len(sources)} source chunks", expanded=False):
                        for i, s in enumerate(sources, 1):
                            src_url = s["metadata"].get("source", "")
                            page = s["metadata"].get("page", "")
                            score = s.get("score", 1.0)
                            score_pct = f"{score*100:.0f}%" if score <= 1 else f"{score:.3f}"
                            pg_str = f" · p.{page}" if page != "" else ""
                            preview = s["text"][:300] + ("…" if len(s["text"]) > 300 else "")
                            st.markdown(f"""
                            <div class="source-card">
                                <span class="source-score">relevance {score_pct}</span>
                                <b style="color:#4a4a6a">#{i}</b> {preview}
                                <div class="source-link">{src_url}{pg_str}</div>
                            </div>
                            """, unsafe_allow_html=True)

        # ── CHAT INPUT ────────────────────────────────────────────
        prompt = st.chat_input("Ask a question about your documents…")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            if st.session_state.use_stream:
                # Streaming: collect tokens into placeholder
                t0 = time.time()
                placeholder = st.empty()
                answer_parts = []
                with st.spinner(""):
                    for token in pipeline.stream_ask(prompt, top_k=top_k):
                        answer_parts.append(token)
                        preview = "".join(answer_parts)
                        placeholder.markdown(f"""
                        <div class="msg-ai-wrap">
                            <div>
                                <div class="msg-meta">COGNIRAG · streaming…</div>
                                <div class="msg-ai">{preview}▌</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                elapsed = round(time.time() - t0, 2)
                answer = "".join(answer_parts)
                # Get sources separately
                scored = pipeline.vector_store.similarity_search_with_score(prompt, k=top_k)
                sources = [
                    {"text": doc.page_content[:600], "metadata": doc.metadata, "score": round(float(sc), 3)}
                    for doc, sc in scored
                ]
            else:
                with st.spinner(""):
                    t0 = time.time()
                    result = pipeline.ask(prompt, top_k=top_k)
                    elapsed = round(time.time() - t0, 2)
                answer = result["answer"]
                sources = result["sources"]

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "elapsed": elapsed,
            })
            st.session_state.total_queries += 1
            st.session_state.total_elapsed += elapsed
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  RIGHT PANEL
# ═══════════════════════════════════════════════════════════════════
with col_panel:
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Knowledge base card ───────────────────────────────────────
    doc_count = pipeline.doc_count
    if doc_count > 0:
        src_count = len(pipeline.all_sources)
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Knowledge Base</div>
            <div class="info-big">{doc_count:,}</div>
            <div class="info-small">indexed chunks</div>
            <div style="margin-top:10px; padding-top:10px; border-top:1px solid #12122a;">
                <div class="info-small">{src_count} source{"s" if src_count!=1 else ""}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Performance card ──────────────────────────────────────────
    if st.session_state.total_queries > 0:
        avg = st.session_state.total_elapsed / st.session_state.total_queries
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Performance</div>
            <div class="info-time">{avg:.1f}s</div>
            <div class="info-small">avg response time</div>
            <div style="margin-top:8px;">
                <span class="pill blue">{st.session_state.total_queries} queries</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Last response timing ──────────────────────────────────────
    if st.session_state.messages:
        last_ai = next(
            (m for m in reversed(st.session_state.messages) if m["role"] == "assistant"), None
        )
        if last_ai and last_ai.get("elapsed"):
            sources_count = len(last_ai.get("sources", []))
            st.markdown(f"""
            <div class="info-card">
                <div class="info-label">Last Response</div>
                <div class="info-time info-green">{last_ai['elapsed']}s</div>
                <div class="info-small">{sources_count} chunk{"s" if sources_count!=1 else ""} cited</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Ingest history ────────────────────────────────────────────
    history = pipeline.source_history
    if history:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">Ingest History</div>
        """, unsafe_allow_html=True)
        for h in reversed(history[-4:]):  # last 4
            name = h["source"]
            name = name if len(name) < 28 else "…" + name[-25:]
            st.markdown(f"""
            <div class="src-item">
                <span style="color:#4a4a6a">{h['type'].upper()}</span>
                {name}<br>
                <span style="color:#2e2e50">{h['chunks']} chunks · {h['elapsed']}s</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tips ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="info-card">
        <div class="info-label">Tips</div>
        <div style="font-size:10px;color:#2a2a44;line-height:1.9;font-family:'IBM Plex Mono',monospace;">
            • Mix URLs + PDFs for richer context<br>
            • Enable MMR for diverse results<br>
            • ↑ Top-K for broader answers<br>
            • New Chat keeps documents<br>
            • Reset All wipes everything
        </div>
    </div>
    """, unsafe_allow_html=True)