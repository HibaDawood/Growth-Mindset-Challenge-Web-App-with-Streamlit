# 📌 Imports
import streamlit as st
import pandas as pd
import os
from io import BytesIO


# 📌 Set up Streamlit App
st.set_page_config(page_title="💿 Data Sweeper", layout="wide")
st.title("💿 Data Sweeper")
st.write("Transform your files between CSV and Excel with built-in data cleaning and visualization!")


# 📌 Custom CSS for Styling
st.markdown(
    """
    <style>
    /* Background Color */
    .stApp {
        background-color: #F7CFD8;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #73C7C7;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #A6F1E0;
        color: black;
    }

    /* Header Styling */
    h1, h2, h3 {
        color: #73C7C7;
    }

    /* DataFrame Styling */
    .stDataFrame {
        background-color: #F4F8D3;
        border-radius: 10px;
        padding: 10px;
    }

    /* Success Message Styling */
    .stSuccess {
        background-color: #A6F1E0;
        color: black;
        border-radius: 10px;
        padding: 10px;
    }

    /* Error Message Styling */
    .stError {
        background-color: #F7CFD8;
        color: black;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 📌 File Upload
uploaded_files = st.file_uploader(
    "Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # 📌 Read the Uploaded File
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine="openxlsx")
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"Error reading file: {e}")
            continue

        # 📌 Display File Info
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {file.size / 1024:.2f} KB")

        # 📌 Show Preview of Data
        st.write("🔍 **Preview the Data**")
        st.dataframe(df.head())

        # 📌 Data Cleaning Options
        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if not numeric_cols.empty:
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                        st.write("✅ Missing Values Filled!")
                    else:
                        st.write("⚠️ No numeric columns found for filling missing values.")

        # 📌 Select Columns for Conversion
        st.subheader("🎯 Select Columns to Keep")
        selected_columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[selected_columns]

        # 📌 Data Visualization
        st.subheader("📊 Data Visualizations")
        if st.checkbox(f"Show Visualization for {file.name}"):
            num_cols = df.select_dtypes(include='number').columns
            if len(num_cols) >= 2:
                st.bar_chart(df[num_cols].iloc[:, :2])
            else:
                st.write("⚠️ Not enough numeric columns to create a visualization.")

        # 📌 File Conversion Options
        st.subheader("💬 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()

            try:
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"

                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False, engine="openpyxl")  # ✅ FIXED
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)  # ✅ FIXED

                # 📌 Download Button
                st.download_button(
                    label=f"⏬ Download {file.name} as {conversion_type}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
            except Exception as e:
                st.error(f"Error during file conversion: {e}")

        st.success("🎉🎊 All files processed successfully!")

