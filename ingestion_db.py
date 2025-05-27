import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time

def ingest_db(df, table_name, engine):
    '''This function ingests the dataframe into the database in chunks'''
    df.to_sql(table_name, con=engine, if_exists="replace", index=False, chunksize=1000)


engine = create_engine("sqlite:///inventory.db")

logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)
def load_raw_data():
    '''This function loads CSVs into DataFrames and ingests them into DB'''
    start = time.time()
    folder = "D:\\study\\program\\data analysis project\\data\\data"
    
    for file in os.listdir(folder):
        if file.endswith(".csv"):
            file_path = os.path.join(folder, file)
            try:
                df = pd.read_csv(file_path, low_memory=False)
                df = df.convert_dtypes()  # Optional but optimizes memory

                logging.info(f"Ingesting {file} with shape {df.shape}")
                ingest_db(df, file[:-4], engine)

            except Exception as e:
                logging.error(f"Failed to ingest {file}: {str(e)}")

    end = time.time()
    total_time = (end - start) / 60
    logging.info("--------- Ingestion complete ---------")
    logging.info(f"Total time taken: {total_time:.2f} minutes")

if __name__ == "__main__":
    load_raw_data()