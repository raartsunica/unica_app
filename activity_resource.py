import streamlit as st
import pandas as pd

st.title("Activity Resource Validation")

# Initialize session state to store files
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}

# File Uploads with Session State Handling
uploaded_files = {
    "WBS": st.file_uploader("Upload Project Work Breakdown Structure.xlsx", type="xlsx"),
    "Roles": st.file_uploader("Upload Project Resource Default Role Setup.xlsx", type="xlsx"),
    "Validation": st.file_uploader("Upload Project Validation Group Lines.xlsx", type="xlsx"),
    "Comparison": st.file_uploader("Upload Project Activity Resource Validation.xlsx", type="xlsx")
}

# Store files in session state to prevent refresh issues
for key, file in uploaded_files.items():
    if file:
        st.session_state.uploaded_files[key] = file

# Confirmation button before processing
if st.button("Confirm and Process"):
    if len(st.session_state.uploaded_files) < 4:
        st.warning("Please upload all required files before proceeding.")
    else:
        # Read the uploaded Excel files from session state
        df_wbs = pd.read_excel(st.session_state.uploaded_files["WBS"], usecols=["PROJECTID", "WBSID", "ROLE"])
        df_roles = pd.read_excel(st.session_state.uploaded_files["Roles"], usecols=["ROLEID", "RESOURCENAME"])
        df_validation = pd.read_excel(st.session_state.uploaded_files["Validation"], usecols=["PROJID", "RESOURCEID"])
        df_comparison = pd.read_excel(st.session_state.uploaded_files["Comparison"], usecols=["PROJECTID", "WBSID", "RESOURCEID"])

        # Merge data to determine expected combinations
        merged_wbs_roles = df_wbs.merge(df_roles, left_on="ROLE", right_on="ROLEID", how="left")
        expected_combinations = merged_wbs_roles.merge(df_validation, left_on="PROJECTID", right_on="PROJID", how="left")

        expected_combinations = expected_combinations[["PROJECTID", "WBSID", "RESOURCEID"]].dropna()

        # Find differences between expected_combinations and df_comparison
        merged_comparison = expected_combinations.merge(df_comparison, on=["PROJECTID", "WBSID", "RESOURCEID"], how="outer", indicator=True)

        differences = merged_comparison[merged_comparison["_merge"] != "both"].drop(columns=["_merge"])

        st.write("Differences found between expected and actual data:")
        st.dataframe(differences)

        # Allow user to download modified comparison file
        differences.to_excel("Updated_Validation_File.xlsx", index=False)
        
        with open("Updated_Validation_File.xlsx", "rb") as file:
            st.download_button("Download Updated Validation File", file, "Updated_Validation_File.xlsx")
