# ─────────────────────────────────────────────────────────────────────────────
#  Plagio — Streamlit UI
#  CSC310 Algorithms & Data Structures · Dr. Mohamed Watfa
#
#  Run:  streamlit run streamlit_app.py
#  Place this file in the same directory as the backend .py files.
#
#  Uses backend modules from this project root.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import re
import html
import base64
from datetime import datetime

# ── page config — must be the very first Streamlit call ──────────────────────
st.set_page_config(
    page_title="Plagio platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── backend imports ───────────────────────────────────────────────────────────
from Preproccessing_documents import preprocess_document_text
from hashing import build_table_chaining, build_table_double
from Sorting import merge_sort_similarity
from Jaccard import compute_all_similarity_scores
from divide_and_conquer import compute_all_divide_conquer_scores
from Red_black_trees import RedBlackTree


# ─────────────────────────────────────────────────────────────────────────────
#  PIPELINE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def generate_html_report(jaccard_results, dac_results, doc_tables_chain):
    """Generates a standalone HTML report string."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Simple CSS for the report
    report_css = """
    <style>
        body { font-family: sans-serif; line-height: 1.6; color: #333; max-width: 1000px; margin: 0 auto; padding: 20px; }
        h1, h2 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f8f9fa; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .high { color: #d9534f; font-weight: bold; }
        .med { color: #f0ad4e; font-weight: bold; }
        .low { color: #5cb85c; font-weight: bold; }
        .footer { margin-top: 50px; font-size: 0.8em; color: #777; text-align: center; }
    </style>
    """
    
    html_content = f"<html><head><title>Plagio Report</title>{report_css}</head><body>"
    html_content += f"<h1>Plagio Similarity Report</h1>"
    html_content += f"<p>Generated on: {now}</p>"
    
    # Jaccard Table
    html_content += "<h2>Jaccard Similarity Results</h2>"
    html_content += "<table><tr><th>Rank</th><th>Doc A</th><th>Doc B</th><th>Score</th><th>Level</th></tr>"
    for i, (d1, d2, s) in enumerate(jaccard_results, 1):
        level = similarity_label(s)
        html_content += f"<tr><td>{i}</td><td>{d1}</td><td>{d2}</td><td>{s:.4f}</td><td><span class='{level.lower()}'>{level}</span></td></tr>"
    html_content += "</table>"
    
    # D&C Table
    html_content += "<h2>Divide & Conquer Positional Similarity</h2>"
    html_content += "<table><tr><th>Rank</th><th>Doc A</th><th>Doc B</th><th>Score</th><th>Level</th></tr>"
    for i, (d1, d2, s) in enumerate(dac_results, 1):
        level = similarity_label(s)
        html_content += f"<tr><td>{i}</td><td>{d1}</td><td>{d2}</td><td>{s:.4f}</td><td><span class='{level.lower()}'>{level}</span></td></tr>"
    html_content += "</table>"
    
    html_content += "<div class='footer'>CSC310 Algorithms & Data Structures · Lebanese American University</div>"
    html_content += "</body></html>"
    return html_content
def build_pipeline_data(doc_inputs):
    """
    doc_inputs : list of (doc_name: str, raw_text: str)
    Returns    : doc_tokens, doc_tables_chain, doc_tables_double
    """
    doc_tokens, doc_tables_chain, doc_tables_double = [], [], []

    for name, text in doc_inputs:
        tokens    = preprocess_document_text(text)
        ht_chain  = build_table_chaining(tokens)
        ht_double = build_table_double(tokens)
        doc_tokens.append((name, tokens))
        doc_tables_chain.append((name, ht_chain))
        doc_tables_double.append((name, ht_double))

    return doc_tokens, doc_tables_chain, doc_tables_double


def run_jaccard(doc_tables_chain):
    results = compute_all_similarity_scores(doc_tables_chain)
    merge_sort_similarity(results)
    return results


def run_divide_conquer(doc_tokens):
    results = compute_all_divide_conquer_scores(doc_tokens)
    merge_sort_similarity(results)
    return results


def build_rbt(results):
    tree = RedBlackTree()
    for doc1, doc2, score in results:
        tree.insert({"doc1": str(doc1), "doc2": str(doc2), "similarity": score})
    return tree


def similarity_label(score):
    if score > 0.8:
        return "HIGH"
    if score > 0.5:
        return "MED"
    return "LOW"


def results_to_df(results):
    rows = []
    for rank, (d1, d2, score) in enumerate(results, 1):
        rows.append({
            "Rank":       rank,
            "Document A": str(d1),
            "Document B": str(d2),
            "Score":      round(score, 4),
            "Level":      similarity_label(score),
        })
    return pd.DataFrame(rows)


def _normalize_segment_to_token(segment):
    tokens = preprocess_document_text(segment)
    if len(tokens) == 1:
        return tokens[0]
    return None


def _highlight_text_with_shared_tokens(raw_text, shared_tokens):
    parts = re.findall(r"\w+|\W+", raw_text)
    rendered = []
    for part in parts:
        token = _normalize_segment_to_token(part)
        safe_part = html.escape(part)
        if token is not None and token in shared_tokens:
            rendered.append(f'<mark class="hl-match">{safe_part}</mark>')
        else:
            rendered.append(safe_part)
    return "".join(rendered)


def render_pair_highlight_view(doc_text_by_name, results, method_label, key_prefix):
    if not doc_text_by_name or not results:
        return

    pair_labels = []
    pair_lookup = {}
    for idx, (doc1, doc2, score) in enumerate(results):
        label = f"{idx + 1}. {doc1} vs {doc2} ({score:.4f})"
        pair_labels.append(label)
        pair_lookup[label] = (doc1, doc2, score)

    selected_label = st.selectbox(
        f"{method_label} pair to preview",
        options=pair_labels,
        key=f"{key_prefix}_pair_preview",
    )
    doc1, doc2, score = pair_lookup[selected_label]
    text1 = doc_text_by_name.get(str(doc1), "")
    text2 = doc_text_by_name.get(str(doc2), "")
    tokens1 = set(preprocess_document_text(text1))
    tokens2 = set(preprocess_document_text(text2))
    shared_tokens = tokens1.intersection(tokens2)

    st.caption(
        f"Highlighted shared words for {doc1} vs {doc2} "
        f"(score: {score:.4f}, shared unique words: {len(shared_tokens)})."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{doc1}**")
        st.markdown(
            f'<div class="doc-highlight-box">{_highlight_text_with_shared_tokens(text1, shared_tokens)}</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(f"**{doc2}**")
        st.markdown(
            f'<div class="doc-highlight-box">{_highlight_text_with_shared_tokens(text2, shared_tokens)}</div>',
            unsafe_allow_html=True,
        )


def get_rbt_coords(node, x=0, y=0, layer=1, pos_list=None, edge_list=None):
    if pos_list is None: pos_list = []
    if edge_list is None: edge_list = []
    
    if node:
        pos_list.append({
            "x": x, "y": y, 
            "label": f"{node.key:.2f}", 
            "color": "#FF4B4B" if node.color else "#31333F",
            "data": f"{node.data['doc1']} vs {node.data['doc2']}"
        })
        
        # dynamic width based on layer
        width = 1.0 / (2 ** (layer - 1))
        
        if node.left:
            edge_list.append({"x0": x, "y0": y, "x1": x - width, "y1": y - 1})
            get_rbt_coords(node.left, x - width, y - 1, layer + 1, pos_list, edge_list)
        if node.right:
            edge_list.append({"x0": x, "y0": y, "x1": x + width, "y1": y - 1})
            get_rbt_coords(node.right, x + width, y - 1, layer + 1, pos_list, edge_list)
            
    return pos_list, edge_list

def draw_rbt_plotly(tree, title, font_color):
    if not tree.root:
        return None
        
    pos, edges = get_rbt_coords(tree.root)
    
    fig = go.Figure()
    
    # Draw edges
    for e in edges:
        fig.add_trace(go.Scatter(
            x=[e["x0"], e["x1"]], y=[e["y0"], e["y1"]],
            mode="lines",
            line=dict(color=font_color, width=1),
            hoverinfo="none",
            showlegend=False
        ))
        
    # Draw nodes
    fig.add_trace(go.Scatter(
        x=[p["x"] for p in pos],
        y=[p["y"] for p in pos],
        mode="markers+text",
        marker=dict(
            size=30,
            color=[p["color"] for p in pos],
            line=dict(color=font_color, width=2)
        ),
        text=[p["label"] for p in pos],
        textposition="middle center",
        textfont=dict(color="white"),
        hovertext=[f"Score: {p['label']}<br>{p['data']}" for p in pos],
        hoverinfo="text",
        showlegend=False
    ))
    
    fig.update_layout(
        title=title,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=font_color,
        height=400,
        margin=dict(t=40, b=10, l=10, r=10)
    )
    return fig

def draw_similarity_network(results, threshold, font_color):
    # nodes are unique documents
    docs = set()
    for d1, d2, s in results:
        docs.add(d1)
        docs.add(d2)
    
    doc_list = sorted(list(docs))
    n = len(doc_list)
    import math
    
    # Arrange nodes in a circle
    pos = {}
    for i, doc in enumerate(doc_list):
        angle = 2 * math.pi * i / n
        pos[doc] = (math.cos(angle), math.sin(angle))
        
    fig = go.Figure()
    
    # Draw edges for pairs above threshold
    for d1, d2, s in results:
        if s >= threshold:
            x0, y0 = pos[d1]
            x1, y1 = pos[d2]
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode="lines",
                line=dict(color="#4a90d9", width=s*10), # width proportional to similarity
                opacity=0.6,
                hoverinfo="none",
                showlegend=False
            ))
            
    # Draw nodes
    fig.add_trace(go.Scatter(
        x=[pos[d][0] for d in doc_list],
        y=[pos[d][1] for d in doc_list],
        mode="markers+text",
        marker=dict(size=20, color="#e8903a"),
        text=doc_list,
        textposition="top center",
        hoverinfo="text",
        hovertext=doc_list,
        showlegend=False
    ))
    
    fig.update_layout(
        title="Document Similarity Network",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=font_color,
        height=500,
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
#  PLOTLY CHARTS
# ─────────────────────────────────────────────────────────────────────────────
def similarity_ring(score, title, font_color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score * 100, 2),
        title={"text": title, "font": {"size": 14}},
        number={"suffix": "%", "font": {"size": 32, "color": font_color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": font_color},
            "bar":  {"color": "#4a90d9", "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  50], "color": "#1a3a22"},
                {"range": [50, 80], "color": "#3a2e00"},
                {"range": [80, 100],"color": "#3a0f0f"},
            ],
            "threshold": {
                "line": {"color": font_color, "width": 2},
                "thickness": 0.75,
                "value": score * 100,
            },
        },
    ))
    fig.update_layout(
        height=250,
        margin=dict(t=50, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=font_color,
    )
    return fig


def collision_chart(doc_tables_chain, doc_tables_double, font_color):
    doc_names   = [d for d, _ in doc_tables_chain]
    chain_cols  = [ht.collisions for _, ht in doc_tables_chain]
    double_cols = [ht.collisions for _, ht in doc_tables_double]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Chaining",
        x=doc_names, y=chain_cols,
        marker_color="#4a90d9",
        text=chain_cols, textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Double Hashing",
        x=doc_names, y=double_cols,
        marker_color="#e8903a",
        text=double_cols, textposition="outside",
    ))
    fig.update_layout(
        barmode="group",
        title="Hash Collisions per Document",
        xaxis_title="Document",
        yaxis_title="Collisions",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=font_color,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=360,
        margin=dict(t=50, b=40, l=50, r=20),
    )
    fig.update_xaxes(showgrid=False, tickangle=-30)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.15)")
    return fig


def score_distribution_chart(jaccard_results, dac_results, font_color):
    jac_scores = [s for _, _, s in jaccard_results]
    dac_scores = [s for _, _, s in dac_results]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=jac_scores, name="Jaccard",
        opacity=0.75, marker_color="#4a90d9", nbinsx=20,
    ))
    fig.add_trace(go.Histogram(
        x=dac_scores, name="D&C Positional",
        opacity=0.75, marker_color="#e8903a", nbinsx=20,
    ))
    fig.update_layout(
        barmode="overlay",
        title="Score Distribution — Jaccard vs D&C Positional",
        xaxis_title="Similarity Score",
        yaxis_title="Pair Count",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=font_color,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        height=320,
        margin=dict(t=50, b=40, l=50, r=20),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.15)")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  CSS  — injected at runtime based on dark/light toggle
# ─────────────────────────────────────────────────────────────────────────────
def inject_css(dark: bool):
    if dark:
        bg_main   = "#0d1117"
        bg_card   = "#161b22"
        border    = "#30363d"
        text      = "#e6edf3"
        accent    = "#58a6ff"
        high_bg, high_fg = "#3a0f0f", "#ff9090"
        med_bg,  med_fg  = "#3a2e00", "#ffc87a"
        low_bg,  low_fg  = "#0f2e16", "#90ee9a"
    else:
        bg_main   = "#f4f6f9"
        bg_card   = "#ffffff"
        border    = "#dde1e8"
        text      = "#1a1d23"
        accent    = "#0969da"
        high_bg, high_fg = "#ffd0d0", "#820000"
        med_bg,  med_fg  = "#fff0cc", "#6b3a00"
        low_bg,  low_fg  = "#d0f0d8", "#0a5a14"

    css = f"""
    <style>
        /* ── main background ── */
        .stApp {{ background: {bg_main}; }}

        /* ── text ── */
        body, p, span, label, div         {{ color: {text}; }}
        h1, h2, h3, h4                    {{ color: {text} !important; }}

        /* ── section headers ── */
        .section-header {{
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {accent} !important;
            border-bottom: 1px solid {border};
            padding-bottom: 6px;
            margin-bottom: 18px;
        }}

        /* ── metric cards ── */
        .metric-card {{
            background: {bg_card};
            border: 1px solid {border};
            border-radius: 10px;
            padding: 18px 12px;
            text-align: center;
            margin-bottom: 8px;
        }}
        .metric-card .card-label  {{ font-size: 0.7rem; opacity: 0.55; text-transform: uppercase; letter-spacing: 0.08em; }}
        .metric-card .card-name   {{ font-weight: 700; font-size: 0.88rem; margin: 4px 0; word-break: break-all; color: {text}; }}
        .metric-card .card-count  {{ font-size: 1.6rem; font-weight: 800; color: {accent}; }}
        .metric-card .card-unit   {{ font-size: 0.7rem; opacity: 0.5; }}

        /* ── level badges ── */
        .badge-high {{ background:{high_bg}; color:{high_fg}; padding:2px 10px; border-radius:999px; font-size:0.78rem; font-weight:600; }}
        .badge-med  {{ background:{med_bg};  color:{med_fg};  padding:2px 10px; border-radius:999px; font-size:0.78rem; font-weight:600; }}
        .badge-low  {{ background:{low_bg};  color:{low_fg};  padding:2px 10px; border-radius:999px; font-size:0.78rem; font-weight:600; }}

        /* ── generic containers ── */
        .stPlotlyChart, .stDataFrame {{ border-radius: 8px; overflow: hidden; }}

        /* ── highlighted text viewer ── */
        .doc-highlight-box {{
            background: {bg_card};
            border: 1px solid {border};
            border-radius: 10px;
            padding: 12px;
            max-height: 280px;
            overflow-y: auto;
            white-space: pre-wrap;
            line-height: 1.6;
        }}
        .hl-match {{
            background: #f6d365;
            color: #111111;
            border-radius: 4px;
            padding: 0 2px;
        }}

        /* ── hide file limit text ── */
        [data-testid="stFileUploadDropzoneInstructions"] {{
            display: none;
        }}
        small {{
            display: none !important;
        }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙ Controls")

    st.divider()
    st.markdown("### Input Parameters")
    paste_mode = st.radio(
        "Paste parsing mode",
        options=["Single document", "Multiple documents"],
        horizontal=False,
    )
    multi_separator = st.text_input("Multi-doc separator line", value="---")
    pasted_base_name = st.text_input("Pasted document base name", value="pasted_doc")
    min_words_per_doc = st.number_input("Minimum words per document", min_value=1, value=1, step=1)
    normalize_whitespace = st.toggle("Normalize pasted whitespace", value=True)

    st.divider()
    st.markdown("### Filter Results")
    
    if st.session_state.get("results_ready"):
        all_scores = [s for _, _, s in st.session_state["jaccard_results"]]
        mean_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        if st.button("Auto-Set Threshold (Mean)", help=f"Set threshold to mean score: {mean_score:.2f}"):
            st.session_state["threshold_val"] = round(mean_score, 2)
            st.rerun()
            
    threshold = st.slider(
        "Minimum similarity score",
        min_value=0.0, max_value=1.0, 
        value=st.session_state.get("threshold_val", 0.0), 
        step=0.01,
        help="Pairs below this score are hidden in result tables.",
        key="threshold_slider"
    )
    # Sync with session state for auto-set
    st.session_state["threshold_val"] = threshold

    st.divider()
    st.markdown("### RBT Range Query")
    rbt_min = st.slider("Min score", 0.0, 1.0, 0.8, 0.01)
    rbt_max = st.slider("Max score", 0.0, 1.0, 1.0, 0.01)
    if rbt_min > rbt_max:
        st.warning("Min must be ≤ Max.")

    st.divider()
    st.caption("CSC310 · Lebanese American University\n")


# Follow Streamlit's built-in theme (Settings -> Theme)
theme_base = (st.get_option("theme.base") or "dark").lower()
is_dark_theme = theme_base == "dark"
inject_css(is_dark_theme)
FONT_COLOR = "white" if is_dark_theme else "#1a1d23"


# ─────────────────────────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("# 🔍 Plagio")
st.markdown("**Document Similarity & Plagiarism Detection** — CSC310 Algorithms & Data Structures")

st.markdown("---")


# ─────────────────────────────────────────────────────────────────────────────
#  INPUT SECTION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Document Input</div>', unsafe_allow_html=True)

col_upload, col_paste = st.columns([1, 1], gap="large")

with col_upload:
    st.markdown("**Upload .txt files**")
    uploaded_files = st.file_uploader(
        "Drop files",
        type=["txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

with col_paste:
    st.markdown("**Paste text**")
    paste_text = st.text_area("Text here", height=140, label_visibility="collapsed",
                               placeholder="Paste one document, or many documents separated by a full separator line.")
    st.caption(
        f"Mode: {paste_mode} · Separator: `{multi_separator or '---'}` · Min words: {int(min_words_per_doc)}"
    )
    if paste_text.strip():
        st.caption(
            f"Pasted text: {len(paste_text)} chars, {len(paste_text.split())} words"
        )


# ── assemble doc_inputs list ─────────────────────────────────────────────────
doc_inputs = []
input_warnings = []


def _decode_uploaded_txt(file_obj):
    """
    Decode uploaded text bytes with simple fallback encodings.
    Returns decoded text (or empty string if all attempts fail).
    """
    raw_bytes = file_obj.read()
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return raw_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    return ""


def _unique_name(name, used):
    candidate = name or "document"
    if candidate not in used:
        used.add(candidate)
        return candidate
    idx = 2
    while f"{candidate}_{idx}" in used:
        idx += 1
    final = f"{candidate}_{idx}"
    used.add(final)
    return final


def _split_pasted_documents(raw_text, separator):
    """
    Split pasted text into one or more document bodies.
    A line containing only the separator acts as a split marker.
    """
    safe_sep = re.escape(separator.strip() or "---")
    parts = re.split(rf"\n\s*{safe_sep}\s*\n", raw_text.strip())
    cleaned = []
    for part in parts:
        text = part.strip()
        if text:
            cleaned.append(text)
    return cleaned


used_names = set()

for f in (uploaded_files or []):
    raw = _decode_uploaded_txt(f)
    if not raw.strip():
        input_warnings.append(f"Skipped empty or unreadable file: {f.name}")
        continue
    safe_name = _unique_name(f.name.strip(), used_names)
    doc_inputs.append((safe_name, raw))

if paste_text.strip():
    base_name = pasted_base_name.strip() or "pasted_doc"
    pasted_raw = paste_text.strip()

    if paste_mode == "Single document":
        pasted_docs = [pasted_raw]
    else:
        pasted_docs = _split_pasted_documents(pasted_raw, multi_separator)

    if not pasted_docs:
        input_warnings.append("Pasted text is empty after cleanup.")
    else:
        for idx, text in enumerate(pasted_docs, 1):
            if normalize_whitespace:
                text = re.sub(r"\s+", " ", text).strip()
            word_count = len(text.split())
            if word_count < int(min_words_per_doc):
                input_warnings.append(
                    f"Skipped pasted section {idx}: {word_count} words (minimum is {int(min_words_per_doc)})."
                )
                continue
            name_seed = base_name if len(pasted_docs) == 1 else f"{base_name}_{idx}"
            safe_name = _unique_name(name_seed, used_names)
            doc_inputs.append((safe_name, text))

if input_warnings:
    for msg in input_warnings:
        st.warning(msg, icon="⚠")


# ── track card-level removals (x buttons) ───────────────────────────────────
if "removed_docs" not in st.session_state:
    st.session_state["removed_docs"] = []

current_names = []
idx = 0
while idx < len(doc_inputs):
    current_names.append(doc_inputs[idx][0])
    idx += 1

st.session_state["removed_docs"] = [
    n for n in st.session_state["removed_docs"] if n in current_names
]

if st.session_state["removed_docs"]:
    doc_inputs = [
        (name, text)
        for name, text in doc_inputs
        if name not in st.session_state["removed_docs"]
    ]
    st.caption(
        f"Excluded {len(st.session_state['removed_docs'])} document(s). "
        "Use reset to bring them back."
    )
    if st.button("Reset removed documents", key="reset_removed_docs"):
        st.session_state["removed_docs"] = []
        st.rerun()


# ── document summary cards ───────────────────────────────────────────────────
if doc_inputs:
    st.markdown(f"**{len(doc_inputs)} document(s) ready**")
    cols = st.columns(min(len(doc_inputs), 6))
    for i, (name, text) in enumerate(doc_inputs):
        word_count = len(text.split())
        with cols[i % 6]:
            card_col, remove_col = st.columns([6, 1], gap="small")
            with card_col:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="card-label">Doc {i + 1}</div>'
                    f'<div class="card-name">{name[:22]}</div>'
                    f'<div class="card-count">{word_count}</div>'
                    f'<div class="card-unit">words</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with remove_col:
                if st.button("✕", key=f"remove_doc_{name}", help=f"Remove {name}"):
                    if name not in st.session_state["removed_docs"]:
                        st.session_state["removed_docs"].append(name)
                    st.rerun()
    st.markdown("")


# ─────────────────────────────────────────────────────────────────────────────
#  RUN BUTTON
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
btn_col, hint_col = st.columns([1, 5])
with btn_col:
    run = st.button(
        "▶ Run Analysis",
        type="primary",
        disabled=len(doc_inputs) < 2,
        width="stretch",
    )
with hint_col:
    if len(doc_inputs) < 2:
        st.info("Need at least 2 documents to compare.", icon="ℹ")
    elif len(doc_inputs) >= 2:
        n_pairs = len(doc_inputs) * (len(doc_inputs) - 1) // 2
        st.caption(f"{len(doc_inputs)} documents → {n_pairs} pair(s) to compare")


# ─────────────────────────────────────────────────────────────────────────────
#  PIPELINE + RESULTS
# ─────────────────────────────────────────────────────────────────────────────
if run:
    # run pipeline and cache results in session state
    with st.spinner("Preprocessing and building hash tables…"):
        doc_tokens, doc_tables_chain, doc_tables_double = build_pipeline_data(doc_inputs)

    with st.spinner("Computing Jaccard similarity…"):
        jaccard_results = run_jaccard(doc_tables_chain)

    with st.spinner("Computing divide-and-conquer positional similarity…"):
        dac_results = run_divide_conquer(doc_tokens)

    st.session_state.update({
        "results_ready":     True,
        "jaccard_results":   jaccard_results,
        "dac_results":       dac_results,
        "doc_tables_chain":  doc_tables_chain,
        "doc_tables_double": doc_tables_double,
        "doc_text_by_name":  {name: text for name, text in doc_inputs},
    })
    st.balloons()

if st.session_state.get("results_ready"):
    jaccard_results   = st.session_state["jaccard_results"]
    dac_results       = st.session_state["dac_results"]
    doc_tables_chain  = st.session_state["doc_tables_chain"]
    doc_tables_double = st.session_state["doc_tables_double"]
    doc_text_by_name  = st.session_state.get("doc_text_by_name", {})

    # ── TOP SIMILARITY RINGS ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Top Similarity — Both Methods</div>',
                unsafe_allow_html=True)

    ring_c1, ring_c2 = st.columns(2)
    with ring_c1:
        if jaccard_results:
            d1, d2, s = jaccard_results[0]
            fig = similarity_ring(s, f"Jaccard\n{d1} vs {d2}", FONT_COLOR)
            st.plotly_chart(fig, width="stretch")
    with ring_c2:
        if dac_results:
            d1, d2, s = dac_results[0]
            fig = similarity_ring(s, f"D&C Positional\n{d1} vs {d2}", FONT_COLOR)
            st.plotly_chart(fig, width="stretch")

    # ── METHOD COMPARISON TABS ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Similarity Results — Method Comparison</div>',
                unsafe_allow_html=True)

    tab_jac, tab_dac, tab_dist = st.tabs([
        "📐 Jaccard (Set-Based)",
        "⚡ Divide & Conquer (Positional)",
        "📊 Score Distribution",
    ])

    def render_results_tab(results, method_label, key_prefix):
        if not results:
            st.warning("No results to show.")
            return

        is_desc_sorted = True
        i = 1
        while i < len(results):
            if results[i - 1][2] < results[i][2]:
                is_desc_sorted = False
                break
            i += 1

        if is_desc_sorted:
            st.caption(f"{method_label}: pairs are sorted by similarity score (highest to lowest).")
        else:
            st.warning(f"{method_label}: pairs are not fully sorted from highest to lowest.")

        filtered = [(d1, d2, s) for d1, d2, s in results if s >= threshold]

        if not filtered:
            st.info(f"No pairs at or above the current threshold ({threshold:.2f}).")
            return

        df = results_to_df(filtered)

        # colour Level column
        def _style_level(val):
            mapping = {
                "HIGH": "background-color:#3a0f0f;color:#ff9090",
                "MED":  "background-color:#3a2e00;color:#ffc87a",
                "LOW":  "background-color:#0f2e16;color:#90ee9a",
            }
            return mapping.get(val, "")

        try:
            styled = df.style.map(_style_level, subset=["Level"])   # pandas >= 2.1
        except AttributeError:
            styled = df.style.applymap(_style_level, subset=["Level"])  # older pandas

        st.dataframe(styled, width="stretch", hide_index=True)

        top = filtered[0]
        lev = similarity_label(top[2])
        badge = f'<span class="badge-{lev.lower()}">{lev}</span>'
        st.markdown(
            f"**{method_label} — Highest pair:** {top[0]} vs {top[1]} "
            f"→ `{top[2]:.4f}` {badge}",
            unsafe_allow_html=True,
        )

        st.markdown("**Text highlights**")
        render_pair_highlight_view(doc_text_by_name, filtered, method_label, key_prefix)

    with tab_jac:
        st.caption(
            "Jaccard treats each document as a **set of unique words**. "
            "Score = |A∩B| / |A∪B|. "
            "Ignores word frequency and order."
        )
        render_results_tab(jaccard_results, "Jaccard", "jac")

    with tab_dac:
        st.caption(
            "D&C Positional aligns token lists **by index** and recursively counts "
            "exact position matches. Sensitive to word order and length differences. "
            "Scores are typically lower than Jaccard for documents with same words "
            "in different order."
        )
        render_results_tab(dac_results, "D&C Positional", "dac")

    with tab_dist:
        fig = score_distribution_chart(jaccard_results, dac_results, FONT_COLOR)
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "When Jaccard is high but D&C is low, documents share **vocabulary** "
            "but not **word order** — a sign of paraphrased or reorganised content "
            "rather than direct copy-paste."
        )

    # ── HASH COLLISION VISUALIZATION ─────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Hash Table Analysis</div>',
                unsafe_allow_html=True)

    fig = collision_chart(doc_tables_chain, doc_tables_double, FONT_COLOR)
    st.plotly_chart(fig, width="stretch")

    # stats table
    stats_rows = []
    for (name, ht_c), (_, ht_d) in zip(doc_tables_chain, doc_tables_double):
        if ht_c.collisions < ht_d.collisions:
            winner = "Chaining"
        elif ht_d.collisions < ht_c.collisions:
            winner = "Double Hashing"
        else:
            winner = "Tie"
        stats_rows.append({
            "Document":           name,
            "Chain — Size":       ht_c.size,
            "Chain — Entries":    ht_c.count,
            "Chain — Collisions": ht_c.collisions,
            "Double — Size":      ht_d.size,
            "Double — Entries":   ht_d.count,
            "Double — Collisions":ht_d.collisions,
            "Fewer Collisions":   winner,
        })
    st.dataframe(pd.DataFrame(stats_rows), width="stretch", hide_index=True)

    # ── RED-BLACK TREE SECTION ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Red-Black Tree Insights</div>',
                unsafe_allow_html=True)
    st.caption(
        f"In-order traversal visits pairs in **ascending** score order. "
        f"Range query returns all pairs with score in [{rbt_min:.2f}, {rbt_max:.2f}]."
    )

    def show_rbt_pair(method_label, results):
        tree     = build_rbt(results)
        inorder  = tree.inorder_list()
        ranged   = tree.range_query_list(rbt_min, rbt_max)

        st.markdown(f"**{method_label} — Structure Visualization**")
        fig = draw_rbt_plotly(tree, f"{method_label} RBT Structure", FONT_COLOR)
        if fig:
            st.plotly_chart(fig, width="stretch")

        c_inorder, c_range = st.columns(2)
        with c_inorder:
            st.markdown(f"**{method_label} — In-order (ascending)**")
            if inorder:
                df = pd.DataFrame(inorder)
                df["similarity"] = df["similarity"].round(4)
                st.dataframe(df, width="stretch", hide_index=True)
            else:
                st.info("No entries in tree.")

        with c_range:
            st.markdown(f"**{method_label} — Range [{rbt_min:.2f}, {rbt_max:.2f}]**")
            if ranged:
                df = pd.DataFrame(ranged)
                df["similarity"] = df["similarity"].round(4)
                st.dataframe(df, width="stretch", hide_index=True)
            else:
                st.info(f"No pairs in range [{rbt_min:.2f}, {rbt_max:.2f}].")

    show_rbt_pair("Jaccard", jaccard_results)

    with st.expander("D&C Positional RBT"):
        show_rbt_pair("D&C Positional", dac_results)

    # ── SIMILARITY NETWORK ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Similarity Network Visualization</div>',
                unsafe_allow_html=True)
    st.caption("Connections show pairs above the current threshold. Line thickness = similarity strength.")
    
    net_fig = draw_similarity_network(jaccard_results, threshold, FONT_COLOR)
    st.plotly_chart(net_fig, width="stretch")

    # ── DOWNLOAD REPORT ─────────────────────────────────────────────────────
    st.markdown("---")
    report_html = generate_html_report(jaccard_results, dac_results, doc_tables_chain)
    
    st.download_button(
        label="📥 Download Full HTML Report",
        data=report_html,
        file_name=f"Plagio_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
        mime="text/html",
        type="primary"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "CSC310 Algorithms & Data Structures · Lebanese American University · "
    "Dr. Mohamed Watfa · Spring 2026"
)