import streamlit as st
import pandas as pd
import google.generativeai as genai

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Customer Complaint Analyzer",
    page_icon="📋",
    layout="wide"
)

st.title("📋 AI Customer Complaint Analyzer")
st.write(
    "Upload a CSV file containing customer complaints. "
    "The AI will categorize complaints, assign priority, and suggest replies."
)

# -------------------------------
# API Key Input
# -------------------------------
api_key = st.text_input(
    "Enter your Gemini API Key",
    type="password"
)

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader(
    "Upload Complaint CSV",
    type=["csv"]
)

# -------------------------------
# AI Function
# -------------------------------
def analyze_complaint(text):

    prompt = f"""
You are a customer support AI.

Analyze the complaint below.

Return ONLY in this exact format.

Category:
Priority:
Reply:

Possible Categories:
- Delivery
- Refund
- Payment
- Product Quality
- Technical Issue
- Customer Service
- Account
- Other

Priority should be:
High
Medium
Low

Complaint:
{text}
"""

    response = model.generate_content(prompt)

    result = response.text.strip().split("\n")

    category = ""
    priority = ""
    reply = ""

    for line in result:
        if line.startswith("Category:"):
            category = line.replace("Category:", "").strip()

        elif line.startswith("Priority:"):
            priority = line.replace("Priority:", "").strip()

        elif line.startswith("Reply:"):
            reply = line.replace("Reply:", "").strip()

    return category, priority, reply


# -------------------------------
# Process File
# -------------------------------
if uploaded_file is not None:

    if not api_key:
        st.warning("Please enter your Gemini API Key first.")
        st.stop()

    df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Data")
    st.dataframe(df)

    if "Complaint" not in df.columns:
        st.error("CSV must contain a column named 'Complaint'")
        st.stop()

    if st.button("Analyze Complaints"):

        categories = []
        priorities = []
        replies = []

        progress = st.progress(0)

        for i, complaint in enumerate(df["Complaint"]):

            try:
                category, priority, reply = analyze_complaint(str(complaint))

            except Exception as e:
                category = "Error"
                priority = "Error"
                reply = str(e)

            categories.append(category)
            priorities.append(priority)
            replies.append(reply)

            progress.progress((i + 1) / len(df))

        df["Category"] = categories
        df["Priority"] = priorities
        df["Suggested Reply"] = replies

        st.success("Analysis Completed!")

        st.subheader("Results")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Result CSV",
            data=csv,
            file_name="Customer_Complaint_Analysis.csv",
            mime="text/csv"
        )
