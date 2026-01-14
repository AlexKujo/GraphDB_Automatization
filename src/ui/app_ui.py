
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from src.controllers.app_controller import TableController


class TableUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Table Manager")
        self.window.geometry("600x400")
        
        self.controller = TableController()
        self._ui_create_widgets()
    
    def _ui_create_widgets(self):
        """Создаёт все виджеты интерфейса"""
        self._ui_create_google_sheets_section()
        self._ui_create_excel_section()
        self._ui_create_date_selection_section()
        self._ui_create_action_buttons()
        self._ui_create_info_section()
    
    def _ui_create_google_sheets_section(self):
        """Секция для загрузки из Google Sheets"""
        frame = ttk.LabelFrame(self.window, text="Google Sheets", padding=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame, text="Sheet ID:").pack(side="left")
        self.sheet_id_entry = ttk.Entry(frame, width=40)
        self.sheet_id_entry.pack(side="left", padx=5)
        
        # Добавляем поддержку Ctrl+V для вставки
        self.sheet_id_entry.bind('<Control-v>', self._paste_to_entry)
        
        ttk.Button(frame, text="Загрузить", command=self._load_google_sheets).pack(side="left")
    
    def _paste_to_entry(self, event):
        """Вставляет текст из буфера обмена в поле ввода"""
        try:
            text = self.window.clipboard_get()
            self.sheet_id_entry.insert(tk.INSERT, text)
        except tk.TclError:
            pass  # Буфер пуст
        return "break"  # Предотвращает дальнейшую обработку события
    
    def _ui_create_excel_section(self):
        """Секция для загрузки из Excel"""
        frame = ttk.LabelFrame(self.window, text="Excel File", padding=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        self.excel_path_label = ttk.Label(frame, text="Файл не выбран")
        self.excel_path_label.pack(side="left", padx=5)
        
        # ttk.Button(frame, text="Выбрать файл", command=self._select_excel_file).pack(side="left")
        ttk.Button(frame, text="Выбрать файл", command=self._load_excel).pack(side="left", padx=5)
    
    def _ui_create_date_selection_section(self):
        """Секция выбора дат"""
        frame = ttk.LabelFrame(self.window, text="Выбор периода", padding=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame, text="С:").pack(side="left")
        self.date_from_combo = ttk.Combobox(frame, state="readonly", width=15)
        self.date_from_combo.pack(side="left", padx=5)
        
        ttk.Label(frame, text="По:").pack(side="left")
        self.date_to_combo = ttk.Combobox(frame, state="readonly", width=15)
        self.date_to_combo.pack(side="left", padx=5)
    
    def _ui_create_action_buttons(self):
        """Кнопки действий"""
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(frame, text="Получить сумму", command=self._get_sum).pack(side="left", padx=5)
        ttk.Button(frame, text="Сгенерировать изображение", command=self._generate_image).pack(side="left", padx=5)
        ttk.Button(frame, text="Искать похожие", command=self._search_similar_images).pack(side="left", padx=15)
        self.send_button = ttk.Button(frame, text="Добавить в neo4j", command=self._send_number, state="disabled")
        self.send_button.pack(side="left", padx=5)
    
    def _ui_create_info_section(self):
        """Блок справочной информации"""
        frame = ttk.LabelFrame(self.window, text="Информация", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.info_text = tk.Text(frame, height=8, state="disabled")
        self.info_text.pack(fill="both", expand=True)
  
  
    
    def _load_google_sheets(self):
        """Обработчик загрузки из Google Sheets"""
        sheet_id = self.sheet_id_entry.get()
        if not sheet_id:
            messagebox.showwarning("Ошибка", "Введите Sheet ID")
            return
        
        try:
            from src.config.config import GOOGLE_SHEETS_CREDENTIALS_PATH
            self.controller.load_from_google_sheets(
                cred_path=str(GOOGLE_SHEETS_CREDENTIALS_PATH),
                sheet_id=sheet_id
            )
            self._add_info(f"Таблица загружена из {self.controller.get_source_info()}")
            self._populate_date_combos()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить таблицу: {e}")
    
    def _load_excel(self):
        file_path = filedialog.askopenfilename(
            title="Выберите Excel файл",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        self.excel_path = file_path
        self.excel_path_label.config(text=os.path.basename(file_path))

        try:
            self.controller.load_from_excel(self.excel_path)
            self._add_info(f"Таблица загружена из {self.controller.get_source_info()}")
            self._populate_date_combos()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить таблицу: {e}")

    def _populate_date_combos(self):
        """Заполняет выпадающие списки датами"""
        dates = self.controller.get_all_dates()
        
        self.date_from_combo['values'] = dates
        self.date_to_combo['values'] = dates
        
        if dates:
            self.date_from_combo.current(0)
            self.date_to_combo.current(len(dates) - 1)
    
    def _get_sum(self):
        """Обработчик получения суммы"""
        if not self.controller.is_table_loaded():
            messagebox.showwarning("Ошибка", "Сначала загрузите таблицу")
            return
        
        date_from = self.date_from_combo.get()
        date_to = self.date_to_combo.get()
        
        if not date_from or not date_to:
            messagebox.showwarning("Ошибка", "Выберите даты")
            return
        
        try:
            total = self.controller.get_sum_for_period(date_from, date_to)
            self._add_info(f"Сумма за период {date_from} - {date_to}: {total}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вычислить сумму: {e}")
    
    def _generate_image(self):
        """Генерирует изображение"""
        date_from = self.date_from_combo.get()
        date_to = self.date_to_combo.get()
        
        try:
            self.controller.try_generate_image(date_from, date_to)
            self.send_button.config(state="normal")
            self._add_info(f"Изображение {self.controller.get_image_name()} сгенерировано")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать изображение: {e}")
    
    def _send_number(self):
        """Обработчик отправки в neo4j"""
        try:
            self.controller.push_to_neo4j()
            self._add_info("Данные отправлены в neo4j")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отправить данные: {e}")
    
    def _add_info(self, message: str):
        """Добавляет сообщение в информационный блок"""
        self.info_text.config(state="normal")
        self.info_text.insert("end", f"{message}\n")
        self.info_text.see("end")
        self.info_text.config(state="disabled")
        
    def _search_similar_images(self):
        """Ищет похожие изображения"""
        try:
            results = self.controller.search_similar_images()
            if not results:
                self._add_info("Похожие изображения не найдены")
                return
            
            self._add_info("Похожие изображения:")
            for res in results:
                self._add_info(f"Path: {res['image_path']}, Sum: {res['sum']}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось найти похожие изображения: {e}")
    
    def run(self):
        """Запускает приложение"""
        self.window.mainloop()


