import streamlit as st
import pandas as pd
import plotly.express as px
from utils.meta_api import init_api, get_ad_accounts, get_active_campaigns, get_campaign_insights, get_daily_insights
import toml

# Set page configuration
st.set_page_config(
    page_title="Cafe Marketing Dashboard",
    page_icon="☕",
    layout="wide"
)

# Defaults
DEFAULT_ACCOUNT_NAME = "Chaitanya Soni"
DEFAULT_CAMPAIGN_NAME_KEYWORD = "Sardi ki Chai"

# Load helper functions for loading secrets safely
def load_token():
    try:
        if "FACEBOOK_ACCESS_TOKEN" in st.secrets["general"]:
             return st.secrets["general"]["FACEBOOK_ACCESS_TOKEN"]
    except FileNotFoundError:
        secrets_path = ".streamlit/secrets.toml"
        try:
            with open(secrets_path, "r") as f:
                config = toml.load(f)
                return config.get("general", {}).get("FACEBOOK_ACCESS_TOKEN")
        except:
             return None
    return None

# Simple CSS that adapts to theme
st.markdown("""
    <style>
    .stMetric {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Helper to extract landing page views
def get_landing_page_views(actions):
    if not actions:
        return 0
    for action in actions:
        if action.get('action_type') == 'landing_page_view':
            return int(action.get('value', 0))
    return 0

def main():
    st.title("☕ Cafe Marketing Dashboard")
    st.markdown(f"**Campaign Performance Overview**")

    # Initialize API
    token = load_token()
    if not token:
        st.error("API Token not found. Please configure secrets.")
        st.stop()
    
    if not init_api(token):
        st.error("Failed to connect to Facebook Marketing API.")
        st.stop()

    # --- Ads Account Selection (Hidden Logic) ---
    with st.spinner("Loading Data..."):
        accounts = get_ad_accounts()
    
    if not accounts:
        st.warning("No Ad Accounts found linked to this profile.")
        st.stop()

    # Logic to select default account
    account_map = {acc['name']: acc['id'] for acc in accounts}
    selected_account_name = None
    
    # Check if default exists
    if DEFAULT_ACCOUNT_NAME in account_map:
        selected_account_name = DEFAULT_ACCOUNT_NAME
    else:
        # Fallback to first
        selected_account_name = list(account_map.keys())[0]

    selected_account_id = account_map[selected_account_name]

    # --- Campaign Selection (Hidden Logic) ---
    campaigns = []
    campaigns = get_active_campaigns(selected_account_id)

    if not campaigns:
        st.info(f"No active or paused campaigns found for account: {selected_account_name}")
        st.stop()

    selected_campaign_id = None
    selected_campaign_name = None

    # Logic to select default campaign
    found_default_campaign = False
    for cmp in campaigns:
        if DEFAULT_CAMPAIGN_NAME_KEYWORD.lower() in cmp['name'].lower():
             selected_campaign_id = cmp['id']
             selected_campaign_name = cmp['name']
             found_default_campaign = True
             break
    
    if not found_default_campaign:
        active_cmps = [c for c in campaigns if c['status'] == 'ACTIVE']
        if active_cmps:
            selected_campaign_id = active_cmps[0]['id']
            selected_campaign_name = active_cmps[0]['name']
        else:
            selected_campaign_id = campaigns[0]['id']
            selected_campaign_name = campaigns[0]['name']

    # --- Removed Admin Settings Section as requested ---

    # --- Main Content ---

    # Fetch Summary Insights
    with st.spinner("Fetching Summary..."):
        insights = get_campaign_insights(selected_campaign_id)

    if not insights:
        st.warning("No data available for this campaign yet.")
    else:
        # Fetch Daily Insights for Charts
        with st.spinner("Fetching Daily Trends..."):
            daily_data_raw = get_daily_insights(selected_campaign_id)
        
        # Display Core Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        spend = float(insights.get('spend', 0))
        impressions = int(insights.get('impressions', 0))
        reach = int(insights.get('reach', 0))
        
        # Actions logic for landing page views
        actions = insights.get('actions', [])
        landing_page_views = get_landing_page_views(actions)
        
        with col1:
            st.metric("Total Spent", f"₹{spend:,.2f}")
        with col2:
            st.metric("People Reached", f"{reach:,}", help="Unique number of people who saw your ad.")
        with col3:
            st.metric("Total Views (Impressions)", f"{impressions:,}", help="Total number of times your ad was seen.")
        with col4:
            st.metric("Interested Audience", f"{landing_page_views:,}", help="Landing Page Views (Conversion Estimate)")

        # --- Daily Trends & Growth Curves ---
        if daily_data_raw:
            df = pd.DataFrame(daily_data_raw)
            df['date_start'] = pd.to_datetime(df['date_start'])
            df = df.sort_values('date_start')
            
            # Convert numeric columns
            numeric_cols = ['spend', 'impressions', 'reach']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Extract Daily Landing Page Views
            df['landing_page_views'] = df['actions'].apply(lambda x: get_landing_page_views(x) if isinstance(x, list) else 0)

            # Calculate Cumulative Growth
            df['Cumulative Spend'] = df['spend'].cumsum()
            df['Cumulative Reach'] = df['reach'].cumsum()
            df['Cumulative Impressions'] = df['impressions'].cumsum()
            df['Cumulative Interested Audience'] = df['landing_page_views'].cumsum()

            st.markdown("---")
            st.subheader("Daily Performance Trends")

            # Tabs for different views
            tab1, tab2 = st.tabs(["Daily Activity", "Cumulative Growth"])
            
            with tab1:
                col_c1, col_c2 = st.columns(2)
                
                with col_c1:
                    # Daily Reach & Impressions
                    chart_df = df.melt(id_vars=['date_start'], value_vars=['reach', 'impressions'], var_name='Metric', value_name='Count')
                    fig_daily_reach = px.line(chart_df, x='date_start', y='Count', color='Metric', 
                                            title="Daily Reach & Impressions",
                                            markers=True,
                                            text='Count')
                    fig_daily_reach.update_traces(textposition="top center")
                    st.plotly_chart(fig_daily_reach, use_container_width=True)
                
                with col_c2:
                    # Daily Spend
                    fig_daily_spend = px.bar(df, x='date_start', y='spend', 
                                           title="Daily Spend (₹)",
                                           color_discrete_sequence=['#ffca28'],
                                           text_auto='.2s')
                    fig_daily_spend.update_traces(textposition="outside")
                    st.plotly_chart(fig_daily_spend, use_container_width=True)

            with tab2:
                # Cumulative Growth
                growth_df = df.melt(id_vars=['date_start'], value_vars=['Cumulative Reach', 'Cumulative Impressions', 'Cumulative Interested Audience'], var_name='Metric', value_name='Total')
                fig_growth = px.line(growth_df, x='date_start', y='Total', color='Metric', 
                                   title="Total Growth Over Time",
                                   color_discrete_sequence=['#66bb6a', '#42a5f5', '#ef5350'],
                                   markers=True,
                                   text='Total')
                fig_growth.update_traces(textposition="top left")
                st.plotly_chart(fig_growth, use_container_width=True)


if __name__ == "__main__":
    main()
