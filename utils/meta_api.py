from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.user import User
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign

def init_api(access_token):
    """Initialize the Facebook Ads API."""
    try:
        FacebookAdsApi.init(access_token=access_token)
        return True
    except Exception as e:
        print(f"Error initializing API: {e}")
        return False

def get_ad_accounts():
    """Fetch ad accounts for the current user."""
    try:
        user = User(fbid='me')
        accounts = user.get_ad_accounts(fields=['name', 'account_id', 'account_status'])
        return [
            {
                'name': account['name'],
                'id': account['account_id'],
                'status': account['account_status']
            }
            for account in accounts
        ]
    except Exception as e:
        print(f"Error fetching ad accounts: {e}")
        return []

def get_active_campaigns(account_id):
    """Fetch active campaigns for a given account."""
    try:
        account = AdAccount(f'act_{account_id}')
        campaigns = account.get_campaigns(
            fields=['name', 'id', 'status', 'objective'],
            params={'effective_status': ['ACTIVE', 'PAUSED']} # Fetch Active and Paused to show more context
        )
        return [
            {
                'name': cmp['name'],
                'id': cmp['id'],
                'status': cmp['status'],
                'objective': cmp.get('objective', 'N/A')
            }
            for cmp in campaigns
        ]
    except Exception as e:
        print(f"Error fetching campaigns: {e}")
        return []

def get_campaign_insights(campaign_id):
    """Fetch insights for a specific campaign."""
    try:
        campaign = Campaign(campaign_id)
        insights = campaign.get_insights(
            fields=[
                'impressions',
                'reach',
                'spend',
                'frequency',
                'cpc',
                'ctr',
                'actions', # For detailed conversions if needed
            ],
            params={'date_preset': 'maximum'} # Get lifetime data by default
        )
        if insights:
            return insights[0] # Return the first (summary) object
        return None
    except Exception as e:
        print(f"Error fetching insights: {e}")
        return None

def get_daily_insights(campaign_id):
    """Fetch daily insights for a specific campaign to plot trends."""
    try:
        campaign = Campaign(campaign_id)
        insights = campaign.get_insights(
            fields=[
                'date_start',
                'impressions',
                'reach',
                'spend',
                'clicks',
                'actions',
            ],
            params={
                'date_preset': 'maximum',
                'time_increment': 1 # Breakdown by day
            }
        )
        return [dict(i) for i in insights]
    except Exception as e:
        print(f"Error fetching daily insights: {e}")
        return []
