# app.py - Enhanced Application with Clear Instructions
import streamlit as st
import pandas as pd
from config import Config
from utils.data_loader import (
    load_data_with_fallback,
    display_data_status,
    show_upload_instructions,
    get_sample_data_download
)
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
    st.markdown("*Upload your financial data for personalized insights*")
    
    # Load data with fallback logic
    df, data_source = load_data_with_fallback()
    
    # Display data status in sidebar
    display_data_status(data_source, df)
    
    # Main content based on data source
    if data_source != "uploaded":
        # Show instructions for uploading data
        st.info("👆 **Upload your own financial data in the sidebar to get personalized insights!**")
        
        # Show detailed instructions
        show_upload_instructions()
        
        st.markdown("---")
        st.markdown("### 📊 Meanwhile, explore with sample data below:")
    
    else:
        # User uploaded their own data
        st.success("🎉 **Great! You're now viewing insights from your own financial data.**")
        st.markdown("---")
    
    # Sidebar Controls
    st.sidebar.title("🎛️ Dashboard Controls")
    
    # Show current data info
    if data_source == "google_sheets":
        st.sidebar.markdown("[📝 View sample data source](https://docs.google.com/spreadsheets/d/1k6DNSgJ5XHw1D7rM7JTkv_d8TmqVstgwTwj8qETBKsU/edit)")
    
    # Filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filters")
    
    # Month filter
    available_months = sorted(df['Month'].unique())
    selected_months = st.sidebar.multiselect(
        "📅 Select Months",
        available_months,
        default=available_months,
        help="Choose which months to include in analysis"
    )
    
    # Category filter
    available_categories = sorted(df['Category'].unique())
    selected_categories = st.sidebar.multiselect(
        "🏷️ Filter Categories",
        available_categories,
        default=available_categories,
        help="Choose which categories to include"
    )
    
    # Type filter
    available_types = sorted(df['Type'].unique())
    selected_types = st.sidebar.multiselect(
        "📊 Filter Types",
        available_types,
        default=available_types,
        help="Choose transaction types (Income, Fixed, Variable, etc.)"
    )
    
    # Filter data
    filtered_df = df[
        (df['Month'].isin(selected_months)) & 
        (df['Category'].isin(selected_categories)) &
        (df['Type'].isin(selected_types))
    ]
    
    if filtered_df.empty:
        st.warning("⚠️ No data matches your filters. Please adjust your selection.")
        return
    
    # Data summary in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📈 Current View:**")
    st.sidebar.markdown(f"• **Transactions:** {len(filtered_df)}")
    if selected_months:
        st.sidebar.markdown(f"• **Period:** {min(selected_months)} to {max(selected_months)}")
    st.sidebar.markdown(f"• **Categories:** {len(selected_categories)}")
    
    # KPIs Section
    st.header("📈 Key Performance Indicators")
    
    # Add context based on data source
    if data_source == "uploaded":
        st.markdown("*Based on your uploaded financial data*")
    else:
        st.markdown("*Based on sample data - upload your file to see your real numbers*")
    
    kpis = calculate_kpis(filtered_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💵 Total Income", 
            f"${kpis['total_income']:,.2f}",
            help="Sum of all income transactions in selected period"
        )
    
    with col2:
        st.metric(
            "💸 Total Expenses", 
            f"${kpis['total_expenses']:,.2f}",
            help="Sum of all expense transactions in selected period"
        )
    
    with col3:
        st.metric(
            "💰 Net Income", 
            f"${kpis['net_income']:,.2f}",
            delta=f"{kpis['savings_rate']:.1f}% savings rate",
            help="Income minus expenses (your actual savings)"
        )
    
    with col4:
        st.metric(
            "📊 Investments", 
            f"${kpis['total_investments']:,.2f}",
            help="Sum of all investment transactions"
        )
    
    st.markdown("---")
    
    # Charts Section
    st.header("📊 Financial Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Monthly Overview")
        fig1 = create_income_expense_chart(filtered_df)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Expense Breakdown")
        # Let user choose which type to analyze
        expense_types = [t for t in selected_types if t in ['Fixed', 'Variable', 'Investment']]
        if expense_types:
            selected_expense_type = st.selectbox("Select expense type:", expense_types, index=0)
            fig2 = create_category_breakdown(filtered_df, selected_expense_type)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No expense data to display with current filters")
    
    # Savings Trend (only if multiple months selected)
    if len(selected_months) > 1:
        st.subheader("💹 Savings Trend Over Time")
        fig4 = create_savings_trend(filtered_df)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("📊 Select multiple months in the sidebar to see savings trends")
    
    # Budget Analysis (if Budget column exists)
    if 'Budget' in filtered_df.columns:
        st.subheader("📋 Budget vs Actual Analysis")
        fig3 = create_budget_comparison(filtered_df)
        if fig3.data:
            st.plotly_chart(fig3, use_container_width=True)
    
    # Data Table Section
    st.header("📄 Transaction Details")
    
    # Display options
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        show_all = st.checkbox("Show all transactions")
    with col2:
        if st.button("📥 Download Data"):
            csv = filtered_df.to_csv(index=False)
            filename = "your_financial_data.csv" if data_source == "uploaded" else "sample_financial_data.csv"
            st.download_button(
                "💾 Click to Download",
                csv,
                filename,
                "text/csv",
                help="Download the currently filtered data"
            )
    with col3:
        if data_source != "uploaded":
            sample_csv = get_sample_data_download()
            st.download_button(
                "📥 Get Template",
                sample_csv,
                "financial_template.csv",
                "text/csv",
                help="Download template to create your own data file"
            )
    
    if show_all:
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(filtered_df.head(10), use_container_width=True)
        st.info(f"📊 Showing 10 of {len(filtered_df)} transactions. Check 'Show all' to see more.")
    
    # Call-to-action if using sample data
    if data_source != "uploaded":
        st.markdown("---")
        st.info("🎯 **Ready to analyze your own finances?** Upload your data file in the sidebar to get started!")
    
    # Help section
    st.markdown("---")
    with st.expander("❓ Need Help?"):
        st.markdown(f"""
        **How this dashboard works:**
        
        {'🎉 **You uploaded your own data!** This dashboard is showing insights from your personal financial information.' if data_source == 'uploaded' else '📊 **You are viewing sample data.** Upload your own file to see personalized insights.'}
        
        **To upload your own data:**
        1. **📥 Download template** - Click the template button to get the correct format
        2. **✏️ Fill with your data** - Add your income, expenses, and transactions
        3. **📤 Upload file** - Use the file uploader in the sidebar
        4. **📊 Get insights** - See your personalized financial dashboard!
        
        **Required columns:**
        - **Month**: January2025, Feb2025, etc.
        - **Type**: Income, Fixed, Variable, Investment  
        - **Category**: Salary, Rent, Food, etc.
        - **Amount**: 5000 (income), -1200 (expenses)
        
        **🔒 Privacy:** Your data is processed securely in your browser and never stored on our servers.
        """)
    
    # Footer
    st.markdown("---")
    footer_text = "Built with ❤️ using Streamlit & Plotly"
    if data_source == "uploaded":
        footer_text += " | Your data is processed securely and privately"
    else:
        footer_text += " | Upload your data to get personalized insights"
    
    st.markdown(f"*{footer_text}*")

if __name__ == "__main__":
    main()
