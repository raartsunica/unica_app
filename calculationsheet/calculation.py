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
    for col in hierarchy_cols:
        agg_dict[col] = 'first'
    
    grouped_df = df.groupby(group_cols, as_index=False).agg(agg_dict)
    
    # Genereer "Omschrijving" kolom met underscore gescheiden waarden uit de hiërarchie kolommen
    grouped_df["Omschrijving"] = grouped_df[hierarchy_cols].astype(str).agg("_".join, axis=1)
    
    # Hiërarchie genereren inclusief aggregatieniveaus
    grouped_df = grouped_df.sort_values(by=group_cols)
    hierarchy_numbers = []
    expanded_rows = []
    counters = {}
    
    for _, row in grouped_df.iterrows():
        level_keys = [row[col] for col in group_cols]
        
        for i in range(len(level_keys)):
            key = tuple(level_keys[:i+1])
            if key not in counters:
                counters[key] = 1
            else:
                counters[key] += 1
            
            # Reset lagere niveaus
            lower_keys = list(counters.keys())
            for lk in lower_keys:
                if len(lk) > i+1 and lk[:i+1] == key:
                    counters[lk] = 1
        
        # Genereer hiërarchisch nummer
        number = ".".join(str(counters[tuple(level_keys[:i+1])]) for i in range(len(level_keys)))
        hierarchy_numbers.append(number)
        
        # Voeg aggregatieniveaus toe
        for i in range(len(level_keys)):
            parent_key = level_keys[:i+1] + ["00"] * (len(level_keys) - (i+1))
            parent_row = {col: parent_key[j] for j, col in enumerate(group_cols)}
            parent_row.update({col: "00" for col in hierarchy_cols if col not in group_cols})
            parent_row.update({col: 0 for col in sum_cols})
            parent_row["Omschrijving"] = "_".join(parent_key)
            parent_row["WBS"] = ".".join(str(counters[tuple(parent_key[:j+1])]) for j in range(i+1))
            expanded_rows.append(parent_row)
        
        expanded_rows.append(row.to_dict())
    
    expanded_df = pd.DataFrame(expanded_rows)
    expanded_df.insert(0, "WBS", hierarchy_numbers + [row["WBS"] for row in expanded_rows if "WBS" in row])
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
