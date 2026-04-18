import streamlit as st
from utils import navigation, classifiers

if __name__ == '__main__':
    classifiers.load_classifier_models()
    navigation.page_config()
    navigation.sidebar()