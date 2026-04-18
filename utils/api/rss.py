import requests
import streamlit as st

@st.cache_data(ttl=360, show_spinner=False)
def search_apps(query, limit, country="us"):
    """Search for apps in the App Store using the iTunes Search API"""
    url = "https://itunes.apple.com/search"
    params = {
        "term": query,
        "entity": "software",
        "country": country,
        "limit": limit
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        count = data.get("resultCount", 'No results found...')
        apps = data.get("results", [])
        return count, apps
    except Exception as e:
        return {"error": str(e)}

def fetch_reviews(app_id, country="us", sort="mostRecent", pages=10):
    """Fetch reviews for a specific app using the iTunes RSS feed."""
    reviews = []
    for page in range(1, pages + 1):
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby={sort}/json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            data = data.get("feed", []).get("entry")
            if not data:
                break
            reviews.extend(parse_reviews(data))
        except Exception as e:
            return {"error": str(e)}
    return reviews

def parse_reviews(data):
    """Parse the raw reviews to be used later."""
    records = []
    for entry in data:
        records.append({
            "author": entry['author']['name']['label'],
            "last_updated": entry['updated']['label'],
            "title": entry['title']['label'],
            "review": entry['content']['label'],
            "given_rating": int(entry['im:rating']['label']),
            "app_version": entry['im:version']['label'],
            "net_helpfulness": int(entry['im:voteSum']['label']),
            "helpfulness_count": int(entry['im:voteCount']['label']),
        })

    return records