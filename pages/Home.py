import streamlit as st

st.title("📊 App Store Insights")
st.caption("Turn user reviews into actionable insights with AI")

col1, col2 = st.columns(2)

with col1:
    if st.button("📂 Upload Reviews"):
        st.switch_page("pages/1_Home.py")

with col2:
    if st.button("⚡ Run Analysis"):
        st.switch_page("pages/3_Analytics.py")

st.divider()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Reviews Analyzed", "1,248")
col2.metric("Avg Rating", "4.2 ⭐")
col3.metric("Positive Sentiment", "68%")
col4.metric("Issues Detected", "134")

st.divider()

st.header("Features")

col_1, col_2, col_3 = st.columns(3)
with col_1:
    with st.container(border=True):
        st.subheader(":gray[:material/apps:]")
        st.write("**Sentiment Analysis**")
        st.caption("Classify reviews into positive, negative, neutral")

with col_2:
    with st.container(border=True):
        st.subheader(":gray[:material/home:]")
        st.write("**Home**")
        st.caption("Classify reviews into positive, negative, neutral")

with col_3:
    with st.container(border=True):
        st.subheader(":gray[:material/dashboard:]")
        st.write("**Home**")
        st.caption("Classify reviews into positive, negative, neutral")
