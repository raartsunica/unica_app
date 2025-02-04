import streamlit as st
import subprocess

st.title("Project Resource Validation App")

# Button to run Calc_2_WBS.py
if st.button("Run Calc_2_WBS"):
    subprocess.run(["python", "Calc_2_WBS.py"])

# Button to run activity_resource.py
if st.button("Run Activity Resource Validation"):
    subprocess.run(["python", "activity_resource.py"])
