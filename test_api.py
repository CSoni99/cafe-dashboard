import sys
import os
import toml
from utils.meta_api import init_api, get_ad_accounts, get_active_campaigns, get_campaign_insights

def check_secrets():
    secrets_path = ".streamlit/secrets.toml"
    if not os.path.exists(secrets_path):
        print("Secrets file not found.")
        return None
    
    with open(secrets_path, 'r') as f:
        config = toml.load(f)
        return config.get('general', {}).get('FACEBOOK_ACCESS_TOKEN')

def main():
    print("--- Testing Meta API Connection ---")
    
    token = check_secrets()
    if not token:
        print("Failed to load token.")
        return

    print("Initializing API...")
    if not init_api(token):
        print("Initialization failed.")
        return
    print("API Initialized.")

    print("\nFetching Ad Accounts...")
    accounts = get_ad_accounts()
    print(f"Found {len(accounts)} accounts.")
    for acc in accounts:
        print(f"- {acc['name']} (ID: {acc['id']})")

    if not accounts:
        print("No accounts found. Stopping.")
        return

    # Use first account for testing
    first_account_id = accounts[0]['id']
    print(f"\nFetching Active Campaigns for Account {first_account_id}...")
    campaigns = get_active_campaigns(first_account_id)
    print(f"Found {len(campaigns)} campaigns.")
    for cmp in campaigns:
        print(f"- {cmp['name']} (ID: {cmp['id']}, Status: {cmp['status']})")

    if not campaigns:
        print("No campaigns found. Stopping.")
        return

    # Use first campaign for insights
    first_campaign_id = campaigns[0]['id']
    print(f"\nFetching Insights for Campaign {first_campaign_id}...")
    insights = get_campaign_insights(first_campaign_id)
    if insights:
        print("Insights Data:")
        print(insights)
    else:
        print("No insights data returned.")

if __name__ == "__main__":
    main()
