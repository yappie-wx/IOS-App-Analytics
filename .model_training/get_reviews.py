import requests
import pandas as pd

def fetch_reviews(app_id, country="us", sort="mostRecent", pages=10):
    """
    Fetch reviews for a specific app using the iTunes RSS feed.
    """
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
    """
    Parse the raw reviews to be used later.
    """
    records = []
    for entry in data:
        records.append({
            "author": entry['author']['name']['label'],
            "last_updated": entry['updated']['label'],
            "title": entry['title']['label'],
            "review": entry['content']['label'],
            "rating": int(entry['im:rating']['label']),
            "app_version": entry['im:version']['label'],
            "net_helpfulness": int(entry['im:voteSum']['label']),
            "helpfulness_count": int(entry['im:voteCount']['label']),
        })

    return records

apps_to_retrieve = {
    "Socials": [
        686449807, # Telegram
        1235601864, # TikTok
    ],
    "Productivity": [
        6448311069, # ChatGPT
        1232780281, # Notion
    ],
    "Delivery": [
        647268330, # Grab
        368677368, # Uber
    ],
    "Banking": [
        1049286296, # UOB
        932493382, # Revolut
    ],
    "Gaming": [
        1160056295, # Mobile Legends
        1330123889, # PUBG
    ],
    "Entertainment": [
        544007664, # Youtube
        389801252, # Instagram
        363590051, # Netflix
        959840394, # Shopee
    ],
    "Health": [
        426826309, # Strava
    ],
    "Navigation": [
        585027354, # Google Maps
    ]
}
records = []

for key, app_ids in apps_to_retrieve.items():
    for app_id in app_ids:
        app = fetch_reviews(app_id)
        records.extend(app)

pd.DataFrame(records).to_csv("reviews.csv")
