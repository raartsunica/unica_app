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
        
        # Dynamisch de kolommen voor groeperen en sommeren kiezen
        group_cols = st.multiselect("Kies kolommen om te groeperen", df.columns)
        sum_cols = st.multiselect("Kies kolommen om te sommeren", df.columns)
        exclude_group_cols = st.multiselect("Kies kolommen die wel in de groepering meegenomen moeten worden, maar niet in de hiërarchie", df.columns)
        
        # Zorg ervoor dat kolommen voor groepering en summatie correct geselecteerd zijn
        if group_cols and sum_cols:
            # Bepaal de kolommen die in de hiërarchie komen
            hierarchy_cols = [col for col in df.columns if col not in group_cols and col not in sum_cols and col not in exclude_group_cols]
            
            # Groeperen en sommeren van de gegevens
            grouped_df = df.groupby(group_cols)[sum_cols].sum().reset_index()
            
            # Maak een nieuwe lijst voor de hiërarchische output
            hierarchical_df = []
            level_counter = {i: 1 for i in range(len(hierarchy_cols))}  # Hou het nummer per niveau bij
            
            # Functie om hiërarchie dynamisch te bouwen met herstart van nummering per niveau
            def build_hierarchy(group_data, hierarchy_columns, prefix=""):
                nonlocal hierarchical_df
                
                # Groeperen op het eerste niveau
                for group, subgroup_data in group_data.groupby(hierarchy_columns[0]):
                    row_data = [f"{prefix}{level_counter[len(hierarchy_columns) - len(hierarchy_columns)]}", f"{hierarchy_columns[0]}: {group}"]
                    for col in exclude_group_cols:
                        row_data.append(subgroup_data[col].iloc[0] if col in subgroup_data else None)
                    hierarchical_df.append(row_data)
                    
                    # Nummering per niveau herstarten
                    level_counter[len(hierarchy_columns) - len(hierarchy_columns)] += 1

                    # Als er nog meer kolommen in de hiërarchie zijn, herhaal het proces
                    if len(hierarchy_columns) > 1:
                        build_hierarchy(subgroup_data, hierarchy_columns[1:], prefix=f"{prefix}{level_counter[len(hierarchy_columns) - len(hierarchy_columns)]}.")
                    else:
                        # Voeg de samengevoegde waarden toe zonder verdere subgroepen
                        for idx, row in subgroup_data.iterrows():
                            hierarchical_df.append([f"{prefix}{level_counter[len(hierarchy_columns) - len(hierarchy_columns)]}.{idx+1}",
                                                     "_".join([str(val) for val in row[hierarchy_columns].values()]),  # Maak een ID gebaseerd op de samengevoegde kolomwaarden
                                                     *row[sum_cols].values] + 
                                                    [row[col] if col in row.index else None for col in exclude_group_cols])  # Voeg de exclusieve kolommen toe

            # Bouw de volledige hiërarchie vanaf het begin
            build_hierarchy(grouped_df, hierarchy_cols)
            
            # Controleer of alle rijen dezelfde lengte hebben voordat we ze in een DataFrame plaatsen
            columns = ["ID", "Omschrijving"] + sum_cols + exclude_group_cols
            corrected_hierarchical_df = []

            # Voeg lege kolommen toe indien nodig om inconsistentie in lengte te vermijden
            for row in hierarchical_df:
                while len(row) < len(columns):
                    row.append(None)  # Voeg None toe tot de rij de juiste lengte heeft
                corrected_hierarchical_df.append(row)
            
            # Zet de lijst van rijen om naar een DataFrame met de juiste kolomnamen
            hierarchical_df = pd.DataFrame(corrected_hierarchical_df, columns=columns)
            st.session_state['processed_df'] = hierarchical_df
            st.dataframe(hierarchical_df)

def main():
    load_file()
    process_data()
    download_result()

if __name__ == "__main__":
    main()
