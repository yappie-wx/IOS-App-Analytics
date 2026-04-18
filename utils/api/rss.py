import requests
import streamlit as st

@st.cache_data(ttl=360, show_spinner=False)
def search_apps(query, limit, country="sg"):
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

@st.cache_data(ttl=360)
def fetch_reviews(app_id, country="sg", sort="mostRecent", pages=10):
    """Fetch reviews for a specific app using the iTunes RSS feed."""
    reviews = []
    for page in range(1, pages + 1):
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby={sort}/json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            entries = data.get("feed", {}).get("entry")  # Fix 1: fallback to {}
            if not entries:
                break

            # Fix 2: Apple returns a dict (not list) when there's only 1 entry
            if isinstance(entries, dict):
                entries = [entries]

            # Fix 3: Skip the first entry on page 1 (it's app metadata, not a review)
            if page == 1:
                entries = entries[1:]

            if not entries:
                continue

            reviews.extend(parse_reviews(entries))

        except Exception as e:
            continue  # Fix 4: skip bad pages instead of aborting everything

    if not reviews:
        return "No reviews found for this app."
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