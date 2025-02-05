import pandas as pd
file = st.file_uploader("Upload een Excel-bestand", type=["xlsx"])
if file:
    df = pd.read_excel(file)
    st.dataframe(df)
