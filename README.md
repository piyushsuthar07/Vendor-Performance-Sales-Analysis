# Vendor-Performance-Sales-Analysis
This project helps businesses understand which vendors or brands are performing best by analyzing sales, purchases, freight, and profits using SQL and Python.
## 📊 What It Does
- Imports CSVs to SQLite DB
- Generates a summary of vendor-wise metrics
- Cleans and transforms data
- Performs EDA to find insights like:
  - Top vendors by sales
  - Brands with high margin but low sales
  - Inventory turnover & locked capital
  - Statistical differences in vendor performance

## 🛠️ Technologies Used
- Python (pandas, seaborn, matplotlib, scipy)
- SQLite + SQLAlchemy
- Logging

## 🔄 How to Run
1. Place CSVs in `data/data/`
2. Run `ingestion_db.py`
3. Run `get_vendor_summary1.py`
4. Run `vendor_performance_analysis.py`

## 📈 Business Use Cases
- Vendor selection
- Promotional targeting
- Inventory management
- Capital optimization

## 📗 Output
- Database: `vendor_sales_summary1` table
- Visual insights (plots, charts)
