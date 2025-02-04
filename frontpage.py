import streamlit as st
import d365fo_connect
import Calc_2_WBS
import activity_resource

st.title("Calculatie converter App")

# Selection for navigation
page = st.selectbox("Select a function:", ["Home", "Calculatie naar WBS", "Activity Resource Validation", "D365FO connector"])

if page == "Calculatie naar WBS":
    Calc_2_WBS.main()  # Ensure `Calc_2_WBS.py` has a `main()` function

elif page == "Activity Resource Validation":
    activity_resource.main()  # Ensure `activity_resource.py` has a `main()` function

elif page == "D365FO Connector":
    d365fo_connect.main()  # Ensure `activity_resource.py` has a `main()` function
