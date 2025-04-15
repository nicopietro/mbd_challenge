import streamlit as st

st.set_page_config(page_title="Animal ML App", page_icon="🐾")

pg = st.navigation([
    st.Page("pages/0_home.py", title="Home", icon="🏠"),
    st.Page("pages/1_predict.py", title="Predict", icon="📈"),
    st.Page("pages/2_train.py", title="Train", icon="🧠"),
])
pg.run()