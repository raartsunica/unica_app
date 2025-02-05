import requests
import json

def get_dynamics_data():
    with open('config.json') as config_file:
        config = json.load(config_file)
    url = config["api_url"]
    headers = {"Authorization": f"Bearer {config['token']}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Fout bij ophalen van data uit Dynamics 365")
        return None

def filter_data(data):
    project_nummer = st.text_input("Voer projectnummer in")
    if project_nummer:
        filtered_data = [record for record in data if record['project'] == project_nummer]
        return filtered_data
    return data

def merge_data(df1, df2, join_type):
    return df1.merge(df2, how=join_type)

def compare_target(df, target_df):
    return df.compare(target_df)
