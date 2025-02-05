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
            # Verwijder de geselecteerde 'exclusieve' groeperingskolommen uit de hiërarchie
            hierarchy_cols = [col for col in group_cols if col not in exclude_group_cols]
            
            # Groeperen en sommeren van de gegevens
            grouped_df = df.groupby(group_cols)[sum_cols].sum().reset_index()
            
            # Maak een nieuwe lijst voor de hiërarchische output
            hierarchical_df = []
            counter = 1
            
            # Groeperen op de geselecteerde kolommen en door de groepen itereren
            for group, group_data in grouped_df.groupby(hierarchy_cols[0] if hierarchy_cols else group_cols[0]):  # Groep op basis van de eerste geselecteerde kolom
                # Voeg de regel voor deze groep toe (bijvoorbeeld: "1", "Groep: [waarde]")
                row_data = [f"{counter}", f"{hierarchy_cols[0] if hierarchy_cols else group_cols[0]}: {group}"]
                
                # Voeg de exclusieve groeperingskolommen toe als losse kolommen
                for col in exclude_group_cols:
                    if col in group_data.columns:  # Check of de kolom bestaat
                        row_data.append(group_data[col].iloc[0])  # Neem de eerste waarde van deze kolommen
                    else:
                        row_data.append(None)  # Als de kolom niet bestaat, voeg None toe
                
                hierarchical_df.append(row_data)
                subgroup_counter = 1
                
                # Als er meer dan 1 groep is, groepeer dan op de tweede kolom
                if len(hierarchy_cols) > 1:
                    for subgroup, subgroup_data in group_data.groupby(hierarchy_cols[1]):
                        # Voeg de subgroep regel toe (bijvoorbeeld: "1.1", "Subgroep: [waarde]")
                        hierarchical_df.append([f"{counter}.{subgroup_counter}", f"{hierarchy_cols[1]}: {subgroup}"] + 
                                                [subgroup_data[col].iloc[0] if col in subgroup_data.columns else None for col in exclude_group_cols])  # Voeg ook de exclusieve kolommen toe
                        
                        # Voeg de samengevoegde waarden voor deze subgroep toe
                        for idx, row in subgroup_data.iterrows():
                            hierarchical_df.append([f"{counter}.{subgroup_counter}.{idx+1}",
                                                     "_".join([str(val) for val in row[hierarchy_cols].values]),  # Maak een ID gebaseerd op de samengevoegde kolomwaarden
                                                     *row[sum_cols].values])  # Voeg de gesommeerde waarden toe
                        subgroup_counter += 1
                else:
                    # Voeg de samengevoegde waarden toe zonder subgroepen
                    for idx, row in group_data.iterrows():
                        hierarchical_df.append([f"{counter}.{idx+1}",
                                                 "_".join([str(val) for val in row[hierarchy_cols].values]),
                                                 *row[sum_cols].values] + 
                                                [row[col] if col in row.index else None for col in exclude_group_cols])  # Voeg de exclusieve kolommen toe
                counter += 1
            
            # Zet de hiërarchische output om naar een DataFrame
            columns = ["ID", "Omschrijving"] + sum_cols + exclude_group_cols
            hierarchical_df = pd.DataFrame(hierarchical_df, columns=columns)
            st.session_state['processed_df'] = hierarchical_df
            st.dataframe(hierarchical_df)

def main():
    load_file()
    process_data()
    download_result()

if __name__ == "__main__":
    main()
