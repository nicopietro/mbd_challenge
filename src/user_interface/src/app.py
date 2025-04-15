import streamlit as st

from ml_service_requests import check_api_health

st.title("Animal Prediction App")

if st.button("Check API Health"):
    health_status = check_api_health()
    st.json(health_status)