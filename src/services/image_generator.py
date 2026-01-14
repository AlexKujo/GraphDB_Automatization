import requests
import base64
import os
from dotenv import load_dotenv
import uuid
from src.config.config import IMAGES_DIR


class ImageGen:
    def __init__(self):
        load_dotenv()
        
        self.image_path = None
        
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY не найден. "
                "Установите переменную окружения OPENROUTER_API_KEY в файле .env"
            )
        
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create(self, number: str):
        """Создает изображение по промпту"""
        
        prompt = f"Generate an image which would contain number {number}."
        
        data = {
            "model": "google/gemini-2.5-flash-image",
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": "1:1", "image_size": "1K"},
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            response.raise_for_status()

            # Сохраняем изображение
            result = response.json()
            image_url = result["choices"][0]["message"]["images"][0]["image_url"]["url"]
            image_bytes = base64.b64decode(image_url.split(",")[1])

            filepath = str(IMAGES_DIR / f"{uuid.uuid4().hex}.png")

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            print(f"✅ {filepath}")
            self.image_path = filepath

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
        
    def get_image_path(self):
        """Возвращает путь к сгенерированному изображению"""
        if self.image_path is None:
            raise ValueError("Изображение не сгенерировано")
        return self.image_path  # Замените на реальный путь после генерации


# # Использование
# gen = ImageGen()
# gen.create("24")
