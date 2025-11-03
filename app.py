import streamlit as st
import pandas as pd
import time
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
from services.mock_service import mock_chatbot_response
from services.gemini_service import get_gemini_response
from services.logging_service import log_result

# Load environment variables from .env if present
load_dotenv()

# ------------------------------
# CONFIGURATION
# ------------------------------
st.set_page_config(page_title="Chatbot Flow Validator", layout="wide")

st.title(" Chatbot Flow Validator")
st.markdown("Validate chatbot responses, log results, and generate QA reports easily.")

# ------------------------------
# SIDEBAR INPUTS
# ------------------------------
st.sidebar.header(" Test Setup")
use_mock_api = st.sidebar.checkbox("Use Mock Responses (No API key needed)", value=True)
if not use_mock_api:
    configured = False
    source = ""
    selected_model = st.sidebar.selectbox(
        "Gemini model",
        options=["Gemini 2.0 Flash", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"],
        index=0,
    )
    gemini_api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        configured = True
        source = "sidebar"
    else:
        # Fallback: Streamlit secrets, then environment variable
        secret_key = None
        try:
            secret_key = st.secrets.get("GEMINI_API_KEY")  # requires .streamlit/secrets.toml
            if secret_key:
                genai.configure(api_key=secret_key)
                configured = True
                source = "secrets"
        except Exception:
            pass
        if not configured:
            env_key = os.getenv("GEMINI_API_KEY")
            if env_key:
                genai.configure(api_key=env_key)
                configured = True
                source = "env"
    if configured:
        st.sidebar.success(f"Gemini API configured ({source}).")
    else:
        st.sidebar.warning("No API key found. Enter one or enable mock mode.")

## Services moved to services/ package

# ------------------------------
# MAIN TEST FORM
# ------------------------------
st.subheader("Run Chat Flow Test")

with st.form("chat_form"):
    prompt = st.text_area("Enter User Prompt:", height=100, placeholder="e.g., hi, how are you?")
    expected = st.text_area("Expected Chatbot Response:", height=100, placeholder="e.g., Hello! How can I assist you today?")
    submit_btn = st.form_submit_button("Run Test")

if submit_btn:
    if not prompt.strip() or not expected.strip():
        st.warning("Please fill both fields before running the test.")
    else:
        with st.spinner("Running test..."):
            time.sleep(1)
            if use_mock_api:
                actual = mock_chatbot_response(prompt)
            else:
                # selected_model is only defined when not mock; fallback just in case
                model_to_use = 'Gemini 2.0 Flash'
                try:
                    model_to_use = selected_model
                except Exception:
                    pass
                actual = get_gemini_response(prompt, model_to_use)

            status = "Pass" if expected.lower().strip() in actual.lower() else "❌ Fail"
            log_result(prompt, expected, actual, status)

            st.success(f"**Test Result:** {status}")
            st.write("**Actual Response:**")
            st.info(actual)

# ------------------------------
# QA SUMMARY SECTION
# ------------------------------
st.subheader("QA Summary")

try:
    if not os.path.exists("test_results.csv") or os.path.getsize("test_results.csv") == 0:
        raise FileNotFoundError
    data = pd.read_csv("test_results.csv", encoding="utf-8")
    st.dataframe(data.tail(10), use_container_width=True)

    total = len(data)
    passed = len(data[data["Status"] == "Pass"])
    failed = len(data[data["Status"] == "Fail"])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tests", total)
    with col2:
        st.metric("Passed", passed)
    with col3:
        st.metric("Failed", failed)

    # Optional: Add bar chart
    st.subheader("Pass/Fail Distribution")
    chart_data = pd.DataFrame({
        "Result": ["Pass", "Fail"],
        "Count": [passed, failed]
    })
    st.bar_chart(chart_data.set_index("Result"))

except (FileNotFoundError, pd.errors.EmptyDataError):
    st.info("No test results logged yet. Run a few tests first.")

# ------------------------------
# REPORT DOWNLOAD
# ------------------------------
if os.path.exists("test_results.csv"):
    with open("test_results.csv", "r", encoding="utf-8", errors="replace") as f:
        st.download_button(
            label="Download QA Report",
            data=f.read(),
            file_name="QA_Test_Report.csv",
            mime="text/csv"
        )
else:
    st.button("Download QA Report", disabled=True, help="No report available yet")


