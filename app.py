import streamlit as st
import pandas as pd
import requests
import datetime
import plotly.express as px

# --- Configuration ---
st.set_page_config(
    page_title="US National Debt Tracker",
    page_icon="🇺🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# US Population (approximate - update as needed)
US_POPULATION = 335_000_000

# --- API & Data Logic ---
@st.cache_data(ttl="24h")
def fetch_debt_data(date_trigger, days=365):
    """
    Fetches US National Debt data for the specified number of days.
    The `date_trigger` argument ensures the cache is invalidated daily.
    """
    url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/debt_to_penny"
    params = {
        "sort": "-record_date",
        "page[size]": days,
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
    # --- Sidebar ---
    with st.sidebar:
        st.image("https://em-content.zobj.net/source/twitter/53/flag-for-united-states_1f1fa-1f1f8.png", width=50)
        st.title("Debt Tracker")
        st.caption("Official Data")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📈 Analysis", "📄 Reports"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.subheader("DATE RANGE")
        
        # Date range selector
        date_range = st.selectbox(
            "Select Range",
            ["1 Year", "10 Years", "All Time"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # Download button
        st.button("⬇️ Download Report", use_container_width=True)
    
    # --- Main Content ---
    st.title("🇺🇸 US National Debt Tracker")

    # Fetch Data (pass today's date to handle cache invalidation)
    today = datetime.date.today()
    
    # Determine days to fetch based on date range
    days_map = {"1 Year": 365, "10 Years": 3650, "All Time": 10000}
    days_to_fetch = days_map.get(date_range, 365)
    
    df = fetch_debt_data(today, days=days_to_fetch)

    if df.empty:
        st.warning("No data available. Please try again later.")
        return

    # --- Key Metrics ---
    # Get latest and previous day data
    latest_record = df.iloc[0]
    
    # Check if we have at least 2 records for delta calculation
    if len(df) >= 2:
        previous_record = df.iloc[1]
        delta_24h = latest_record["tot_pub_debt_out_amt"] - previous_record["tot_pub_debt_out_amt"]
        pct_change_24h = (delta_24h / previous_record["tot_pub_debt_out_amt"]) * 100
    else:
        delta_24h = None
        pct_change_24h = None

    current_debt = latest_record["tot_pub_debt_out_amt"]
    last_updated = latest_record["record_date"].strftime("%B %d, %Y, %I:%M %p EST")
    
    # Calculate debt per citizen
    debt_per_citizen = current_debt / US_POPULATION
    
    # Calculate 10-year change if we have enough data
    if len(df) >= 365:
        oldest_record = df.iloc[-1]
        debt_10y_ago = oldest_record["tot_pub_debt_out_amt"]
        pct_change_10y = ((current_debt - debt_10y_ago) / debt_10y_ago) * 100
    else:
        pct_change_10y = None

    st.caption(f"Last Updated: {last_updated}")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        debt_trillions = current_debt / 1_000_000_000_000
        delta_billions = delta_24h / 1_000_000_000 if delta_24h is not None else None
        delta_str = f"+${delta_billions:.1f}B" if delta_billions is not None else None
        st.metric(
            label="Total Public Debt",
            value=f"${debt_trillions:.1f}T",
            delta=delta_str,
            delta_color="inverse"
        )
        if pct_change_24h is not None:
            st.caption(f"↑ +{pct_change_24h:.2f}%")
    
    with col2:
        delta_str_24h = f"+${delta_24h / 1_000_000_000:.1f}B" if delta_24h is not None else None
        st.metric(
            label="24h Change",
            value=delta_str_24h if delta_str_24h else "N/A",
            delta=f"+{pct_change_24h:.1f}%" if pct_change_24h is not None else None,
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Debt per Citizen",
            value=f"${debt_per_citizen:,.0f}",
            delta=f"+{pct_change_24h:.2f}%" if pct_change_24h is not None else None,
            delta_color="inverse"
        )

    # --- Visualization ---
    range_label = date_range.replace(" ", "-")
    st.subheader(f"{range_label} Debt Trend")
    
    # Add 10Y change indicator if available
    if pct_change_10y is not None:
        col_chart1, col_chart2 = st.columns([3, 1])
        with col_chart2:
            st.metric(
                label="",
                value=f"${debt_trillions:.1f}T",
                delta=f"Last 10Y: ↑ +{pct_change_10y:.1f}%",
                delta_color="inverse"
            )
    
    # Create a Plotly area chart
    df_sorted = df.sort_values(by="record_date", ascending=True)
    fig = px.area(
        df_sorted, 
        x="record_date", 
        y="tot_pub_debt_out_amt",
        labels={"record_date": "Date", "tot_pub_debt_out_amt": "Total Debt ($)"},
        template="plotly_dark"
    )
    
    # Customize the chart to look sleek
    fig.update_traces(
        line_color='#FF4B4B',
        fillcolor='rgba(255, 75, 75, 0.3)',
        line_width=2
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- Data Table ---
    st.markdown("---")
    
    # Prepare table with daily changes
    df_display = df.copy()
    df_display = df_display.sort_values(by="record_date", ascending=False)
    df_display["daily_change"] = -df_display["tot_pub_debt_out_amt"].diff(-1)
    
    # Rename columns for display
    df_display = df_display.rename(columns={
        "record_date": "DATE",
        "tot_pub_debt_out_amt": "TOTAL DEBT",
        "daily_change": "DAILY CHANGE"
    })
    
    # Format the DATE column
    df_display["DATE"] = df_display["DATE"].dt.strftime("%Y-%m-%d")
    
    st.subheader("Recent Data")
    
    # Display top 10 records
    st.dataframe(
        df_display.head(10),
        use_container_width=True,
        hide_index=True,
        column_config={
            "DATE": st.column_config.TextColumn("DATE", width="medium"),
            "TOTAL DEBT": st.column_config.NumberColumn(
                "TOTAL DEBT",
                format="$%.2f",
                width="large"
            ),
            "DAILY CHANGE": st.column_config.NumberColumn(
                "DAILY CHANGE",
                format="%+.2f",
                width="medium"
            )
        }
    )
    
    with st.expander("View All Data"):
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "DATE": st.column_config.TextColumn("DATE"),
                "TOTAL DEBT": st.column_config.NumberColumn("TOTAL DEBT", format="$%.2f"),
                "DAILY CHANGE": st.column_config.NumberColumn("DAILY CHANGE", format="%+.2f")
            }
        )

    # --- Footer ---
    st.markdown("---")
    st.caption("Data Source: U.S. Treasury Fiscal Data API")

if __name__ == "__main__":
    main()
