from src.services.table_reader import GoogleSheetsReader, ExcelReader
from src.services.table_analyzer import TableAnalyzer
from datetime import datetime
from src.services.graph_service import ImageNode, GraphDBService
from src.services.image_generator import ImageGen
import os


class TableController:
    def __init__(self):
        self.table = None
        self.source_info = None
        self.analyzer = None
        self.current_sum = None
        self.image_generated = False
        self.image_node = None
        self._graph_service = None
        self._image_gen = None

    def load_from_google_sheets(self, cred_path: str, sheet_id: str) -> None:
        """Загружает таблицу из Google Sheets"""
        reader = GoogleSheetsReader(cred_path=cred_path, sheet_id=sheet_id)
        self.table = reader.read()
        self.analyzer = TableAnalyzer(self.table)
        self.source_info = f"Google Sheets (ID: {sheet_id})"

    def load_from_excel(self, file_path: str) -> None:
        """Загружает таблицу из Excel"""
        reader = ExcelReader(file_path=file_path)
        self.table = reader.read()
        self.analyzer = TableAnalyzer(self.table)

        self.source_info = f"Excel ({os.path.basename(file_path)})"

    def is_table_loaded(self) -> bool:
        """Проверяет загружена ли таблица"""
        return self.table is not None

    def get_all_dates(self) -> list[str]:
        """Возвращает все уникальные даты из таблицы"""
        if not self.is_table_loaded() or self.analyzer is None:
            return []

        dates = self.analyzer.dates.dropna() 
        return [str(d) for d in sorted(dates)]

    def get_sum_for_period(self, date_from: str, date_to: str) -> int:
        """Вычисляет сумму за период"""
        if not self.is_table_loaded() or self.analyzer is None:
            raise ValueError("Таблица не загружена")

        date_from_parsed = datetime.fromisoformat(date_from).date()
        date_to_parsed = datetime.fromisoformat(date_to).date()

        self.current_sum = self.analyzer.sum_by_period(date_from_parsed, date_to_parsed)
        return self.current_sum

    def get_source_info(self) -> str:
        """Возвращает информацию об источнике данных"""
        return self.source_info or "Таблица не загружена"

    def try_generate_image(self, date_from: str, date_to: str) -> bool:
        """Генерирует изображение и создает ImageNode"""
        if self.current_sum is None:
            raise ValueError("Сначала получите сумму")

        if self._image_gen is None:
            self._image_gen = ImageGen()

        self._image_gen.create(str(self.current_sum))
        image_path = self._image_gen.get_image_path()

        if image_path is None:
            raise ValueError("Не удалось сгенерировать изображение")

        self.image_node = ImageNode(
            sum=self.current_sum,
            period_start=date_from,
            period_end=date_to,
            image_path=image_path,
        )

        self.image_generated = True
        return True

    def get_image_name(self) -> str:
        """Возвращает путь к сгенерированному изображению"""
        if not self.image_generated or self.image_node is None:
            raise ValueError("Сначала сгенерируйте изображение")

        return self.image_node.image_path

    def push_to_neo4j(self) -> bool:
        """Отправляет данные в neo4j"""
        if not self.image_generated or self.image_node is None:
            raise ValueError("Сначала сгенерируйте изображение")

        if self._graph_service is None:
            self._graph_service = GraphDBService()

        self._graph_service.push_image_node(self.image_node)
        return True

    def search_similar_images(self, threshold: float = 0.8) -> list[dict[str, str]]:
        """Ищет похожие изображения в neo4j"""
        if not self.image_generated or self.image_node is None:
            raise ValueError("Сначала сгенерируйте изображение")

        self.push_to_neo4j()  

        if self._graph_service is None:
            self._graph_service = GraphDBService()

        similar_nodes = self._graph_service.find_similar_by_sum(self.image_node.id)
        return similar_nodes

    def is_image_generated(self) -> bool:
        """Проверяет, сгенерировано ли изображение"""
        return self.image_generated
