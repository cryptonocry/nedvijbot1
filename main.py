import os
import json
import base64
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_NAME = "Заявки Telegram"
SHEET_NAME = "Лист1"

def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    google_credentials = os.getenv("GOOGLE_CREDENTIALS")
    if not google_credentials:
        raise ValueError("❌ GOOGLE_CREDENTIALS не установлена или пуста.")

    try:
        if google_credentials.strip().startswith('{'):
            # Прямой JSON
            creds_dict = json.loads(google_credentials)
        else:
            # Base64
            decoded_bytes = base64.b64decode(google_credentials)
            decoded_str = decoded_bytes.decode('utf-8', errors='replace')
            creds_dict = json.loads(decoded_str)

        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
        return sheet
    except Exception as e:
        raise Exception(f"❌ Ошибка авторизации в Google Sheets: {e}")

if __name__ == "__main__":
    try:
        sheet = get_sheet()
        values = sheet.get_all_values()
        print("✅ Таблица найдена. Первая строка:")
        print(values[0] if values else "Таблица пуста")
    except Exception as err:
        print(err)
