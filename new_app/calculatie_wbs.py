import streamlit as st
import pandas as pd
import io
def download_result():
    if 'processed_df' in st.session_state:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            st.session_state['processed_df'].to_excel(writer, index=False)
        st.download_button("Download resultaat", output.getvalue(), file_name="wbs_result.xlsx")


def load_file():
    file = st.file_uploader("Upload een Excel-bestand", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        st.session_state['df'] = df
        st.dataframe(df)

def process_data():
    if 'df' in st.session_state:
        df = st.session_state['df']
        group_cols = st.multiselect("Kies kolommen om te groeperen", df.columns)
        sum_cols = st.multiselect("Kies kolommen om te sommeren", df.columns)
        if group_cols and sum_cols:
            grouped_df = df.groupby(group_cols)[sum_cols].sum().reset_index()
            st.session_state['processed_df'] = grouped_df
            st.dataframe(grouped_df)

def main():
    load_file
