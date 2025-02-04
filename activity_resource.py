import streamlit as st
import pandas as pd

def main():
    st.title("Activity Resource Validation")

    # Initialize session state for storing uploaded files
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {}

    # File Uploads
    uploaded_files = {
        "WBS": st.file_uploader("Upload Project Work Breakdown Structure.xlsx", type="xlsx"),
        "Roles": st.file_uploader("Upload Project Resource Default Role Setup.xlsx", type="xlsx"),
        "Validation": st.file_uploader("Upload Project Validation Group Lines.xlsx", type="xlsx"),
        "Comparison": st.file_uploader("Upload Project Activity Resource Validation.xlsx", type="xlsx")
    }

    # Store uploaded files in session state
    for key, file in uploaded_files.items():
        if file:
            st.session_state.uploaded_files[key] = file

    # Confirmation button to process the files
    if st.button("Confirm and Process"):
        if len(st.session_state.uploaded_files) < 4:
            st.warning("Please upload all required files before proceeding.")
        else:
            try:
                # Read required columns from each file
                df_wbs = pd.read_excel(st.session_state.uploaded_files["WBS"], usecols=["PROJECTID", "WBSID", "ROLE"])
                df_roles = pd.read_excel(st.session_state.uploaded_files["Roles"], usecols=["ROLEID", "RESOURCENAME"])
                df_validation = pd.read_excel(st.session_state.uploaded_files["Validation"], usecols=["PROJID", "RESOURCEID"])
                df_comparison = pd.read_excel(st.session_state.uploaded_files["Comparison"], usecols=["PROJECTID", "WBSID", "RESOURCEID"])

                # Step 1: Merge Validation with Roles on PROJID and ROLEID
                merged_validation_roles = df_validation.merge(df_roles, left_on="RESOURCEID", right_on="ROLEID", how="left")

                # Step 2: Merge the result of Step 1 with WBS on PROJECTID and ROLEID
                final_combinations = merged_validation_roles.merge(df_wbs, left_on=["PROJID", "ROLEID"], right_on=["PROJECTID", "ROLE"], how="left")

                # Keep only necessary columns: PROJECTID, WBSID, RESOURCEID
                final_combinations = final_combinations[["PROJECTID", "WBSID", "RESOURCEID"]].dropna()

                # Display Calculated Results Table (Valid Expected Combinations)
                st.subheader("Calculated Results from Files 1, 2, and 3")
                st.dataframe(final_combinations)

                # Display File 4 (Comparison File)
                st.subheader("Contents of File 4: Project Activity Resource Validation")
                st.dataframe(df_comparison)

                # Find differences between final_combinations and df_comparison
                merged_comparison = final_combinations.merge(
                    df_comparison, on=["PROJECTID", "WBSID", "RESOURCEID"], how="outer", indicator=True
                )

                differences = merged_comparison[merged_comparison["_merge"] != "both"].drop(columns=["_merge"])

                # Display Differences
                st.subheader("Differences Found")
                st.dataframe(differences)

                # Provide download option for differences
                differences.to_excel("Updated_Validation_File.xlsx", index=False)
                with open("Updated_Validation_File.xlsx", "rb") as file:
                    st.download_button("Download Updated Validation File", file, "Updated_Validation_File.xlsx")
            
            except ValueError as e:
                st.error(f"Error: {e}. Please ensure all files contain the required columns.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# Ensure main() runs only when called directly
if __name__ == "__main__":
    main()
