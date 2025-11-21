import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.express as px

# --- Configuration ---
st.set_page_config(
    page_title="US National Debt Tracker",
    page_icon="🇺🇸",
    layout="wide"
)

# --- API & Data Logic ---
@st.cache_data(ttl="24h")
def fetch_debt_data(date_trigger):
    """
    Fetches the last 365 days of US National Debt data.
    The `date_trigger` argument ensures the cache is invalidated daily.
    """
    url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny"
    params = {
        "sort": "-record_date",
        "page[size]": 365,
        "fields": "record_date,tot_pub_debt_out_amt"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "data" not in data:
            st.error("API returned unexpected format.")
            return pd.DataFrame()
            
        df = pd.DataFrame(data["data"])
        
        # Data Cleaning
        df["record_date"] = pd.to_datetime(df["record_date"])
        df["tot_pub_debt_out_amt"] = df["tot_pub_debt_out_amt"].astype(float)
        
        # Sort just in case API didn't
        df = df.sort_values(by="record_date", ascending=False)
        
        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from Treasury API: {e}")
        return pd.DataFrame()

# --- Main App ---
def main():
    st.title("🇺🇸 US National Debt Tracker")
    st.markdown("Tracking the Total Public Debt Outstanding of the United States.")
    st.markdown("---")

    # Fetch Data (pass today's date to handle cache invalidation)
    today = datetime.date.today()
    df = fetch_debt_data(today)

    if df.empty:
        st.warning("No data available. Please try again later.")
        return

    # --- Key Metrics ---
    # Get latest and previous day data
    latest_record = df.iloc[0]
    
    # Check if we have at least 2 records for delta calculation
    if len(df) >= 2:
        previous_record = df.iloc[1]
        delta = latest_record["tot_pub_debt_out_amt"] - previous_record["tot_pub_debt_out_amt"]
    else:
        delta = None

    current_debt = latest_record["tot_pub_debt_out_amt"]
    last_updated = latest_record["record_date"].strftime("%B %d, %Y")

    st.caption(f"Last Updated: {last_updated}")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Public Debt",
            value=f"${current_debt:,.2f}",
            delta=f"${delta:,.2f}" if delta is not None else None,
            delta_color="inverse" # Red if debt goes up (bad), Green if down (good)
        )

    # --- Visualization ---
    st.subheader("1-Year Debt Trend")
    
    # Create a Plotly line chart
    fig = px.line(
        df, 
        x="record_date", 
        y="tot_pub_debt_out_amt",
        labels={"record_date": "Date", "tot_pub_debt_out_amt": "Total Debt ($)"},
        template="plotly_dark"
    )
    
    # Customize the chart to look sleek
    fig.update_traces(line_color='#FF4B4B', line_width=3)
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- Data Table ---
    with st.expander("View Raw Data"):
        st.dataframe(df.style.format({"tot_pub_debt_out_amt": "${:,.2f}"}))

    # --- Footer ---
    st.markdown("---")
    st.caption("Data Source: U.S. Treasury Fiscal Data API")

if __name__ == "__main__":
    main()
