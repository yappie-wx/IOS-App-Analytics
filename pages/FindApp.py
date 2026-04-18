import streamlit as st

from utils import rss
from data.Forms import COUNTRIES, LIMIT_OPTIONS

st.title('Find an App')

# ===============================================
# Search Component
# ===============================================

# Sort Countries by Name
countries = dict(sorted(COUNTRIES.items(), key=lambda item: item[1]))

col1, col2, col3 = st.columns([4, 3, 1.2], vertical_alignment='bottom')
with col1:
    app_query = st.text_input(
        label="",
        icon=":material/search:",
    )
with col2:
    country_query = st.selectbox(
        label='',
        options=list(countries.keys()),
        format_func=lambda x: COUNTRIES[x],
        index=125
    )
with col3:
    limit_query = st.selectbox(
        label='',
        options=LIMIT_OPTIONS,
        index=1
    )

if app_query and not app_query.isspace():
    with st.spinner("Fetching Results..."):
        results = rss.search_apps(app_query, limit=limit_query, country=country_query)

        st.session_state['app_query_results'] = results

# ===============================================
# Display apps
# ===============================================
if "app_query_results" in st.session_state:
    count, apps = st.session_state['app_query_results']
    st.caption(f"{count} results found")
    for app in apps:
        icon = app.get("artworkUrl100", "").replace("100x100", "200x200")
        name = app['trackName']
        developer = app['sellerName']
        app_id = int(app['trackId'])

        icon_col, desc_col, info_col = st.columns([1,3,1], vertical_alignment='center')
        with icon_col:
            st.image(icon)
        with desc_col:
            st.subheader(name)
            st.caption(developer)
        with info_col:
            if st.button("See More", key=name, use_container_width=True):
                st.session_state['selected_app'] = app
                st.session_state['selected_country'] = country_query
                st.switch_page('pages/Analytics.py')