import streamlit as st

from utils import rss, classifiers

if st.button("← Back to Search"):
    st.switch_page('pages/FindApp.py')

if 'selected_app' in st.session_state:
    classifiers.load_classifier_models()
    app = st.session_state['selected_app']
    country = st.session_state['selected_country']
    reviews = rss.fetch_reviews(
        app_id=app['trackId'],
        country=country
    )
else:
    st.warning("Please select an app in search")
    st.stop()

def metrics():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Reviews", value=app['total_reviews'])
    with col2:
        st.metric(label="Positive Reviews", value=app['positive_reviews'])
    with col3:
        st.metric(label="Negative Reviews", value=app['negative_reviews'])

st.title(":material/dashboard: Analytics")