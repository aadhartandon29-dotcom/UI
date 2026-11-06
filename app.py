"""LOGIQ: a Streamlit learning studio for science and maths problems."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
MODEL_NAME = "gemini-3.8-flash"
st.set_page_config(
    page_title="LOGIQ | Learn the thinking",
    page_icon=str(APP_DIR / "assets" / "favicon.png"),
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "LOGIQ helps you work through maths, physics, and chemistry problems, one clear step at a time."},
)

SOLUTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string", "description": "One or two sentences describing the central idea."},
        "solution_steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "reasoning": {"type": "string"},
                    "equation": {"type": "string", "description": "Optional LaTeX, without dollar delimiters."},
                },
                "required": ["title", "reasoning", "equation"],
            },
        },
        "final_answer": {"type": "string", "description": "Direct result, including units where appropriate."},
        "key_concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "explanation": {"type": "string"}},
                "required": ["name", "explanation"],
            },
        },
        "related_concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "connection": {"type": "string"}},
                "required": ["name", "connection"],
            },
        },
        "check": {"type": "string", "description": "Brief verification, units check, or important assumption."},
    },
    "required": ["summary", "solution_steps", "final_answer", "key_concepts", "related_concepts", "check"],
}

SYSTEM_INSTRUCTION = """You are LOGIQ, a careful and encouraging tutor for mathematics, physics, and chemistry.
Solve the stated problem accurately. Show a concise, checkable derivation: identify the useful principle, work in
order, and include units and significant figures when relevant. For chemistry, balance equations and preserve
atoms/charge. For maths, verify results when practical. State assumptions that affect the answer. If the prompt is
ambiguous, say what is missing and only give a best-effort result when a reasonable assumption allows it. Do not
invent given values. Explain key ideas plainly and suggest genuinely connected concepts. Return only JSON matching
the supplied schema. Use LaTeX (without dollar delimiters) in equation fields."""

st.markdown(
    """
    <style>
    :root { --ink:#f4f5ef; --muted:#a3a79d; --subtle:#777d73; --lime:#c9f36b; --panel:#1b1e1a; --line:rgba(236,242,224,.09); }
    html { scroll-behavior:smooth; }
    .stApp { color:var(--ink); background:radial-gradient(ellipse at 71% 1%,rgba(201,243,107,.075),transparent 26rem),#151714; font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }
    [data-testid="stHeader"] { background:rgba(21,23,20,.72); }
    .block-container { max-width:1210px; padding-top:2rem; padding-bottom:5rem; }
    [data-testid="stSidebar"] { background:#171916; border-right:1px solid var(--line); }
    [data-testid="stSidebar"]>div:first-child { padding-top:1.5rem; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:var(--muted); }
    [data-testid="stSidebar"] hr { border-color:var(--line); margin:1.35rem 0; }
    .topline,.brand-lockup,.hero-overline,.hero-meta,.section-heading,.section-label,.answer-heading,.side-status,.footer-note { display:flex; align-items:center; }
    .topline { justify-content:space-between; border-bottom:1px solid var(--line); padding-bottom:1.05rem; }
    .brand-lockup { gap:.62rem; color:var(--ink); font-size:1rem; font-weight:750; letter-spacing:.14em; }
    .brand-lockup span:last-child,.side-brand strong { color:var(--lime); }
    .brand-mark { display:inline-block; width:31px; height:31px; overflow:hidden; border-radius:10px; box-shadow:0 0 22px rgba(201,243,107,.12); vertical-align:middle; }
    .brand-mark svg { display:block; width:100%; height:100%; }
    .topline-note { color:var(--subtle); font-size:.68rem; letter-spacing:.18em; text-transform:uppercase; }
    .hero { padding:4.4rem 0 2.5rem; animation:rise-in .65s ease both; }
    .hero-overline { gap:.55rem; margin-bottom:1.15rem; color:var(--lime); font-size:.68rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }
    .live-dot { display:inline-block; width:7px; height:7px; border-radius:50%; background:var(--lime); box-shadow:0 0 13px rgba(201,243,107,.65); animation:breathe 2.8s ease-in-out infinite; }
    .hero h1 { max-width:760px; margin:0; color:var(--ink); font-size:clamp(2.7rem,6vw,5rem); font-weight:570; letter-spacing:-.065em; line-height:.99; }
    .hero h1 em { color:var(--lime); font-style:normal; }
    .hero-copy { max-width:620px; margin:1.35rem 0 0; color:#b0b4aa; font-size:1.05rem; line-height:1.75; }
    .hero-meta { flex-wrap:wrap; gap:.55rem; margin-top:1.7rem; }
    .hero-meta span { padding:.42rem .66rem; border:1px solid var(--line); border-radius:999px; color:#b8bcb2; font-size:.61rem; font-weight:650; letter-spacing:.11em; }
    .hero-meta .meta-accent { border-color:rgba(201,243,107,.25); color:var(--lime); background:rgba(201,243,107,.055); }
    .section-heading { justify-content:space-between; gap:1rem; margin-bottom:.75rem; }
    .section-label { gap:.55rem; color:#e6e9e0; font-size:.76rem; font-weight:720; letter-spacing:.11em; text-transform:uppercase; }
    .section-label::before { content:""; width:17px; height:1px; background:var(--lime); }
    .section-hint { color:var(--subtle); font-size:.73rem; }
    .sample-caption { margin:1.25rem 0 .55rem; color:var(--subtle); font-size:.64rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }
    [data-testid="stSelectbox"] label { color:#aeb3a8 !important; font-size:.73rem !important; }
    [data-testid="stTextArea"] textarea { border:1px solid rgba(236,242,224,.12); border-radius:13px; background:#1b1e1a; color:var(--ink); line-height:1.65; transition:border-color .2s,box-shadow .2s,background .2s; }
    [data-testid="stTextArea"] textarea:focus { border-color:rgba(201,243,107,.68); background:#1d201c; box-shadow:0 0 0 3px rgba(201,243,107,.09); }
    [data-testid="stTextArea"] textarea::placeholder { color:#71776e; }
    [data-testid="stSelectbox"] [data-baseweb="select"]>div { border-color:rgba(236,242,224,.12); border-radius:10px; background:#1b1e1a; }
    div[data-testid="stButton"] button,div[data-testid="stFormSubmitButton"] button { min-height:2.8rem; border-radius:10px; font-weight:680; transition:transform .18s,box-shadow .18s,border-color .18s,background .18s; }
    div[data-testid="stButton"] button:hover,div[data-testid="stFormSubmitButton"] button:hover { transform:translateY(-1px); }
    div[data-testid="stButton"] button[kind="primary"],div[data-testid="stFormSubmitButton"] button[kind="primary"] { border:1px solid var(--lime); background:var(--lime); color:#161912; box-shadow:0 8px 28px rgba(201,243,107,.13); }
    div[data-testid="stButton"] button[kind="primary"]:hover,div[data-testid="stFormSubmitButton"] button[kind="primary"]:hover { background:#d4fa83; box-shadow:0 11px 34px rgba(201,243,107,.2); }
    div[data-testid="stButton"] button[kind="secondary"] { border:1px solid var(--line); background:rgba(255,255,255,.025); color:#dfe2d9; }
    div[data-testid="stButton"] button[kind="secondary"]:hover { border-color:rgba(201,243,107,.4); background:rgba(201,243,107,.055); }
    .prompt-footnote { padding-top:.45rem; color:#858b81; font-size:.68rem; line-height:1.5; }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line) !important; border-radius:14px !important; background:linear-gradient(145deg,rgba(31,34,29,.76),rgba(24,26,23,.86)); }
    .result-divider { height:1px; margin:3.3rem 0 2.5rem; background:linear-gradient(90deg,transparent,rgba(201,243,107,.34),var(--line) 62%,transparent); }
    .answer-heading { justify-content:space-between; align-items:end; margin-bottom:1.45rem; }
    .answer-kicker { margin:0 0 .35rem; color:var(--lime); font-size:.65rem; font-weight:740; letter-spacing:.16em; text-transform:uppercase; }
    .answer-title { margin:0; color:var(--ink); font-size:clamp(1.7rem,3vw,2.45rem); font-weight:580; letter-spacing:-.045em; }
    .answer-subject { padding:.4rem .7rem; border:1px solid rgba(201,243,107,.27); border-radius:99px; color:var(--lime); font-size:.63rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }
    .inside-label { margin:0 0 .8rem; color:var(--lime); font-size:.64rem; font-weight:730; letter-spacing:.15em; text-transform:uppercase; }
    .summary-copy { color:#d4d8cd; font-size:1rem; line-height:1.75; }
    .step-number { display:inline-flex; width:30px; height:30px; align-items:center; justify-content:center; border:1px solid rgba(201,243,107,.25); border-radius:50%; background:rgba(201,243,107,.06); color:var(--lime); font-size:.67rem; font-weight:750; }
    .step-title { margin:.08rem 0 .35rem; color:#f0f2eb; font-size:.98rem; font-weight:690; }
    .step-copy { color:#b7bcb1; font-size:.91rem; line-height:1.75; }
    .final-answer-box { padding:1rem 1.15rem; border:1px solid rgba(201,243,107,.22); border-radius:12px; background:linear-gradient(110deg,rgba(201,243,107,.09),rgba(201,243,107,.025)); }
    .final-answer-box p { margin:0; color:#f4f6ee; font-size:1.05rem; line-height:1.7; }
    .concept-title { color:var(--lime); font-size:.88rem; font-weight:720; }
    .concept-copy { margin-top:.4rem; color:#aeb3a8; font-size:.83rem; line-height:1.65; }
    .check-copy { color:#c4c9be; font-size:.88rem; line-height:1.7; }
    .welcome-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.85rem; margin-top:2.1rem; }
    .welcome-card { min-height:125px; padding:1.15rem; border:1px solid var(--line); border-radius:12px; background:rgba(29,32,27,.54); }
    .welcome-index { color:var(--lime); font-size:.65rem; font-weight:750; letter-spacing:.14em; }
    .welcome-title { margin:.6rem 0 .35rem; color:#e9ece4; font-size:.88rem; font-weight:680; }
    .welcome-copy { color:#92988e; font-size:.75rem; line-height:1.6; }
    .side-brand { display:flex; align-items:center; gap:.6rem; margin-bottom:1.7rem; color:var(--ink); font-size:.92rem; font-weight:760; letter-spacing:.14em; }
    .side-eyebrow { margin:0 0 .65rem; color:#8b9186; font-size:.62rem; font-weight:720; letter-spacing:.16em; text-transform:uppercase; }
    .side-status { gap:.45rem; margin:.45rem 0 .25rem; color:#a9afa2; font-size:.69rem; }
    .side-status .live-dot { width:6px; height:6px; }
    .footer-note { justify-content:center; gap:.4rem; margin-top:3.5rem; color:#687065; font-size:.66rem; letter-spacing:.06em; }
    .footer-note span { color:var(--lime); }
    @keyframes rise-in { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
    @keyframes breathe { 0%,100% { opacity:.68; } 50% { opacity:1; } }
    @media(max-width:720px) { .block-container{padding-top:1.3rem}.hero{padding-top:3.2rem}.topline-note{display:none}.welcome-grid{grid-template-columns:1fr}.hero-copy{font-size:.94rem}.answer-heading{align-items:start;gap:.8rem} }
    @media(prefers-reduced-motion:reduce) { *,*::before,*::after { scroll-behavior:auto !important; animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def _api_key() -> str:
    entered = st.session_state.get("gemini_api_key", "").strip()
    if entered:
        return entered
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if env_key:
        return env_key.strip()
    try:
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        return ""


def _ask_gemini(question: str, subject: str, depth: str, api_key: str) -> dict[str, Any]:
    from google import genai

    prompt = f"""Subject preference: {subject}.
Explanation depth: {depth}.

Student's problem:
{question}

Return a concise worked solution and useful concepts for this exact problem."""
    client = genai.Client(api_key=api_key)
    response = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
        system_instruction=SYSTEM_INSTRUCTION,
        response_format={"type": "text", "mime_type": "application/json", "schema": SOLUTION_SCHEMA},
        generation_config={"max_output_tokens": 3500},
        store=False,
    )
    data = json.loads(response.output_text or "{}")
    if not isinstance(data, dict):
        raise ValueError("The model returned an unexpected response format.")
    data.setdefault("summary", "")
    data.setdefault("solution_steps", [])
    data.setdefault("final_answer", "")
    data.setdefault("key_concepts", [])
    data.setdefault("related_concepts", [])
    data.setdefault("check", "")
    if not data["final_answer"] or not isinstance(data["solution_steps"], list):
        raise ValueError("The model response was incomplete. Please try again.")
    return data


def _load_example(question: str, subject: str) -> None:
    st.session_state["problem_input"] = question
    st.session_state["subject_choice"] = subject
    st.session_state["solution_record"] = None


def _load_recent(question: str, subject: str, solution: dict[str, Any]) -> None:
    st.session_state["problem_input"] = question
    st.session_state["subject_choice"] = subject
    st.session_state["solution_record"] = {"question": question, "subject": subject, "solution": solution}


def _truncate(text: str, length: int = 44) -> str:
    return text if len(text) <= length else text[: length - 1].rstrip() + "…"


def _render_solution(record: dict[str, Any]) -> None:
    solution = record["solution"]
    subject = html.escape("STEM" if record["subject"] == "Auto-detect" else record["subject"])
    st.markdown(
        f'<div class="answer-heading"><div><p class="answer-kicker">YOUR WORKED SOLUTION</p>'
        f'<h2 class="answer-title">Let’s make it clear.</h2></div><span class="answer-subject">{subject}</span></div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown('<p class="inside-label">THE CORE IDEA</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-copy">{html.escape(solution["summary"])}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:.7rem"></div>', unsafe_allow_html=True)
    st.markdown('<p class="inside-label">STEP BY STEP</p>', unsafe_allow_html=True)
    for index, step in enumerate(solution["solution_steps"], start=1):
        if not isinstance(step, dict):
            continue
        number, content = st.columns([0.075, 0.925], vertical_alignment="top")
        with number:
            st.markdown(f'<div class="step-number">{index:02d}</div>', unsafe_allow_html=True)
        with content:
            st.markdown(f'<div class="step-title">{html.escape(str(step.get("title", "Work it through")))}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="step-copy">{html.escape(str(step.get("reasoning", "")))}</div>', unsafe_allow_html=True)
            equation = str(step.get("equation", "")).strip()
            if equation:
                st.latex(equation)

    st.markdown('<div style="height:.4rem"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="inside-label">FINAL ANSWER</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="final-answer-box"><p>{html.escape(solution["final_answer"])}</p></div>', unsafe_allow_html=True)

    key_concepts = [item for item in solution.get("key_concepts", []) if isinstance(item, dict)]
    related_concepts = [item for item in solution.get("related_concepts", []) if isinstance(item, dict)]
    if key_concepts:
        st.markdown('<div style="height:1.1rem"></div>', unsafe_allow_html=True)
        st.markdown('<p class="inside-label">KEY CONCEPTS</p>', unsafe_allow_html=True)
        columns = st.columns(2, gap="medium")
        for index, concept in enumerate(key_concepts):
            with columns[index % 2]:
                with st.container(border=True):
                    st.markdown(f'<div class="concept-title">{html.escape(str(concept.get("name", "Concept")))}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="concept-copy">{html.escape(str(concept.get("explanation", "")))}</div>', unsafe_allow_html=True)
    if related_concepts:
        st.markdown('<div style="height:.65rem"></div>', unsafe_allow_html=True)
        st.markdown('<p class="inside-label">TAKE THE IDEA FURTHER</p>', unsafe_allow_html=True)
        columns = st.columns(2, gap="medium")
        for index, concept in enumerate(related_concepts):
            with columns[index % 2]:
                with st.container(border=True):
                    st.markdown(f'<div class="concept-title">↗ &nbsp;{html.escape(str(concept.get("name", "Related idea")))}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="concept-copy">{html.escape(str(concept.get("connection", "")))}</div>', unsafe_allow_html=True)
    check = str(solution.get("check", "")).strip()
    if check:
        st.markdown('<div style="height:.65rem"></div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<p class="inside-label">QUICK CHECK</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="check-copy">{html.escape(check)}</div>', unsafe_allow_html=True)
    with st.expander("See the original question"):
        st.write(record["question"])


for key, default in (("problem_input", ""), ("solution_record", None), ("recent_questions", []), ("request_error", "")):
    if key not in st.session_state:
        st.session_state[key] = default

with st.sidebar:
    st.markdown(
        '<div class="side-brand"><span class="brand-mark"><svg viewBox="0 0 64 64" role="img" aria-label="LOGIQ mark">'
        '<rect width="64" height="64" rx="18" fill="#171916"/><circle cx="29" cy="29" r="18" fill="none" stroke="#c9f36b" stroke-width="6"/>'
        '<path d="M42 42 55 55" stroke="#c9f36b" stroke-width="7" stroke-linecap="round"/><circle cx="29" cy="29" r="4" fill="#f4f5ef"/>'
        '</svg></span>LOGI<strong>Q</strong></div>', unsafe_allow_html=True,
    )
    st.markdown('<p class="side-eyebrow">YOUR STUDY SPACE</p>', unsafe_allow_html=True)
    st.markdown("Add your Gemini API key to power LOGIQ. It stays in this app session and isn’t written to files.")
    st.text_input("Gemini API key", type="password", key="gemini_api_key", placeholder="Paste your API key", help="Or set GEMINI_API_KEY in your environment or Streamlit secrets.")
    if _api_key():
        st.markdown('<div class="side-status"><span class="live-dot"></span> Gemini is ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="side-status">○ &nbsp; Add a key to start solving</div>', unsafe_allow_html=True)
    st.link_button("Get a Gemini API key ↗", "https://aistudio.google.com/app/apikey", width="stretch")
    st.divider()
    st.markdown('<p class="side-eyebrow">RECENT QUESTIONS</p>', unsafe_allow_html=True)
    if st.session_state["recent_questions"]:
        for index, item in enumerate(st.session_state["recent_questions"][:5]):
            st.button(f"↗  {_truncate(item['question'])}", key=f"recent_{index}", width="stretch", on_click=_load_recent, args=(item["question"], item["subject"], item["solution"]))
    else:
        st.caption("Your solved questions will appear here for this session.")
    st.divider()
    st.markdown('<p class="side-eyebrow">BUILT FOR</p>', unsafe_allow_html=True)
    st.markdown("Mathematics · Physics · Chemistry")
    st.caption(f"Powered by {MODEL_NAME}")

st.markdown(
    '<div class="topline"><div class="brand-lockup"><span class="brand-mark"><svg viewBox="0 0 64 64" role="img" aria-label="LOGIQ mark">'
    '<rect width="64" height="64" rx="18" fill="#171916"/><circle cx="29" cy="29" r="18" fill="none" stroke="#c9f36b" stroke-width="6"/>'
    '<path d="M42 42 55 55" stroke="#c9f36b" stroke-width="7" stroke-linecap="round"/><circle cx="29" cy="29" r="4" fill="#f4f5ef"/>'
    '</svg></span>LOGI<span>Q</span></div><div class="topline-note">A little more insight in every answer</div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<section class="hero"><div class="hero-overline"><span class="live-dot"></span> YOUR SCIENCE + MATH THINKING PARTNER</div>'
    '<h1>Big questions,<br><em>clear thinking.</em></h1>'
    '<p class="hero-copy">Bring the problem you’re stuck on. LOGIQ will work it through with you, explain the ideas behind it, and point you toward what to explore next.</p>'
    '<div class="hero-meta"><span class="meta-accent">STEP-BY-STEP SOLUTIONS</span><span>KEY CONCEPTS</span><span>RELATED IDEAS</span><span>GEMINI POWERED</span></div></section>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-heading"><div class="section-label">Let’s work through it</div><div class="section-hint">Maths, physics, or chemistry — start anywhere.</div></div>', unsafe_allow_html=True)
st.markdown('<p class="sample-caption">Need a place to start?</p>', unsafe_allow_html=True)
samples = [
    ("Try a quadratic", "Solve the quadratic equation 2x^2 - 5x - 3 = 0. Show a clear method and verify both roots.", "Mathematics"),
    ("Try a physics problem", "A 2.0 kg object starts from rest and reaches 12 m/s in 4.0 s. Find its acceleration and net force.", "Physics"),
    ("Try a chemistry problem", "Balance the equation Fe + O2 -> Fe2O3. Explain how you choose the coefficients.", "Chemistry"),
]
for col, (label, question, subject) in zip(st.columns(3, gap="small"), samples):
    with col:
        st.button(label, key=f"example_{subject}", width="stretch", on_click=_load_example, args=(question, subject))

subject_col, depth_col = st.columns([1, 1], gap="large")
with subject_col:
    st.selectbox("SUBJECT", ["Auto-detect", "Mathematics", "Physics", "Chemistry"], key="subject_choice")
with depth_col:
    st.selectbox("EXPLANATION STYLE", ["Detailed", "Balanced", "Concise"], index=0, key="explanation_depth")
st.markdown('<div class="section-heading"><div class="section-label">Your question</div><div class="section-hint">Include values, units, or working you already have.</div></div>', unsafe_allow_html=True)
with st.form("problem_form", clear_on_submit=False, border=False):
    st.text_area(
        "Problem statement", key="problem_input", label_visibility="collapsed", height=155,
        placeholder="For example: A ball is thrown vertically upward at 18 m/s. How long until it returns to the starting height? Show the steps and explain which motion equations apply.",
    )
    helper_col, submit_col = st.columns([1.15, 1], vertical_alignment="center")
    with helper_col:
        st.markdown('<div class="prompt-footnote">↳ &nbsp;One question at a time works best. Include equations or partial work.</div>', unsafe_allow_html=True)
    with submit_col:
        submitted = st.form_submit_button("✳   Solve with LOGIQ", type="primary", width="stretch")

if submitted:
    question = st.session_state["problem_input"].strip()
    st.session_state["solution_record"] = None
    if not question:
        st.session_state["request_error"] = "Add a question first and LOGIQ will work through it with you."
    elif not _api_key():
        st.session_state["request_error"] = "Add a Gemini API key in the sidebar to start solving."
    else:
        st.session_state["request_error"] = ""
        solved = False
        with st.spinner("LOGIQ is working through the steps…"):
            try:
                answer = _ask_gemini(question, st.session_state["subject_choice"], st.session_state["explanation_depth"], _api_key())
                record = {"question": question, "subject": st.session_state["subject_choice"], "solution": answer}
                st.session_state["solution_record"] = record
                history = [item for item in st.session_state["recent_questions"] if item["question"] != question]
                st.session_state["recent_questions"] = [{"question": question, "subject": record["subject"], "solution": answer}, *history][:5]
                solved = True
            except Exception as exc:
                detail = str(exc).replace(_api_key(), "[hidden]") if _api_key() else str(exc)
                st.session_state["request_error"] = "LOGIQ couldn’t finish this request. Check the key, connection, and Gemini API quota. Details: " + detail[:500]
        if solved:
            st.rerun()

if st.session_state["request_error"]:
    st.error(st.session_state["request_error"], icon="⚠️")
if st.session_state["solution_record"]:
    st.markdown('<div class="result-divider"></div>', unsafe_allow_html=True)
    _render_solution(st.session_state["solution_record"])
else:
    st.markdown(
        '<div class="welcome-grid">'
        '<div class="welcome-card"><div class="welcome-index">01 / UNDERSTAND</div><div class="welcome-title">See the method</div><div class="welcome-copy">Follow a clear derivation, one meaningful step at a time.</div></div>'
        '<div class="welcome-card"><div class="welcome-index">02 / CONNECT</div><div class="welcome-title">Learn the ideas</div><div class="welcome-copy">See which core concepts make the answer work.</div></div>'
        '<div class="welcome-card"><div class="welcome-index">03 / EXPLORE</div><div class="welcome-title">Keep going</div><div class="welcome-copy">Find related topics that build on what you just learned.</div></div></div>',
        unsafe_allow_html=True,
    )
st.markdown('<div class="footer-note">Made for curious minds <span>✳</span> LOGIQ</div>', unsafe_allow_html=True)
