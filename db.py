import sqlite3
from http import HTTPStatus
from http.client import responses
from pathlib import Path
from dotenv import dotenv_values

import pandas
import requests

DATABASE_ROOT = Path("./db")
DATABASE_FILE = DATABASE_ROOT / Path("mcd_crashes.db")

config = dotenv_values(".env")
CRASH_URL = config["CRASH_URL"]
POPULATION_URL = config["POPULATION_URL"]
CRASH_TABLE_NAME = "mcd_crash"
POPULATION_TABLE_NAME = "mcd_population"

class GenerateDatabase():
    """
    Create and populate a local SQL database with crash data fetched from
    PennDOT's website.
    """
    def exec(self):
        self._init_folders()
        self._download_data()
        # self._unzip_data()
        self._load_data_into_db()
        self._print_table_names()

    def _init_folders(self):
        DATABASE_ROOT.mkdir(exist_ok=True)
        DATABASE_FILE.unlink(missing_ok=True)

    def _download_data(self) -> None:
        self._download_csv(CRASH_URL, CRASH_TABLE_NAME)
        self._download_csv(POPULATION_URL, POPULATION_TABLE_NAME)

    def _download_csv(self, url: str, file_name: str) -> None:
        print(f"Attempting download from {url=} ... ", end='')
        r = requests.get(url)
        print(f"{r.status_code} {responses[r.status_code]}")
        assert r.status_code == HTTPStatus.OK, f"{r.status_code=}"
        open(f"{DATABASE_ROOT}/{file_name}.csv", 'wb').write(r.content)

    def _load_data_into_db(self):
        with sqlite3.connect(DATABASE_FILE) as conn:
            for csvfile in DATABASE_ROOT.iterdir():
                if csvfile.suffix != ".csv":
                    continue
                print(f"Loading {csvfile} into db...")
                df = pandas.read_csv(csvfile)
                df.columns = df.columns.str.replace(' ', '_')
                df.to_sql(csvfile.stem, conn, if_exists='append', index=False)
                csvfile.unlink()

    def _print_table_names(self):
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            print(cursor.fetchall())

