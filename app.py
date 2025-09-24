# app.py - Main Application
import streamlit as st
import pandas as pd
from config import Config
from utils.data_loader import load_financial_data, load_demo_data
from utils.charts import (
    create_income_expense_chart, 
    create_category_breakdown, 
    create_budget_comparison,
    create_savings_trend
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate key financial KPIs
    """
    total_income = df[df['Type'] == 'Income']['Amount'].sum()
    total_expenses = df[df['Type'].isin(['Fixed', 'Variable'])]['Amount'].sum()
    total_investments = df[df['Type'] == 'Investment']['Amount'].sum()
    
    net_income = total_income + total_expenses  # expenses are negative
    savings_rate = (net_income / total_income * 100) if total_income > 0 else 0
    
    return {
        'total_income': total_income,
        'total_expenses': abs(total_expenses),
        'total_investments': abs(total_investments),
        'net_income': net_income,
        'savings_rate': savings_rate
    }

def main():
    # Page configuration
    st.set_page_config(
        page_title=Config.APP_TITLE,
        page_icon=Config.PAGE_ICON,
        layout=Config.LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("💰 Personal Finance Dashboard")
    st.markdown("*Real-time financial tracking and analytics*")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("📊 Dashboard Controls")
    
    # Load data
    with st.spinner("Loading financial data..."):
        df = load_financial_data()
        
        # Fallback to demo data
        if df.empty:
            st.sidebar.warning("⚠️ Using demo data")
            df = load_demo_data()
        else:
            st.sidebar.success("✅ Live data connected")
    
    if df.empty:
        st.error("❌ Unable to load data")
        return
    
    # Month filter
    available_months = sorted(df['Month'].unique())
    selected_months = st.sidebar.multiselect(
        "Select Months",
        available_months,
        default=available_months
    )
    
    # Category filter
    available_categories = sorted(df['Category'].unique())
    selected_categories = st.sidebar.multiselect(
        "Filter Categories",
        available_categories,
        default=available_categories
    )
    
    # Filter data
    filtered_df = df[
        (df['Month'].isin(selected_months)) & 
        (df['Category'].isin(selected_categories))
    ]
    
    if filtered_df.empty:
        st.warning("No data matches your filters. Please adjust your selection.")
        return
    
    # KPIs Section
    st.header("📈 Key Performance Indicators")
    kpis = calculate_kpis(filtered_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💵 Total Income", 
            f"${kpis['total_income']:,.2f}"
        )
    
    with col2:
        st.metric(
            "💸 Total Expenses", 
            f"${kpis['total_expenses']:,.2f}"
        )
    
    with col3:
        st.metric(
            "💰 Net Income", 
            f"${kpis['net_income']:,.2f}",
            delta=f"{kpis['savings_rate']:.1f}% savings rate"
        )
    
    with col4:
        st.metric(
            "📊 Investments", 
            f"${kpis['total_investments']:,.2f}"
        )
    
    st.markdown("---")
    
    # Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Monthly Overview")
        if not filtered_df.empty:
            fig1 = create_income_expense_chart(filtered_df)
            st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Variable Expenses")
        if not filtered_df.empty:
            fig2 = create_category_breakdown(filtered_df, 'Variable')
            st.plotly_chart(fig2, use_container_width=True)
    
    # Savings Trend
    st.subheader("💹 Savings Trend")
    if len(selected_months) > 1:
        fig4 = create_savings_trend(filtered_df)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Select multiple months to see savings trend")
    
    # Budget Analysis
    if 'Budget' in filtered_df.columns:
        st.subheader("📋 Budget vs Actual Analysis")
        fig3 = create_budget_comparison(filtered_df)
        if fig3.data:
            st.plotly_chart(fig3, use_container_width=True)
    
    # Data Table
    st.subheader("📄 Transaction Details")
    
    # Display options
    show_all = st.checkbox("Show all transactions")
    
    if show_all:
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(filtered_df.head(10), use_container_width=True)
        st.info(f"Showing 10 of {len(filtered_df)} transactions. Check 'Show all transactions' to see more.")
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit & Plotly | Data updated in real-time*")
    st.markdown("**GitHub Repository**: [personal-finance-dashboard](https://github.com)")

if __name__ == "__main__":
    main()