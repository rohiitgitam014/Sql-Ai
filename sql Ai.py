import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai

# 🔑 Gemini API Setup
genai.configure(api_key="AIzaSyBXrDRzqrivXd3f3UqGMb4A-EA6n1y_KV0")  # Replace with your Gemini API Key
model = genai.GenerativeModel("gemini-2.0-flash")

# 🎯 Gemini Prompt Function
def generate_sql(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

# 🌟 Streamlit UI
st.title("🧠 SQL AI Assistant using Gemini")

# Upload Dataset
uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Data Preview")
    st.dataframe(df.head())

    # Load data into SQLite
    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")

    # Ask a natural language question
    user_question = st.text_input("Ask your question in plain English:")

    if user_question:
        # Create prompt for Gemini
        columns = ", ".join(df.columns)
        prompt = (
            f"You are a helpful assistant that converts natural language to SQL.\n"
            f"Table Name: data\n"
            f"Columns: {columns}\n"
            f"Question: {user_question}\n"
            f"SQL Query:"
        )

        sql_query = generate_sql(prompt)

        st.code(sql_query, language="sql")

        # Execute query and show results
        try:
            result = pd.read_sql_query(sql_query, conn)
            st.success("✅ Query executed successfully")
            st.dataframe(result)
        except Exception as e:
            st.error(f"⚠️ SQL Execution Error: {e}")
