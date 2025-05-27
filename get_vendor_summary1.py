import sqlite3
import pandas as pd
import logging
from ingestion_db import ingest_db

from exploring import Vendor_sales_summary

logging.basicConfig(
    filename="logs/get_vendor_summary1.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

def create_vendor_summary1(conn):
    Vendor_sales_summary = pd.read_sql("""
WITH FreightSummary AS (
    SELECT
        VendorNumber,
        SUM(Freight) AS FreightCost
    FROM vendor_invoice
    GROUP BY VendorNumber
), 
PurchaseSummary AS (
    SELECT
        p.VendorNumber,
        p.VendorName,
        p.Brand,
        p.Description,
        p.PurchasePrice,
        pp.Volume,
        pp.Price AS ActualPrice,
        SUM(p.Quantity) AS TotalPurchaseQuantity,
        SUM(p.Dollars) AS TotalPurchaseDollars
    FROM purchases p
    JOIN purchase_prices pp
        ON p.Brand = pp.Brand
    WHERE p.PurchasePrice > 0
    GROUP BY p.VendorNumber, p.VendorName, p.Brand, p.Description, p.PurchasePrice, pp.Volume, pp.Price
),
SalesSummary AS (
    SELECT
        VendorNo,
        Brand,
        SUM(SalesDollars) AS TotalSalesDollars,
        SUM(SalesPrice) AS TotalSalesPrice,
        SUM(SalesQuantity) AS TotalSalesQuantity,
        SUM(ExciseTax) AS TotalExciseTax
    FROM sales
    GROUP BY VendorNo, Brand
)

SELECT
    ps.VendorNumber,
    ps.VendorName,
    ps.Brand,
    ps.Description,
    ps.PurchasePrice,
    ps.ActualPrice,
    ps.Volume,
    ps.TotalPurchaseQuantity,                           
    ps.TotalPurchaseDollars, 
    ss.TotalSalesQuantity,
    ss.TotalSalesDollars,
    ss.TotalSalesPrice,
    ss.TotalExciseTax,
    fs.FreightCost
FROM PurchaseSummary ps
LEFT JOIN SalesSummary ss
    ON ps.VendorNumber = ss.VendorNo
    AND ps.Brand = ss.Brand
LEFT JOIN FreightSummary fs
    ON ps.VendorNumber = fs.VendorNumber
ORDER BY ps.TotalPurchaseDollars DESC
""", conn)
    return Vendor_sales_summary

def clean_data(df):
    """this function help to clean the data"""
    #changing datatype to float
    df["Volume"] = df["Volume"].astype("float")

    #filling missing value with 0
    df.fillna(0, inplace=True)

    #removing spaces from categorical columns
    df["VendorName"] = df["VendorName"].str.strip()
    df["Description"] = df["Description"].str.strip()

    #Creating new column for better analysis
    df["GrossProfit"] = df["TotalSalesDollars"] - df["TotalPurchaseDollars"]
    df["ProfitMargin"] = df["GrossProfit"]/df["TotalSalesDollars"]
    df["StockTurnover"] = df["TotalSalesQuantity"]/df["TotalPurchaseQuantity"]
    df["SalestoPurchaseratio"] = df["TotalSalesDollars"]/df["TotalPurchaseDollars"]

    return df

if __name__ =="__main__":
    #creating database connection
    conn = sqlite3.connect("inventory.db")

    logging.info("creating vendor summary table......")
    summary_df = create_vendor_summary1(conn)
    logging.info(summary_df.head())

    logging.info("cleaning data....")
    clean_df = clean_data(summary_df)
    logging.info(clean_df.head())

    logging.info("investing data...")
    ingest_db(clean_df, "vendor_sales_summary1", conn)
    logging.info("complete")


