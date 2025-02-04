import streamlit as st
import pandas as pd
from io import BytesIO

def group_data(df, group_cols):
    grouped_df = df.groupby(group_cols, dropna=False).agg({'Effort in hours': 'sum'}).reset_index()
    return grouped_df

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Grouped Data')
    processed_data = output.getvalue()
    return processed_data

st.title("Excel Data Groeperen")

uploaded_file = st.file_uploader("Upload een Excel-bestand", type=["xls", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("**Geüploade data voorbeeld:**", df.head())
    
    group_cols = st.multiselect("Selecteer kolommen om op te groeperen", df.columns[:-1].tolist())
    
    if group_cols:
        grouped_df = group_data(df, group_cols)
        st.write("**Gegroepeerde data voorbeeld:**", grouped_df.head())
        
        excel_data = convert_df_to_excel(grouped_df)
        st.download_button(
            label="Download gegroepeerd bestand",
            data=excel_data,
            file_name="Grouped_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
