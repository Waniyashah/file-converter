import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="File Converter", layout="wide")
st.title("File Converter and Cleaner")
st.write("Upload CSV or Excel files, clean data and convert formats.")

files = st.file_uploader("Upload CSV or Excel files.", type=["csv", "xlsx"], accept_multiple_files=True)

if files:
    for i, file in enumerate(files):
        ext = file.name.split(".")[-1]
        if ext == "csv":
            df = pd.read_csv(file)
        else:
            try:
                df = pd.read_excel(file)
            except Exception:
                st.warning(f"There was an issue reading the Excel file {file.name}. Trying without a header.")
                df = pd.read_excel(file, header=None)  # Read without headers if there's an issue

        if df is not None and not df.empty:
            st.subheader(f"{file.name} - Preview")
            st.dataframe(df.head())

        with st.expander(f"Data Cleaning - {file.name}"):
            if st.checkbox(f"Remove Duplicates - {file.name}", key=f"dup_{i}"):
                df = df.drop_duplicates()
                st.success("Duplicates removed")
                st.dataframe(df.head())

            if st.checkbox(f"Fill Missing Values - {file.name}", key=f"fillna_{i}"):
                numeric_cols = df.select_dtypes(include=["number"])
                if not numeric_cols.empty:
                    df[numeric_cols.columns] = numeric_cols.fillna(numeric_cols.mean())
                    st.success("Missing values filled with mean")
                    st.dataframe(df.head())

        selected_columns = st.multiselect(f"Select Columns - {file.name}", df.columns, default=df.columns, key=f"cols_{i}")
        df = df[selected_columns]
        st.dataframe(df.head())

        if st.checkbox(f"Show Chart - {file.name}", key=f"chart_{i}") and not df.select_dtypes(include="number").empty:
            st.bar_chart(df.select_dtypes(include="number").iloc[:, :2])

        format_choice = st.radio(f"Convert {file.name} to: ", ["csv", "excel"], key=f"format_{i}")

        if st.button(f"Download {file.name} as {format_choice}", key=f"download_{i}"):
            output = BytesIO()
            if format_choice == "csv":
                df.to_csv(output, index=False)
                mime = "text/csv"
                new_name = file.name.rsplit(".", 1)[0] + ".csv"
            else:
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False)
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                new_name = file.name.rsplit(".", 1)[0] + ".xlsx"
            output.seek(0)
            st.download_button(label=f"Download {new_name}", data=output, mime=mime, file_name=new_name)

            st.success(f"Processing complete for {file.name}")
