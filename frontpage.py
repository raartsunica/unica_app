import streamlit as st

st.title("Calculation Sheet")

# Button to navigate to different script functionalities
page = st.selectbox("Select a function:", ["Home", "Calc_2_WBS", "Activity Resource Validation"])

if page == "Calc_2_WBS":
    import Calc_2_WBS  # This runs the script within the same Streamlit session
elif page == "Activity Resource Validation":
    import activity_resource  # Runs activity_resource.py
