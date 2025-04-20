import os

import requests
import streamlit as st

ML_API_HOST = os.getenv('ML_API_HOST', 'http://localhost:8000')


def format_status(name: str, value: str) -> str:
    """Return a formatted HTML string with emoji and colored text for status."""
    if 'reachable' in value:
        return f'✅ **{name}**: <span style="color:green">{value}</span>'
    else:
        return f'❌ **{name}**: <span style="color:red">{value}</span>'


def render_service_status(name: str, status: str) -> str:
    if 'reachable' == status.lower():
        emoji = '✅'
        color = 'green'
    else:
        emoji = '❌'
        color = 'red'
    return f'{emoji} <b>{name}:</b> <span style="color:{color}">{status}</span>'


def render_status_tag(status: str) -> str:
    color = 'green' if status.lower() == 'ok' else 'red'
    return f"""<span style="background-color:{color}; color:white;
        padding:0.25em 0.5em; border-radius:0.5em">{status.upper()}</span>"""


st.title('🐾 Welcome to the Animal Classifier!')
st.markdown("""
This app allows you to:

- 📈 Predict the type of an animal given its features
- 🧠 Train models with synthetic animal data    
- 🛠️ Monitor system health

Use the sidebar to navigate between pages. 👈
""")

st.subheader('🩺 System Health Check')
st.write('Click the button below to check the health of the ML API.')

if st.button('Check API Health'):
    try:
        response = requests.get(f'{ML_API_HOST}/health')
        if response.status_code == 200:
            result = response.json()

            box_content = f"""
            <div style='border-radius: 10px; background-color: #1e1e1e;
            padding: 1.2em; border: 1px solid #444;'>
                <h3 style='margin-top: 0;'>🧠 API Status: {render_status_tag(result['status'])}</h3>
                <p>{render_service_status('MinIO', result['minio'])}</p>
                <p>{render_service_status('PostgreSQL', result['postresql'])}</p>
                <p>{render_service_status('Data Service API', result['data_service_api'])}</p>
            </div>
            """

            st.markdown(box_content, unsafe_allow_html=True)
        else:
            st.error(f'Error: {response.status_code}')
            st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f'🚨 Connection error: {e}')
