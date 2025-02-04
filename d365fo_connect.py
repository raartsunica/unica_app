import msal
import requests
import pandas as pd
import streamlit as st

# Functie om OAuth-token te verkrijgen
def get_access_token(client_id, client_secret, tenant_id):
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(client_id, client_secret=client_secret, authority=authority)
    token_response = app.acquire_token_for_client(scopes=["https://<jouwdomein>.cloudax.dynamics.com/.default"])
    return token_response.get('access_token')

# Functie om gegevens op te halen van OData API
def fetch_data_from_odata(odata_url, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Prefer': 'odata.maxpagesize=1000',
    }
    response = requests.get(odata_url, headers=headers)
    if response.status_code == 200:
        return response.json()['value']  # De werkelijke data bevindt zich onder 'value'
    else:
        return None

# Functie om gegevens terug te sturen naar een OData API
def post_data_to_odata(odata_url, access_token, data):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    response = requests.post(odata_url, json=data, headers=headers)
    return response.status_code, response.text

def main():
# Streamlit UI
st.title('Gegevensbeheer in Dynamics 365 F&O')

# Gebruikersinvoer voor OAuth-gegevens
client_id = st.text_input('Client ID', type="password")
client_secret = st.text_input('Client Secret', type="password")
tenant_id = st.text_input('Tenant ID')

# Gebruikersinvoer voor OData URL's (4 entiteiten)
entity_1_url = st.text_input('URL van Entiteit 1', 'https://<jouwdomein>.cloudax.dynamics.com/data/Entity1')
entity_2_url = st.text_input('URL van Entiteit 2', 'https://<jouwdomein>.cloudax.dynamics.com/data/Entity2')
entity_3_url = st.text_input('URL van Entiteit 3', 'https://<jouwdomein>.cloudax.dynamics.com/data/Entity3')
entity_4_url = st.text_input('URL van Entiteit 4', 'https://<jouwdomein>.cloudax.dynamics.com/data/Entity4')

# Invoeren van doel-URL voor terugladen van gegevens
target_entity_url = st.text_input('URL voor terugladen naar doelentiteit', 'https://<jouwdomein>.cloudax.dynamics.com/data/TargetEntity')

# Verkrijgen van toegangstoken
if st.button('Verbinding maken en gegevens ophalen'):
    if not client_id or not client_secret or not tenant_id:
        st.error('Vul alle vereiste velden in.')
    else:
        try:
            # Verkrijg het access token
            access_token = get_access_token(client_id, client_secret, tenant_id)

            # Gegevens ophalen van de vier entiteiten
            data_1 = fetch_data_from_odata(entity_1_url, access_token)
            data_2 = fetch_data_from_odata(entity_2_url, access_token)
            data_3 = fetch_data_from_odata(entity_3_url, access_token)
            data_4 = fetch_data_from_odata(entity_4_url, access_token)

            # Controleer of de gegevens zijn opgehaald
            if data_1 is None or data_2 is None or data_3 is None or data_4 is None:
                st.error('Er is een fout opgetreden bij het ophalen van de gegevens.')
            else:
                # Combineer de data in één DataFrame (voor verwerking)
                df1 = pd.DataFrame(data_1)
                df2 = pd.DataFrame(data_2)
                df3 = pd.DataFrame(data_3)
                df4 = pd.DataFrame(data_4)

                # Toon de gegevens in de Streamlit app
                st.subheader('Gegevens van Entiteit 1')
                st.write(df1)
                st.subheader('Gegevens van Entiteit 2')
                st.write(df2)
                st.subheader('Gegevens van Entiteit 3')
                st.write(df3)
                st.subheader('Gegevens van Entiteit 4')
                st.write(df4)

                # Gegevens verwerken en klaarzetten voor terugsteken naar F&O
                combined_data = pd.concat([df1, df2, df3, df4], axis=0)  # Combineer de data
                combined_data_json = combined_data.to_dict(orient='records')  # Zet om naar JSON-formaat

                # Terugsteken naar de doelentiteit in F&O
                if st.button('Gegevens terugsteken naar F&O'):
                    status_code, response_text = post_data_to_odata(target_entity_url, access_token, combined_data_json)
                    if status_code == 200:
                        st.success('Gegevens succesvol teruggeladen naar F&O!')
                    else:
                        st.error(f"Fout bij terugladen van gegevens: {status_code} - {response_text}")

        except Exception as e:
            st.error(f"Er is een fout opgetreden: {str(e)}")

# Ensure main() runs only when called directly
if __name__ == "__main__":
    main()
