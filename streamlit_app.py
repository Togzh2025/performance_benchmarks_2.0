import streamlit as st
import pandas as pd

st.title("📊 Performance Benchmarks")

# 📤 File Upload
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    # Read CSV
    df = pd.read_csv(uploaded_file)

    # ✅ Standardize Column Names (Case-insensitive mapping)
    df.columns = df.columns.str.strip().str.lower()  # Normalize column names

    column_mapping = {
        'campaign name': 'campaign',
        'clicks': 'link clicks',
        'conversions': 'results',
        'leads': 'leads',
        'total spent': 'amount spent (usd)'
    }

    # Rename columns if they exist in the dataset
    df.rename(columns={col: standard for col, standard in column_mapping.items() if col in df.columns}, inplace=True)

    # ✅ User-defined Campaign Grouping
    st.subheader("🔧 Customize Campaign Grouping")
    user_keywords = st.text_area(
        "Enter keywords for campaign grouping based on campaign names (comma-separated)", 
        "ungatedcontent, gatedcontent, interactivedemo, talktosales"
    )

    # Convert user input into a dictionary
    keyword_dict = {kw.strip().lower(): kw.strip().capitalize() for kw in user_keywords.split(",") if kw.strip()}

    # 🏷️ Group Campaigns Based on User Input
    def group_campaign(campaign_name):
        if pd.isna(campaign_name):  # Handle missing values
            return 'Other'
        campaign_name = str(campaign_name).lower()
        for keyword, group_name in keyword_dict.items():
            if keyword in campaign_name:
                return group_name
        return 'Other'

    if 'campaign' in df.columns:
        df['campaign'] = df['campaign'].apply(group_campaign)
    else:
        st.error("🚨 Error: 'Campaign' column is missing. Cannot group campaigns.")
        st.stop()

# ✅ Calculate Metrics (Now correctly defined outside of `if uploaded_file:`)
def calculate_metrics(group):
    # Convert values to numeric safely
    impressions = pd.to_numeric(group.get('impressions', pd.Series([0])), errors='coerce').fillna(0).sum()
    clicks = pd.to_numeric(group.get('link clicks', pd.Series([0])), errors='coerce').fillna(0).sum()
    cost = pd.to_numeric(group.get('amount spent (usd)', pd.Series([0])), errors='coerce').fillna(0).sum()
    conversions = pd.to_numeric(group.get('results', pd.Series([0])), errors='coerce').fillna(0).sum()
    leads = pd.to_numeric(group.get('leads', pd.Series([0])), errors='coerce').fillna(0).sum()

    # Calculate metrics safely
    ctr = (clicks / impressions) * 100 if impressions > 0 else 0
    cpc = cost / clicks if clicks > 0 else 0
    cpm = cost / (impressions / 1000) if impressions > 0 else 0
    cpa = cost / conversions if conversions > 0 else 0
    cplead = cost / leads if leads > 0 else 0
    conversion_rate = (conversions / clicks) * 100 if clicks > 0 else 0

    # Return formatted metrics
    return pd.Series({
        'Spend ($)': f"${cost:,.2f}",
        'Impr.': f"{impressions:,.0f}",
        'Clicks': f"{clicks:,.0f}",
        'CTR (%)': f"{ctr:.2f}%",
        'CPC ($)': f"${cpc:,.2f}",
        'CPM ($)': f"${cpm:,.2f}",
        'Conversions': f"{conversions:,.0f}",
        'CPA ($)': f"${cpa:,.2f}",
        'Leads': f"{leads:,.0f}",
        'cpLead ($)': f"${cplead:,.2f}",
        'Conversion Rate (%)': f"{conversion_rate:.2f}%"
    })

if uploaded_file:
    if 'campaign' in df.columns:
        metrics_df = df.groupby('campaign').apply(calculate_metrics).reset_index()
    else:
        st.error("🚨 Error: 'Campaign' column is missing. Cannot calculate metrics.")
        st.stop()

    # 📝 Display Data
    st.subheader("📊 Campaign Performance Benchmarks")
    st.dataframe(metrics_df)

    # 💾 Download CSV
    csv = metrics_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results as CSV", csv, "campaign_metrics.csv", "text/csv")

    st.success("✅ Analysis Complete! Download your CSV file above.")
