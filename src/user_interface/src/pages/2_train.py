import os
import requests
import streamlit as st

ML_API_HOST = os.getenv("ML_API_HOST", "http://localhost:8000")

st.title("🧠 Train a New Model")

st.write("Use this page to train a new model with synthetic animal data.")

datapoints = st.number_input("Number of synthetic datapoints", min_value=1, step=1, value=100)
seed = st.number_input("Random seed (optional)", min_value=0, step=1, value=42)

if st.button("Train Model"):
    payload = {"datapoints": datapoints, "seed": seed}
    try:
        response = requests.post(f"{ML_API_HOST}/api/v1/mpc/train", params=payload)
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ Model trained successfully! ID: `{result['trained_model_id']}`")
            st.subheader("📊 Model Metrics")
            st.json(result["model_metrics"])
        else:
            st.error(f"❌ Error: {response.status_code}")
            st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"🚫 Connection error: {e}")
