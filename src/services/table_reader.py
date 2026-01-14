from abc import ABC, abstractmethod
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class TableReader(ABC):
    DEFAULT_DATE_FORMAT = "%d.%m.%Y"

    def __init__(self, date_format: str | None = None):
        self.date_format = date_format or self.DEFAULT_DATE_FORMAT

    @abstractmethod
    def read(self) -> pd.DataFrame:
        pass

    def _parse_date_column(self, series: pd.Series) -> pd.Series:
        return pd.to_datetime(series, errors="coerce", format=self.date_format).apply(
            lambda x: x.date() if pd.notna(x) else None
        )

    def _parse_value_column(self, series: pd.Series) -> pd.Series:
        return pd.to_numeric(series, errors="coerce").fillna(0).astype("int64")

    def _normalize_table(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or df.shape[1] < 2:
            return df

        df = df.copy()
        df[df.columns[0]] = self._parse_date_column(df.iloc[:, 0])
        df[df.columns[1]] = self._parse_value_column(df.iloc[:, 1])

        return df


class GoogleSheetsReader(TableReader):
    DEFAULT_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    DEFAULT_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")

    def __init__(
        self,
        sheet_id: str,
        cred_path: str | None = None,
        date_format: str | None = None,
        scopes: list[str] | None = None,
    ):
        super().__init__(date_format)
        self.sheet_id = sheet_id
        self.scopes = scopes or self.DEFAULT_SCOPES
        self.cred_path = cred_path or self.DEFAULT_CREDENTIALS_PATH
        
        if not self.cred_path:
            raise ValueError("cred_path не указан и GOOGLE_SHEETS_CREDENTIALS_PATH не установлен")
        
        self.creds = Credentials.from_service_account_file(
            self.cred_path, scopes=self.scopes
        )
        self.client = gspread.authorize(self.creds)

    def get_sheet(self, sheet_id: str) -> gspread.Spreadsheet:
        return self.client.open_by_key(sheet_id)

    def _get_all_raws(self, sheet: gspread.Spreadsheet) -> list:
        return sheet.sheet1.get_all_values()

    def _create_dataframe(self, rows: list) -> pd.DataFrame:
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows[1:], columns=rows[0])

    def read(self) -> pd.DataFrame:
        sheet = self.get_sheet(self.sheet_id)
        rows = self._get_all_raws(sheet)
        df = self._create_dataframe(rows)
        return self._normalize_table(df)


class ExcelReader(TableReader):
    def __init__(self, file_path: str, date_format: str | None = None):
        super().__init__(date_format)
        self.file_path = file_path

    def _read_excel_file(self) -> pd.DataFrame:
        return pd.read_excel(self.file_path, parse_dates=False)

    def read(self) -> pd.DataFrame:
        df = self._read_excel_file()
        return self._normalize_table(df)


# # Использование
# if __name__ == "__main__":
#     sheet_id = os.getenv("GOOGLE_SHEET_ID")
#     excel_path = os.getenv("EXCEL_FILE_PATH")
    
#     if sheet_id:
#         g_reader = GoogleSheetsReader(sheet_id=sheet_id)
#         g_data = g_reader.read()
#         print("Google Sheets:")
#         print(g_data)
#         print(g_data.dtypes)
#         if not g_data.empty:
#             print(f"Value type check: {type(g_data.iloc[0, 1])}, {type(g_data.iloc[1, 0])}")
    
#     if excel_path:
#         e_reader = ExcelReader(file_path=excel_path)
#         e_data = e_reader.read()
#         print("\nExcel:")
#         print(e_data)
#         print(e_data.dtypes)
#         if not e_data.empty:
#             print(f"Value type check: {type(e_data.iloc[0, 1])}, {type(e_data.iloc[1, 0])}")

#     g_data = g_reader.read()
#     e_data = e_reader.read()

#     print("Google Sheets:")
#     print(g_data)
#     print(g_data.dtypes)
#     print(f"Value type check: {type(g_data.iloc[0, 1])}, {type(g_data.iloc[1, 0])}")

#     print("\nExcel:")
#     print(e_data)
#     print(e_data.dtypes)
#     print(f"Value type check: {type(e_data.iloc[0, 1])}, {type(e_data.iloc[1, 0])}")

