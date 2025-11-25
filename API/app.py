import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import platform
import requests
from dotenv import load_dotenv

st.set_page_config(
    page_title="사이버 금융범죄 분석",
    layout="wide"
)
