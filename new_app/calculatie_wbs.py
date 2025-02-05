import streamlit as st
import pandas as pd
import io

def load_file():
    """Laad het Excel-bestand en toon de inhoud."""
    file = st.file_uploader("Upload een Excel-bestand", type=["xlsx"])
    if file:
        df = pd.read_excel(file)
        st.session_state['df'] = df
        st.dataframe(df)
        return df
    return None

def process_data(df):
    """Verwerk de data: bouw hierarchie, groeperen, sommeren, en toon resultaat."""
    
    # Selecteer kolommen voor hiërarchie
    hierarchy_columns = st.multiselect("Kies kolommen voor de hiërarchie", df.columns.tolist())
    
    # Selecteer kolommen om te groeperen
    group_columns = st.multiselect("Kies kolommen om te groeperen", df.columns.tolist())
    
    # Selecteer kolommen om te sommeren
    sum_columns = st.multiselect("Kies kolommen om te sommeren", df.columns.tolist())
    
    # Kolommen die wel in de groepering zitten maar niet in de hiërarchie
    separate_columns = st.multiselect("Kies kolommen om los weer te geven (ook gegroepeerd)", df.columns.tolist())
    
    # Controleer of er een hiërarchie en groeperen kolommen zijn geselecteerd
    if not hierarchy_columns or not group_columns:
        st.warning("Kies alstublieft minimaal één kolom voor de hiërarchie en één kolom voor de groepering.")
        return
    
    # Verwijder de geselecteerde kolommen voor summatie uit de groepering
    group_columns = [col for col in group_columns if col not in sum_columns]

    # Groeperen en sommeren
    grouped_df = df.groupby(group_columns)[sum_columns].sum().reset_index()

    # Bouw hierarchie
    hierarchical_data = []
    level_counter = {i: 1 for i in range(len(hierarchy_columns))}  # begin nummering per niveau

def build_hierarchy(data, hierarchy_columns, prefix=""):
    """Bouw een hiërarchie door te groeperen en op te tellen."""
    if not hierarchy_columns:
        return []
    
    first_column = hierarchy_columns[0]
    
    # Controleer of de kolom in de DataFrame bestaat
    if first_column not in data.columns:
        raise KeyError(f"Kolom '{first_column}' bestaat niet in de DataFrame.")
    
    grouped_data = []
    
    # Groepeer op de eerste kolom in hierarchy_columns
    for group, subgroup_data in data.groupby(first_column):
        level_counter = len(grouped_data) + 1
        # Voeg het huidige groepniveau toe aan de hierarchie
        group_data = [f"{prefix}{level_counter}"]  # Voeg de nummering toe
        
        # Voeg de waarde van de groeperende kolom toe als omschrijving
        group_data.append(f"{first_column}: {group}")
        
        # Verwerk de volgende kolom in de hiërarchie, indien aanwezig
        if len(hierarchy_columns) > 1:
            group_data.extend(build_hierarchy(subgroup_data, hierarchy_columns[1:], prefix=f"{prefix}{level_counter}."))
        else:
            # Voeg de overige kolommen toe die niet in de hiërarchie zitten
            for col in subgroup_data.columns:
                if col != first_column:  # Voeg alleen kolommen toe die niet in de hiërarchie zitten
                    group_data.append(subgroup_data[col].sum())  # Gebruik de som van de kolommen
        
        grouped_data.append(group_data)
    
    return grouped_data
    
    # Start met het bouwen van de hiërarchie
    build_hierarchy(grouped_df, hierarchy_columns)

    # Maak het resultaat in een DataFrame
    result_df = pd.DataFrame(hierarchical_data, columns=['Nummer', 'Omschrijving'] + sum_columns + separate_columns)
    st.dataframe(result_df)

    # Exporteer het resultaat naar Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        result_df.to_excel(writer, index=False)
    output.seek(0)

    # Downloadbutton voor het resultaat
    st.download_button("Download het resultaat als Excel", output, "resultaat.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def main():
    st.title("Excel Groepering en Hiërarchie Bouw")

    # Laad het bestand en toon de inhoud
    df = load_file()

    # Verwerk de data als het bestand geladen is
    if df is not None:
        process_data(df)  # Zorg ervoor dat we df doorgeven aan process_data()

if __name__ == "__main__":
    main()
