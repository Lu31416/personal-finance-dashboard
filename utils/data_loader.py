# utils/data_loader.py - Enhanced Data Loading with Clear Instructions
import pandas as pd
import streamlit as st
import io
from config import Config

def validate_data_format(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Validate if uploaded data has required format
    Returns: (is_valid, error_message)
    """
    required_columns = ['Month', 'Type', 'Category', 'Amount']
    
    if df.empty:
        return False, "File is empty"
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check if Amount column can be converted to numeric
    try:
        pd.to_numeric(df['Amount'], errors='coerce')
    except:
        return False, "Amount column must contain numeric values"
    
    return True, "Valid format"

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize data
    """
    df_clean = df.copy()
    
    # Convert Amount to numeric, handling errors
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce')
    
    # Remove rows with invalid amounts
    df_clean = df_clean.dropna(subset=['Amount'])
    
    # Standardize text columns
    text_columns = ['Month', 'Type', 'Category']
    for col in text_columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
    
    # Add Description column if not present
    if 'Description' not in df_clean.columns:
        df_clean['Description'] = df_clean['Category']
    
    return df_clean

@st.cache_data(ttl=Config.CACHE_TTL)
def load_google_sheets_data() -> pd.DataFrame:
    """
    Load financial data from Google Sheets (fallback data)
    """
    try:
        df = pd.read_csv(Config.GOOGLE_SHEET_URL)
        
        is_valid, error_msg = validate_data_format(df)
        if not is_valid:
            return pd.DataFrame()
        
        return clean_data(df)
        
    except Exception as e:
        return pd.DataFrame()

def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    """
    Load data from uploaded file (CSV or Excel)
    """
    try:
        # Security: Check file size (10MB limit)
        MAX_SIZE = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > MAX_SIZE:
            st.error("File too large. Maximum size is 10MB.")
            return pd.DataFrame()
        
        # Determine file type and read accordingly
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel files.")
            return pd.DataFrame()
        
        # Security: Limit number of rows
        MAX_ROWS = 10000
        if len(df) > MAX_ROWS:
            st.warning(f"File has {len(df)} rows. Using first {MAX_ROWS} rows only.")
            df = df.head(MAX_ROWS)
        
        # Validate format
        is_valid, error_msg = validate_data_format(df)
        if not is_valid:
            st.error(f"❌ File format error: {error_msg}")
            st.info("📥 Please download the template below to see the correct format")
            return pd.DataFrame()
        
        return clean_data(df)
        
    except Exception as e:
        st.error(f"Error reading uploaded file: {str(e)}")
        return pd.DataFrame()

def get_sample_data_download():
    """
    Create a sample CSV for users to download as template
    """
    sample_data = {
        'Month': ['January2025', 'January2025', 'January2025', 'January2025', 'February2025', 'February2025'],
        'Type': ['Income', 'Fixed', 'Variable', 'Variable', 'Income', 'Fixed'],
        'Category': ['Salary', 'Rent', 'Food', 'Transportation', 'Salary', 'Rent'],
        'Description': ['Monthly salary', 'Apartment rent', 'Groceries', 'Gas and parking', 'Monthly salary', 'Apartment rent'],
        'Amount': [5000, -1200, -400, -150, 5000, -1200]
    }
    df = pd.DataFrame(sample_data)
    
    # Convert to CSV string
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()

def show_upload_instructions():
    """
    Show detailed instructions on how to prepare and upload data
    """
    st.markdown("### 📤 How to Upload Your Financial Data")
    
    # Step-by-step instructions
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **📋 Step 1: Prepare Your Data**
        Your file must have these 4 columns (case-sensitive):
        - **Month**: January2025, Feb2025, 2025-01, etc.
        - **Type**: Income, Fixed, Variable, Investment
        - **Category**: Salary, Rent, Food, Gas, etc.
        - **Amount**: 5000 (income), -1200 (expenses)
        
        **💡 Tips:**
        - Use positive numbers for income (5000)
        - Use negative numbers for expenses (-400)
        - Keep categories simple (Food, Transport, etc.)
        - Any month format works (January2025, Jan-25)
        
        **📥 Step 2: Download Template**
        Click the button below to get a sample file with the correct format
        
        **🚀 Step 3: Upload & Analyze**
        Upload your file and see instant insights!
        """)
    
    with col2:
        st.markdown("**📊 Example Data:**")
        example_df = pd.DataFrame({
            'Month': ['Jan2025', 'Jan2025', 'Jan2025'],
            'Type': ['Income', 'Fixed', 'Variable'],
            'Category': ['Salary', 'Rent', 'Food'],
            'Amount': [5000, -1200, -400]
        })
        st.dataframe(example_df, use_container_width=True)
    
    # Download template button (prominent)
    st.markdown("---")
    sample_csv = get_sample_data_download()
    st.download_button(
        "📥 **Download Template File (Recommended)**",
        sample_csv,
        "financial_data_template.csv",
        "text/csv",
        help="Download this template, fill with your data, then upload back",
        type="primary"
    )

def display_file_upload_section():
    """
    Display file upload section with clear instructions
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Upload Your Data")
    
    # File uploader with clear instructions
    uploaded_file = st.sidebar.file_uploader(
        "Choose your financial file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload CSV or Excel file with your financial data"
    )
    
    if uploaded_file is None:
        st.sidebar.info("📥 No file uploaded yet")
        st.sidebar.markdown("**👆 Upload your file to see your own data**")
    
    # Security and format info
    with st.sidebar.expander("ℹ️ File Requirements"):
        st.markdown("""
        **Required columns:**
        - Month, Type, Category, Amount
        
        **File limits:**
        - Max size: 10MB
        - Max rows: 10,000
        - Formats: CSV, Excel (.xlsx, .xls)
        
        **Security:**
        - Data processed securely
        - Never stored on servers
        - Session-only processing
        """)
    
    return uploaded_file

def load_data_with_fallback():
    """
    Main data loading function with fallback logic
    Returns: (df, data_source_message)
    """
    # Try to get uploaded file
    uploaded_file = display_file_upload_section()
    
    if uploaded_file is not None:
        # User uploaded a file
        with st.spinner("🔄 Processing your uploaded file..."):
            df = load_uploaded_file(uploaded_file)
            
            if not df.empty:
                return df, "uploaded"
            else:
                # Upload failed, show Google Sheets data
                st.sidebar.error("❌ Upload failed")
                st.sidebar.info("📊 Showing sample data instead")
    
    # No file uploaded or upload failed - show Google Sheets data
    with st.spinner("📊 Loading sample data..."):
        df = load_google_sheets_data()
        
        if not df.empty:
            return df, "google_sheets"
        else:
            # Google Sheets also failed, create demo data
            demo_data = {
                'Month': ['August2025'] * 6 + ['September2025'] * 6,
                'Type': ['Income', 'Income', 'Fixed', 'Fixed', 'Variable', 'Variable'] * 2,
                'Category': ['Salary', 'Freelance', 'Housing', 'Utilities', 'Food', 'Leisure'] * 2,
                'Description': ['Main job', 'Freelance work', 'Rent', 'Bills', 'Groceries', 'Entertainment'] * 2,
                'Amount': [5000, 1200, -1200, -400, -550, -220, 5000, 1500, -1200, -400, -600, -200]
            }
            return pd.DataFrame(demo_data), "demo"

def display_data_status(data_source: str, df: pd.DataFrame):
    """
    Display data source status in sidebar
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Data Status")
    
    if data_source == "uploaded":
        st.sidebar.success("✅ Your file loaded successfully!")
        st.sidebar.info(f"📈 {len(df)} transactions from your data")
        st.sidebar.markdown("*This is your personal financial data*")
        
    elif data_source == "google_sheets":
        st.sidebar.info("📊 Showing sample financial data")
        st.sidebar.markdown(f"*{len(df)} sample transactions*")
        st.sidebar.markdown("👆 **Upload your file above to see your own data**")
        
    elif data_source == "demo":
        st.sidebar.warning("⚠️ Using demo data")
        st.sidebar.markdown("*Sample data for demonstration*")
        st.sidebar.markdown("👆 **Upload your file above to analyze your own finances**")
