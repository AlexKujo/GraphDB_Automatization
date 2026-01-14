import pandas as pd
from datetime import date

# Импорты GoogleSheetsReader и ExcelReader используются только в блоке __main__
# поэтому оставляем их там

class TableAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        # self._validate_dataframe()
    
    @property
    def dates(self):
        return self.df.iloc[:, 0]
    
    @property
    def values(self):
        return self.df.iloc[:, 1]
    
       
    def get_min_max_date(self) -> tuple[date, date]:
        """Возвращает кортеж (min_date, max_date)"""  
        
        valid_dates = self.dates[self.dates.notna()]
        return (min(valid_dates), max(valid_dates))
    
    def sum_by_period(self, date_from: date, date_to: date) -> int:
        # date_from_parsed = datetime.strptime(date_from,DATE_FORMAT)
        # date_to_parsed = datetime.strptime(date_to,DATE_FORMAT)
        mask = (self.dates >= date_from) & (self.dates <= date_to)
        return int(self.values[mask].sum())
    


# # Использование
# if __name__ == "__main__":
#     from src.services.table_reader import ExcelReader
    
#     # reader = GoogleSheetsReader(
#     #     cred_path='googlesheets_credentials.json',
#     #     sheet_id='1p8PaZ8cDcrEUkDMrzJ8_gEVMSqD_7ruDw_wAEzXkZZo'
#     # )
#     reader = ExcelReader(file_path=r"data\test_table.xlsx")
#     df = reader.read()
    
#     analyzer = TableAnalyzer(df)
#     min_date, max_date = analyzer.get_min_max_date()
    
#     print(f"Date range: {min_date} - {max_date}")