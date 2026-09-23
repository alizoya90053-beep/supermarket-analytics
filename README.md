# SuperMarket Sales Analytics

A complete data analytics project built with **Python**, **Pandas**, and **Streamlit** for interactive visualisation of supermarket sales data.

---

## Project Structure

```
supermarket_analysis/
├── app.py                  # Streamlit frontend (run this)
├── requirements.txt        # Python dependencies
├── data/
│   └── supermarket_sales.csv
├── src/
│   ├── __init__.py
│   ├── data_loader.py      # Load, clean & validate dataset
│   └── analysis.py         # Group-by summaries & KPI functions
└── outputs/                # (optional) saved chart exports
```

---

## Features

| # | Feature |
|---|---------|
| 1 | **Load & Clean** — CSV loading with whitespace trimming, type casting, duplicate + missing-value removal |
| 2 | **Data Quality Report** — Missing values, invalid categories, Sales recalculation check |
| 3 | **Sales = Qty × Unit Price** — Enforced and corrected automatically |
| 4 | **Group Summaries** — Totals, counts, averages by Branch / Product / Customer / Payment / Time |
| 5 | **Interactive Charts** — 20+ Plotly charts with hover, zoom, and download |
| 6 | **Business Insights** — Automated insight cards with top performers, peak hours, loyalty analysis |
| 7 | **Sidebar Filters** — Filter by Branch, Product, Gender, Customer Type, Payment, Date Range |

---

## Setup & Run

```bash
# 1 — Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 2 — Install dependencies
pip install -r requirements.txt

# 3 — Launch the app (from inside supermarket_analysis/)
streamlit run app.py
```

The browser will open automatically at `http://localhost:8501`.

---

## Dashboard Tabs

| Tab | Content |
|-----|---------|
| 📊 Overview | KPI cards, monthly & daily sales bar charts, raw data preview |
| 🧹 Data Quality | Cleaning report, missing values, numeric stats, data types |
| 🏪 Branch Analysis | Sales / transactions / rating / gross income per branch + heatmap |
| 📦 Product Lines | Revenue, quantity, rating, unit price per product line + gender split |
| 👤 Customers | Member vs Normal + Gender breakdown — sales, ratings, avg transaction |
| 💳 Payments | Share of each payment method, transaction counts, avg sale |
| 📅 Time Trends | Monthly trend, day-of-week, peak hour analysis |
| 💡 Business Insights | Automated insight cards + branch scorecard + top 10 transactions |

---

## Dataset

- **Source:** SuperMarket Analysis.csv  
- **Rows:** 1,000 transactions  
- **Columns:** 17  
- **Period:** January – March 2019  
- **Branches:** Alex (Yangon), Cairo (Mandalay), Giza (Naypyitaw)
