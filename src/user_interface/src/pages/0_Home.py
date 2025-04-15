import os

import requests
import streamlit as st

ML_API_HOST = os.getenv("ML_API_HOST", "http://localhost:8000")


st.title("🐾 Welcome to the Animal Classifier!")
st.markdown("""
This app allows you to:

- 📈 Predict the type of an animal given its features
- 🧠 Train models with synthetic animal data    
- 🛠️ Monitor system health

Use the sidebar to navigate between pages. 👈
""")

# User can check all related services before asking for a prediction
if st.button("Check API Health"):
    try:
        response = requests.get(f"{ML_API_HOST}/health")
        if response.status_code == 200:
            result = response.json()
            st.json(result)
        else:
            st.error(f"Error: {response.status_code}")
            st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")