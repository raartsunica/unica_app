import streamlit as st
from calculate_wbs import load_file, process_data, download_result
from activity_resource import get_dynamics_data, filter_data, merge_data, compare_target

def main():
    st.title("Power Platform App")
    menu = st.sidebar.radio("Kies een functie", ["Home", "Calculatie naar WBS", "Combineren Activiteit en Resource", "Opzetten project"])
    
    if menu == "Home":
        st.write("Welkom bij de Power Platform App. Selecteer een functie in het menu.")
    
    elif menu == "Calculatie naar WBS":
        st.header("Calculatie naar WBS")
        load_file()
        process_data()
        download_result()
    
    elif menu == "Combineren Activiteit en Resource":
        st.header("Combineren Activiteit en Resource")
        data = get_dynamics_data()
        if data:
            filtered_data = filter_data(data)
            st.dataframe(filtered_data)
            # Voeg functionaliteit toe om gegevens te combineren en vergelijken
    
    elif menu == "Opzetten project":
        st.header("Opzetten project")
        st.write("Deze functionaliteit wordt nog uitgewerkt.")
    
if __name__ == "__main__":
    main()
