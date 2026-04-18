import streamlit as st
import pandas as pd

from utils import rss, classifiers

st.set_page_config(layout='wide')

if st.button("← Back to Search"):
    st.switch_page('pages/FindApp.py')

if 'selected_app' in st.session_state:
    sent_model, int_model = classifiers.load_classifier_models()
    app = st.session_state['selected_app']
    country = st.session_state['selected_country']
    reviews = rss.fetch_reviews(
        app_id=app['trackId'],
        country=country
    )

else:
    st.warning("Please select an app in search")
    st.stop()

reviews_df = pd.DataFrame(reviews)
preds = pd.DataFrame(classifiers.predict_batch(reviews, sent_model, int_model))
df = pd.merge(reviews_df, preds, left_index=True, right_index=True)

sentiments = df['sentiment'].value_counts()
intents = df['intent'].value_counts()

rating_distri = df['given_rating'].value_counts().sort_index()
df['smoothed_rating'] = df['given_rating'].rolling(window=10, min_periods=1).mean()

version_ratings = df.groupby('app_version')['given_rating'].mean().reset_index()

def score_reviews(reviews):
    sent_score = (sentiments['positive']) / (len(reviews_df.index))
    rating_score = (rating_distri[5] + rating_distri[4]) / len(reviews_df.index)

    score = (sent_score * 0.4) + (rating_score * 0.6)

    if score >= 0.8:
        return ":green[Very Positive]"
    elif score >= 0.55:
        return ":green[Positive]"
    elif score >= 0.45:
        return "Neutral"
    elif score >= 0.2:
        return ":red[Negative]"
    elif score >= 0:
        return ":red[Very Negative]"

score = score_reviews(sentiments)

def metrics():
    col1, col2, col3 = st.columns(3, border=True)
    with col1:
        st.metric(label="Positive Reviews", value=sentiments['positive'])
    with col2:
        st.metric(label="Negative Reviews", value=sentiments['negative'])
    with col3:
        st.metric(label="Recent Reviews", value=score)

st.title(":material/dashboard: Analytics")

import plotly.express as px

metrics()

rating_distr_plot = px.bar(
    rating_distri, 
    labels={
        "given_rating": "User Given Rating",
        "value": "Count"
    },
    title="Ratings Distribution",
)
st.plotly_chart(rating_distr_plot)

ratings_over_time_plot = px.line(
    df,
    x='last_updated',
    y='smoothed_rating',
    labels={
        'last_updated': "Date Updated",
        'smoothed_rating': "Rating"
    },
    title="Ratings Over Time"
)
st.plotly_chart(ratings_over_time_plot)

intent_distri_plot = px.bar(
    intents,
    labels={
        'intent': "Intent",
        'value': "Count"
    },
    title="Intents Distribution",
)
st.plotly_chart(intent_distri_plot)

intent_distri_pie_plot = px.pie(
    intents,
    values="count",
    names=intents.index,
    title="Intents Distribution",
)
st.plotly_chart(intent_distri_pie_plot)

sentiment_distri_plot = px.bar(
    sentiments,
    labels={
        'sentiment': "Sentiment",
        'value': "Count"
    },
    title="Sentiment Distribution",
)
st.plotly_chart(sentiment_distri_plot)

sentiment_distri_pie_plot = px.pie(
    sentiments,
    values="count",
    names=sentiments.index,
    title="Sentiment Distribution",
)
st.plotly_chart(sentiment_distri_pie_plot)

version_ratings_plot = px.bar(
    version_ratings,
    x='app_version',
    y='given_rating',
    labels={
        'given_rating': 'Mean Rating', 
        'app_version': 'App Version'
    },
    title="Ratings for Versions"
)
st.plotly_chart(version_ratings_plot)