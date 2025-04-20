import os
from datetime import datetime, time, timedelta

import pandas as pd
import requests
import streamlit as st

ML_API_HOST = os.getenv('ML_API_HOST', 'http://localhost:8000')

st.title('📋 User Data Viewer')
st.write('Use this page to explore user-submitted animal records stored in the database.')

# Get current time for consistent default values
now = datetime.now()

# Start datetime input
start_date = st.date_input('Start date', value=now.date() - timedelta(days=7))
start_time = st.time_input('Start time', value=time(0, 0))
start_datetime = datetime.combine(start_date, start_time).isoformat()

# End datetime input
end_date = st.date_input('End date', value=now.date())
end_time = st.time_input('End time', value=time(0, 0))
end_datetime = datetime.combine(end_date, end_time).isoformat()

if st.button('🔍 Load User Data'):
    params = {'start': start_datetime, 'end': end_datetime}
    try:
        response = requests.get(f'{ML_API_HOST}/api/v1/mpc/animals', params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                st.success(f'✅ Found {len(data)} records between the selected dates.')
                data = pd.DataFrame(data)
                desired_order = [
                    'id',
                    'height',
                    'weight',
                    'walks_on_n_legs',
                    'has_wings',
                    'has_tail',
                    'animal_type',
                    'timestamp',
                ]

                data = data[desired_order]
                st.data_editor(data, hide_index=True, use_container_width=True, disabled=True)
            else:
                st.warning('⚠️ No records found for the selected time range.')
        else:
            st.error(f'❌ Error {response.status_code}')
            st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f'🚫 Connection error: {e}')
