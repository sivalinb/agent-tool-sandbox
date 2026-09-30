from pathlib import Path
import streamlit as st
from labcore.config import load_config
from labcore.observability import Recorder
from labcore.ui import header, evidence, sources_panel, ai_panel, docs_panel
from engine import PRESETS, DEFAULT_CSV, assess, run_job, security_evaluation

ROOT = Path(__file__).resolve().parent
config, meta = load_config(ROOT)
header("Agent Tool Sandbox", "One analysis job. One Linux VM. An auditable result.", meta)

@st.cache_resource
def recorder():
    return Recorder(ROOT, "agent-tool-sandbox")

tabs = st.tabs(["Run a tool", "Enforcement eval", "Evidence", "AI reviewer", "Public sources", "Guide"])
with tabs[0]:
    preset = st.selectbox("Job template", list(PRESETS))
    code = st.text_area("Python job", PRESETS[preset], height=230, key="code_" + preset)
    uploaded = st.file_uploader("CSV or JSON input", type=["csv","json","geojson"])
    use_source = st.checkbox("Use the most recently fetched public source", value=False)
    data, filename = DEFAULT_CSV, "data.csv"
    if uploaded:
        data = uploaded.getvalue()
        filename = "data.csv" if uploaded.name.endswith(".csv") else "data.json"
    if use_source and "source_result" in st.session_state:
        source = st.session_state["source_result"]
        data = Path(source["local_path"]).read_bytes()
        filename = "data.json" if source["id"] == "usgs-quakes" else "data.csv"
    a,b,c = st.columns(3)
    config["cpus"] = a.number_input("CPUs", 1, 4, config["cpus"])
    config["memoryMb"] = b.selectbox("Memory MiB", [256,512,1024,2048])
    config["timeoutSeconds"] = c.slider("Deadline seconds", 1,30,config["timeoutSeconds"])
    mode = st.radio("Execution mode", ["Static preview", "Live Apple Container"], horizontal=True)
    if st.button("Run job", type="primary"):
        try:
            with recorder().span("sandbox_job", mode=mode):
                report = assess(code, config) if mode == "Static preview" else run_job(code,data,filename,config)
                report["config_provenance"] = meta
                recorder().save(report)
                st.session_state["report"] = report
        except Exception as e:
            st.error(str(e))
    if "report" in st.session_state:
        report = st.session_state["report"]
        st.caption(report["mode"])
        if "result" in report:
            a,b,c = st.columns(3)
            a.metric("Exit code", report["result"]["returncode"])
            b.metric("Duration", f'{report["result"]["duration_s"]:.2f}s')
            c.metric("Termination", report["result"]["reason"])
            st.code(report["result"]["stdout"] or "(no standard output)")
            if report["result"]["stderr"]:
                st.code(report["result"]["stderr"])
        else:
            st.json(report)
with tabs[1]:
    st.write("Seven real checks: useful analysis, deadline, protected input, disabled network, output limit, and two independent freshness checks.")
    if st.button("Run live enforcement suite"):
        try:
            with recorder().span("enforcement_eval", mode="live"):
                report = security_evaluation(config)
                recorder().save(report,"enforcement")
                st.session_state["enforcement"] = report
        except Exception as e:
            st.error(str(e))
    if "enforcement" in st.session_state:
        report = st.session_state["enforcement"]
        st.dataframe([{k:v for k,v in c.items() if k != "report"} for c in report["cases"]],hide_index=True)
        evidence(report)
with tabs[2]:
    evidence(st.session_state.get("report"))
with tabs[3]:
    ai_panel(ROOT,st.session_state.get("report"))
with tabs[4]:
    sources_panel(ROOT)
with tabs[5]:
    docs_panel(ROOT)
