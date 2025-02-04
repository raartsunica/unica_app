import streamlit as st
import Calc_2_WBS
import activity_resource  # Import but don’t execute immediately

st.title("Project Resource Validation App")

# Selection for navigation
page = st.selectbox("Select a function:", ["Home", "Calc_2_WBS", "Activity Resource Validation"])

if page == "Calc_2_WBS":
    Calc_2_WBS.main()  # Ensure `Calc_2_WBS.py` has a `main()` function

elif page == "Activity Resource Validation":
    activity_resource.main()  # Ensure `activity_resource.py` has a `main()` function
