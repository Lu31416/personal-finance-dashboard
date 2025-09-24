# utils/charts.py - Chart Generation
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_income_expense_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create income vs expense overview chart
    """
    monthly_summary = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
    
    fig = px.bar(
        monthly_summary, 
        x='Month', 
        y='Amount', 
        color='Type',
        title='Monthly Income vs Expenses',
        color_discrete_map={
            'Income': '#2E8B57',
            'Fixed': '#DC143C', 
            'Variable': '#FF6347',
            'Investment': '#4682B4'
        }
    )
    
    fig.update_layout(
        showlegend=True,
        height=400,
        xaxis_title="Month",
        yaxis_title="Amount ($)"
    )
    
    return fig

def create_category_breakdown(df: pd.DataFrame, expense_type: str = 'Variable') -> go.Figure:
    """
    Create category breakdown pie chart
    """
    expense_data = df[df['Type'] == expense_type]
    category_totals = expense_data.groupby('Category')['Amount'].sum().abs()
    
    fig = px.pie(
        values=category_totals.values,
        names=category_totals.index,
        title=f'{expense_type} Expenses Breakdown'
    )
    
    return fig

def create_budget_comparison(df: pd.DataFrame) -> go.Figure:
    """
    Create budget vs actual comparison
    """
    if 'Budget' not in df.columns:
        return go.Figure()
    
    comparison = df.groupby('Category')[['Amount', 'Budget']].sum()
    
    fig = go.Figure(data=[
        go.Bar(name='Actual', x=comparison.index, y=comparison['Amount']),
        go.Bar(name='Budget', x=comparison.index, y=comparison['Budget'])
    ])
    
    fig.update_layout(
        title='Budget vs Actual by Category',
        barmode='group',
        height=400
    )
    
    return fig

def create_savings_trend(df: pd.DataFrame) -> go.Figure:
    """
    Create savings trend over time
    """
    monthly_data = df.groupby('Month').agg({
        'Amount': lambda x: x[df.loc[x.index, 'Type'] == 'Income'].sum() + 
                          x[df.loc[x.index, 'Type'].isin(['Fixed', 'Variable'])].sum()
    }).reset_index()
    
    monthly_data.columns = ['Month', 'Net_Savings']
    
    fig = px.line(
        monthly_data,
        x='Month',
        y='Net_Savings',
        title='Monthly Savings Trend',
        markers=True
    )
    
    fig.update_layout(
        height=300,
        xaxis_title="Month",
        yaxis_title="Net Savings ($)"
    )
    
    return fig