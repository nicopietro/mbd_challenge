import os
from datetime import datetime, time, timedelta

import requests
import streamlit as st

ML_API_HOST = os.getenv('ML_API_HOST', 'http://localhost:8000')

st.title('🧠 Train a New Model using synthetic data')

st.write('Select the number of synthetic datapoints to generate data for model training.')

datapoints = st.number_input('Number of synthetic datapoints', min_value=1, step=1, value=100)
seed = st.number_input('Random seed (optional)', min_value=0, step=1, value=42)

if st.button('Train Model from Synthetic Data'):
    payload = {'datapoints': datapoints, 'seed': seed}
    with st.spinner('🚀 Training model...'):
        try:
            response = requests.post(f'{ML_API_HOST}/api/v1/mpc/train/synthetic', params=payload)
            if response.status_code == 200:
                result = response.json()
                st.success(f'✅ Model trained successfully! ID: `{result["trained_model_id"]}`')
                st.subheader('📊 Model Metrics')
                st.json(result['model_metrics'])
            else:
                st.error(f'❌ Error: {response.status_code}')
                st.json(response.json())
        except requests.exceptions.RequestException as e:
            st.error(f'🚫 Connection error: {e}')

st.title('📅 Train a Model using real user data')

st.write('Select a time range to use real user-generated data for model training.')

now = datetime.now()

# Start datetime input
start_date = st.date_input('Start date', value=now.date() - timedelta(days=7))
start_time = st.time_input('Start time', value=time(0, 0))
start_datetime = datetime.combine(start_date, start_time).isoformat()

# End datetime input
end_date = st.date_input('End date', value=now.date())
end_time = st.time_input('End time', value=time(0, 0))
end_datetime = datetime.combine(end_date, end_time).isoformat()

# Format datetimes nicely
formatted_start = datetime.combine(start_date, start_time).strftime('%Y-%m-%d %H:%M')
formatted_end = datetime.combine(end_date, end_time).strftime('%Y-%m-%d %H:%M')

st.info(f'🕒 **Selected Time Range**\n\n📅 Start: `{formatted_start}`\n\n📅 End: `{formatted_end}`')


if st.button('Train Model from Real Data'):
    params = {
        'start': start_datetime,
        'end': end_datetime,
    }
    with st.spinner('🚀 Training model...'):
        try:
            response = requests.post(f'{ML_API_HOST}/api/v1/mpc/train/userdata', params=params)
            if response.status_code == 200:
                result = response.json()
                st.success(f'✅ Model trained using user data! ID: `{result["trained_model_id"]}`')
                st.subheader('📊 Model Metrics')
                st.json(result['model_metrics'])
            elif response.status_code == 404:
                st.warning('⚠️ No data found in the selected date range.')
            else:
                st.error(f'❌ Error: {response.status_code}')
                st.json(response.json())
        except requests.exceptions.RequestException as e:
            st.error(f'🚫 Connection error: {e}')
