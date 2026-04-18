import streamlit as st

if st.button("← Back to Search"):
    st.switch_page('pages/FindApp.py')

if 'selected_app' in st.session_state:
    app = st.session_state['selected_app']
else:
    st.warning("Please select an app in search")
    st.stop()

st.title("Analytics")