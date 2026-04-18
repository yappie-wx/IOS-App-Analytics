import streamlit as st

def sidebar():
    pages = {
        ":material/apps: Apps": [
            st.Page("pages/Home.py", title=':material/home: Home'),
            st.Page("pages/FindApp.py", title=':material/search: Find an App'),
        ],
        ":material/build: Tools": [
            st.Page('pages/Analytics.py', title=':material/dashboard: Analytics'),
            st.Page('pages/Debug.py', title=':material/bug_report: Debug'),
        ]
    }

    pg = st.navigation(pages, position='sidebar')
    pg.run()

def page_config():
    ABOUT_TEXT = """
        ### 🚀 About This App

        This application is designed to help you make sense of app store data quickly and effectively. It brings together powerful analysis tools to turn raw user reviews into clear, actionable insights.

        **What you can do:**
        - Understand user sentiment at a glance (positive, negative, neutral)
        - Identify key issues and feature requests from large volumes of reviews
        - Detect trends and patterns to guide product decisions
        - Filter out noise such as spam or irrelevant content

        Built with a focus on simplicity and speed, the app is ideal for developers, product managers, and anyone looking to improve their app based on real user feedback.

        Whether you're debugging issues, planning new features, or tracking user satisfaction, this tool helps you move from 

        **Data → Insight → Action**.
    """
    st.set_page_config(
        page_icon="assets/icons/app_store.png",
        page_title="App Store Analysis",
        layout="centered",
        menu_items={
            "Get Help": None,
            "Report a Bug": None,
            "About": ABOUT_TEXT,
        }
    )

    st.logo(
        image=':material/analytics:',
        size='large'
    )