import pandas as pd
import sqlite3

conn = sqlite3.connect("inventory.db")

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type = 'table' ", conn)
print(tables)

for table in tables ["name"]:
    print('-'*10 , f"{table}", '-'*10)
    count = pd.read_sql(f"SELECT COUNT(*) as COUNT FROM {table}", conn)["COUNT"].values[0]
    print("Count of records:", count)
    print(pd.read_sql(f"SELECT * FROM {table} limit 5", conn))


print(pd.read_sql("SELECT * FROM purchase_prices WHERE VendorNumber = 4466", conn))

print(pd.read_sql("SELECT * FROM vendor_invoice WHERE VendorNumber = 4466", conn))

df=pd.read_sql("SELECT * FROM sales", conn)
print(df.columns.tolist())

print(pd.read_sql("SELECT * FROM sales WHERE VendorNo = 4466", conn))


purchase = pd.read_sql("SELECT * FROM purchases WHERE VendorNumber = 4466", conn)
print(purchase.shape)

grouped = purchase.groupby(["Brand","PurchasePrice"])[["Quantity","Dollars"]].sum()
print(grouped)

print("ends here")

sales = pd.read_sql("SELECT * FROM sales WHERE VendorNo = 4466", conn)
grouped2 = sales.groupby('Brand')[['SalesDollars','SalesPrice','SalesQuantity']].sum()
print(grouped2)

vendor_inovoice = pd.read_sql("SELECT * FROM vendor_invoice", conn)
print(vendor_inovoice.columns.tolist())

freight_summary = pd.read_sql("SELECT VendorNumber, SUM(Freight) AS freightcost FROM vendor_invoice GROUP BY VendorNumber", conn)
print(freight_summary)

print("start here")

import time
import pandas as pd

start = time.time()

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

end = time.time()
print(f"Query executed in {end - start:.2f} seconds")

Vendor_sales_summary["Volume"] = Vendor_sales_summary["Volume"].astype('float64')
Vendor_sales_summary.fillna(0, inplace=True)
Vendor_sales_summary["VendorName"] = Vendor_sales_summary["VendorName"].str.strip()
#adding new lines for analysis

Vendor_sales_summary["GrossProfit"] = Vendor_sales_summary["TotalSalesDollars"] - Vendor_sales_summary["TotalPurchaseDollars"]
Vendor_sales_summary["ProfitMargin"] = Vendor_sales_summary["GrossProfit"]/Vendor_sales_summary["TotalSalesDollars"]
Vendor_sales_summary["StockTurnover"] = Vendor_sales_summary["TotalSalesQuantity"]/Vendor_sales_summary["TotalPurchaseQuantity"]
Vendor_sales_summary["SalestoPurchaseratio"] = Vendor_sales_summary["TotalSalesDollars"]/Vendor_sales_summary["TotalPurchaseDollars"]


print(Vendor_sales_summary.head())
print(Vendor_sales_summary.columns.to_list())
print(Vendor_sales_summary.dtypes)
print(Vendor_sales_summary.isnull().sum())
print(Vendor_sales_summary["VendorName"].unique())

#now we create table and stor all new column and data

cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS vendor_sales_summary1")
cursor.execute("""CREATE TABLE vendor_sales_summary1 (
               VendorNumber INT,
               VendorName VARCHAR(100),
               Brand INT,
               Description VARCHAR(100),
               PurchasePrice DECIMAL(10,2),
               ActualPrice DECIMAL(10,2),
               Volume,
               TotalPurchaseQuantity    INT,
               TotalPurchaseDollars DECIMAL(15,2),
               TotalSalesQuantity   INT,
               TotalSalesDollars    DECIMAL(15,2),
               TotalSalesPrice  DECIMAL(15,2),
               TotalExciseTax   DECIMAL(15,2),
               FreightCost  DECIMAL(15,2),
               GrossProfit  DECIMAL(15,2),
               ProfitMargin DECIMAL(15,2),
               StockTurnover    DECIMAL(15,2),
               SalestoPurchaseratio DECIMAL(15,2),
               PRIMARY KEY(vendorNumber, Brand)
);

""")
Vendor_sales_summary.to_sql('vendor_sales_summary1', conn, if_exists = "replace", index=False)

result = pd.read_sql("SELECT * FROM vendor_sales_summary1", conn)

print(result)