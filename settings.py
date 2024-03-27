import os

from dotenv import load_dotenv

load_dotenv(".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

file_path = "путь_до_файла.xlsx"
