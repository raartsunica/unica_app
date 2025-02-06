import streamlit as st
import pandas as pd
import numpy as np

def generate_wbs(df, hierarchy_cols, group_cols, sum_cols):
    # Vul niet-groeperende kolommen met "00"
    for col in hierarchy_cols:
        if col not in group_cols:
            df[col] = "00"
    
    # Zet kolommen correct qua type
    df[group_cols] = df[group_cols].astype(str)
    df[sum_cols] = df[sum_cols].astype(float)
    
    # Groeperen en sommeren, en hiërarchie-kolommen behouden
    agg_dict = {col: 'sum' for col in sum_cols}
    grouped_df = df.groupby(group_cols, as_index=False).agg(agg_dict)
    
    # Genereer "Omschrijving" kolom met underscore gescheiden waarden uit de hiërarchie kolommen
    grouped_df["Omschrijving"] = grouped_df[hierarchy_cols].astype(str).agg("_".join, axis=1)
    
    # Hiërarchie genereren inclusief aggregatieniveaus
    grouped_df = grouped_df.sort_values(by=group_cols)
    expanded_rows = []
    counters = {}
    
    for _, row in grouped_df.iterrows():
        level_keys = [row[col] for col in group_cols]
        wbs_number = []
        
        for i in range(len(level_keys)):
            key = tuple(level_keys[:i+1])
            if key not in counters:
                counters[key] = 1
            else:
                counters[key] += 1
            
            # Reset lagere niveaus als een hoger niveau verandert
            for sub_key in list(counters.keys()):
                if len(sub_key) > i+1 and sub_key[:i+1] == key:
                    counters[sub_key] = 1
            
            wbs_number.append(str(counters[key]))
            
            # Voeg aggregatieniveau toe als het nog niet bestaat
            if i < len(level_keys) - 1:
                parent_key = level_keys[:i+1] + ["00"] * (len(level_keys) - (i+1))
                if tuple(parent_key) not in counters:
                    parent_row = {col: parent_key[j] for j, col in enumerate(group_cols)}
                    parent_row.update({col: "00" for col in hierarchy_cols if col not in group_cols})
                    parent_row.update({col: 0 for col in sum_cols})
                    parent_row["Omschrijving"] = "_".join(parent_key)
                    parent_row["WBS"] = ".".join(wbs_number)
                    expanded_rows.append(parent_row)
        
        row_dict = row.to_dict()
        row_dict["WBS"] = ".".join(wbs_number)
        expanded_rows.append(row_dict)
    
    expanded_df = pd.DataFrame(expanded_rows)
    return expanded_df

# Streamlit app
st.title("WBS Generator")

uploaded_file = st.file_uploader("Upload een Excel-bestand", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Voorbeeld van ingelezen data:")
    st.dataframe(df.head())
    
    cols = df.columns.tolist()
    hierarchy_cols = st.multiselect("Kies hiërarchie kolommen", cols)
    group_cols = st.multiselect("Kies kolommen om te groeperen", cols)
    sum_cols = st.multiselect("Kies kolommen om te sommeren", cols)
    
    if st.button("Genereer WBS"):
        if hierarchy_cols and group_cols and sum_cols:
            result = generate_wbs(df, hierarchy_cols, group_cols, sum_cols)
            st.write("Resultaat:")
            st.dataframe(result)
            
            # Download-link voor Excel
            output_file = "wbs_result.xlsx"
            result.to_excel(output_file, index=False)
            with open(output_file, "rb") as f:
                st.download_button("Download resultaat", f, file_name=output_file)
        else:
            st.error("Selecteer alle benodigde kolommen!")
