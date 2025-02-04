import streamlit as st
import pandas as pd
from io import BytesIO

try:
    import openpyxl
except ImportError:
    st.error("Het pakket 'openpyxl' ontbreekt. Installeer het met 'pip install openpyxl'.")
    st.stop()

def group_data(df, group_cols):
    grouped_df = df.groupby(group_cols, dropna=False).agg({'Effort in hours': 'sum'}).reset_index()
    return grouped_df

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Grouped Data')
    processed_data = output.getvalue()
    return processed_data

def merge_and_compare(files):
    data_frames = [pd.read_excel(file, engine='openpyxl') for file in files[:3]]
    combined_df = pd.concat(data_frames).groupby(['Activiteit', 'Resource'], as_index=False).sum()
    
    reference_df = pd.read_excel(files[3], engine='openpyxl')
    merged_df = reference_df.merge(combined_df, on=['Activiteit', 'Resource'], how='outer', suffixes=('_oud', '_nieuw'))
    
    merged_df['Wijziging'] = merged_df.apply(lambda row: 'Nieuw' if pd.isna(row['Effort in hours_oud']) else ('Gewijzigd' if row['Effort in hours_oud'] != row['Effort in hours_nieuw'] else 'Ongewijzigd'), axis=1)
    
    return merged_df[merged_df['Wijziging'] != 'Ongewijzigd']

st.title("Excel Data Groeperen en Transformeren")

uploaded_files = st.file_uploader("Upload vier Excel-bestanden", type=["xls", "xlsx"], accept_multiple_files=True)

if uploaded_files and len(uploaded_files) == 4:
    try:
        changes_df = merge_and_compare(uploaded_files)
        st.write("**Wijzigingen ter controle:**", changes_df.head())
        
        if not changes_df.empty:
            updated_excel = convert_df_to_excel(changes_df)
            st.download_button(
                label="Download bijgewerkt bestand",
                data=updated_excel,
                file_name="Updated_Data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Er is een fout opgetreden bij de verwerking van de bestanden: {e}")
