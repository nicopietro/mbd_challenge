import os

import requests

import streamlit as st

ML_API_HOST = os.getenv("ML_API_HOST", "http://localhost:8000")

st.title("Animal Classifier")
st.subheader("Enter the features of the animal:")

height = st.number_input("Height (m)", min_value=0.1)
weight = st.number_input("Weight (kg)", min_value=0.1)
walks_on_n_legs = st.number_input("Number of Legs ", min_value=2, max_value=4, step=2)
has_wings = st.checkbox("Has wings?")
has_tail = st.checkbox("Has tail?")

try:
    model_response = requests.get(f"{ML_API_HOST}/api/v1/mpc/models")
    if model_response.status_code == 200:
        models = model_response.json().get("models", [])
    else:
        models = []
        st.warning("Could not retrieve models from the server.")
except requests.exceptions.RequestException:
    models = []
    st.warning("Connection error while fetching models.")

selected_model = st.selectbox(
    "Select a model to use for prediction:",
    sorted(models, reverse=True),
    index=0 if models else None,
    placeholder="Choose a model timestamp...",
)

if st.button("Classify"):
    payload = [{
        "height": height,
        "weight": weight,
        "walks_on_n_legs": walks_on_n_legs,
        "has_wings": has_wings,
        "has_tail": has_tail
    }]
    try:
        response = requests.post(f"{ML_API_HOST}/api/v1/mpc/predict", json=payload)
        if response.status_code == 200:
            result = response.json()
            animal = result["prediction"][0]["animal_type"]
            emojis = {
                "dog": "🐶",
                "chicken": "🐔",
                "kangaroo": "🦘",
                "elephant": "🐘"
            }
            emoji = emojis.get(animal, "🐾")  # Default emoji

            st.success(f"The predicted animal is: **{animal.capitalize()}** {emoji}")
        else:
            st.error(f"Error: {response.status_code}")
            st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")