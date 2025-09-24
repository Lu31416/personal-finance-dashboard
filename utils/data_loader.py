# utils/data_loader.py - Secure Data Loading
import pandas as pd
import streamlit as st
import requests
from config import Config

@st.cache_data(ttl=Config.CACHE_TTL)
def load_financial_data() -> pd.DataFrame:
    """
    Safely load financial data with caching
    """
    try:
        # Option 1: Public Google Sheets
        df = pd.read_csv(Config.GOOGLE_SHEET_URL)
        
        # Basic validations
        required_columns = ['Month', 'Type', 'Category', 'Amount']
        if not all(col in df.columns for col in required_columns):
            st.error("Invalid data format!")
            return pd.DataFrame()
        
        # Basic cleaning
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df = df.dropna(subset=['Amount'])
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_demo_data() -> pd.DataFrame:
    """
    Demo data matching your spreadsheet format
    """
    demo_data = {
        'Month': ['August2025'] * 6 + ['September2025'] * 6,
        'Type': ['Income', 'Income', 'Fixed', 'Fixed', 'Variable', 'Variable'] * 2,
        'Category': ['Salary', 'Freelance', 'Housing', 'Utilities', 'Food', 'Leisure'] * 2,
        'Description': ['Main job', 'Freelance work', 'Rent', 'Bills', 'Groceries', 'Entertainment'] * 2,
        'Amount': [5000, 1200, -1200, -400, -550, -220, 5000, 1500, -1200, -400, -600, -200]
    }
    return pd.DataFrame(demo_data)