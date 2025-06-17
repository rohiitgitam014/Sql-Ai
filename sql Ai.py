import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai

# --- Gemini API Setup ---
genai.configure(api_key="AIzaSyBXrDRzqrivXd3f3UqGMb4A-EA6n1y_KV0")  # 🔑 Replace with your actual key
model = genai.GenerativeModel("models/gemini-1.5-pro")  # ✅ Correct model

# --- Clean Gemini's SQL output ---
def clean_sql_output(raw_sql):
    cleaned = raw_sql.strip()
    if cleaned.startswith("```sql"):
        cleaned = cleaned.replace("```sql", "").replace("```", "")
    elif cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "")
    return cleaned.strip()

# --- Generate SQL using Gemini ---
def generate_sql(prompt):
    try:
        response = model.generate_content(prompt)
        return clean_sql_output(response.text)
    except Exception as e:
        return f"-- Error from Gemini: {e}"

# --- Streamlit UI ---
st.set_page_config(page_title="SQL AI Assistant", page_icon="🧠")
st.title("🧠 SQL AI Assistant using Gemini")
st.markdown("Upload a CSV, ask a natural language question, and let Gemini write and run SQL.")

# --- Upload CSV file ---
uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Uploaded Data Preview")
    st.dataframe(df.head())

    # Load data into SQLite
    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")

    # Natural language question input
    user_question = st.text_input("💬 Ask a question about your data:")

    if user_question:
        # Prompt construction
        columns = ", ".join(df.columns)
        prompt = (
            f"You are a helpful assistant that converts natural language to SQL.\n"
            f"Table name: data\n"
            f"Columns: {columns}\n"
            f"Question: {user_question}\n"
            f"Write only the SQL query."
        )

        sql_query = generate_sql(prompt)
        st.subheader("📜 Generated SQL")
        st.code(sql_query, language="sql")

        # Attempt to run query
        try:
            result = pd.read_sql_query(sql_query, conn)
            st.success("✅ Query executed successfully!")
            st.dataframe(result)
        except Exception as e:
            st.error(f"⚠️ SQL Execution Error: {e}")
