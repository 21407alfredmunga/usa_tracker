# 🇺🇸 US National Debt Tracker

A real-time Streamlit dashboard that tracks the total public debt outstanding of the United States.

## Features

- **Live Data**: Fetches the latest debt figures from the U.S. Treasury Fiscal Data API
- **Historical Trends**: Visualizes debt changes over the past year
- **Daily Updates**: Shows day-over-day debt changes with color-coded metrics
- **Interactive Chart**: Plotly-powered visualization for exploring debt trends
- **Raw Data Access**: View and explore the underlying dataset

## Screenshot

The dashboard displays:
- Current total public debt amount
- Daily change in debt (with inverse color coding)
- Interactive 1-year trend chart
- Expandable raw data table

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd usa_tracker
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

## Requirements

- Python 3.7+
- streamlit
- pandas
- requests
- plotly

## Data Source

Data is sourced from the [U.S. Treasury Fiscal Data API](https://fiscaldata.treasury.gov/), specifically the "Debt to the Penny" dataset which provides daily snapshots of the total public debt outstanding.

## How It Works

1. The app fetches the last 365 days of debt data from the Treasury API
2. Data is cached for 24 hours to minimize API calls
3. The latest debt figure is displayed with the change from the previous day
4. A line chart shows the debt trend over the past year
5. Raw data is available in an expandable table

## License

This project is open source and available under the MIT License.

## Contributing

Contributions, issues, and feature requests are welcome!

---

*Note: This dashboard is for informational purposes only.*
