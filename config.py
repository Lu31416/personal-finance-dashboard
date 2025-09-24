# config.py - Secure Configuration
import os
import streamlit as st
from typing import Optional

def get_env_var(key: str, default: Optional[str] = None) -> str:
    """
    Safely retrieve environment variables
    Priority: Streamlit secrets > .env > default
    """
    # 1. Try to get from Streamlit secrets (production)
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except:
        pass
    
    # 2. Try to get from local environment variable
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # 3. Use default or raise error
    if default is not None:
        return default
    
    raise ValueError(f"Environment variable {key} not found!")

# Secure configurations
class Config:
    # Data source URLs - public spreadsheet, no API key needed!
    GOOGLE_SHEET_URL = get_env_var(
        'GOOGLE_SHEET_URL', 
        'https://docs.google.com/spreadsheets/d/1k6DNSgJ5XHw1D7rM7JTkv_d8TmqVstgwTwj8qETBKsU/export?format=csv'
    )
    
    # App configurations
    APP_TITLE = "Personal Finance Dashboard"
    PAGE_ICON = "💰"
    LAYOUT = "wide"
    
    # Cache settings
    CACHE_TTL = 300  # 5 minutes