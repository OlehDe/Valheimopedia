import os
import json
from datetime import datetime
import hashlib
import secrets

class UserManager:
    def __init__(self):
        self.users_dir = os.path.join(os.path.dirname(__file__), 'user_data')
        if not os.path.exists(self.users_dir):
            os.makedirs(self.users_dir)
        self.sessions = {}

    def _hash_password(self, password):
        """Хешування паролю"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, email):
        """Реєстрація нового користувача"""
        user_file = os.path.join(self.users_dir, f"{username}.json")

        if os.path.exists(user_file):
            return False, "Користувач з таким іменем вже існує"

        user_data = {
            "username": username,
            "password": self._hash_password(password),
            "email": email,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True,
            "news": []
        }

        try:
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=4)
            return True, "Користувач успішно зареєстрований"
        except Exception as e:
            return False, f"Помилка при реєстрації: {str(e)}"

    def create_session(self, username):
        """Створення сесії для користувача"""
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            "username": username,
            "created_at": datetime.now().isoformat()
        }
        return session_token

    def authenticate_user(self, username, password):
        """Автентифікація користувача"""
        user_file = os.path.join(self.users_dir, f"{username}.json")

        if not os.path.exists(user_file):
            return False, "Користувача не знайдено"

        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            if user_data["password"] == self._hash_password(password):
                user_data["last_login"] = datetime.now().isoformat()
                with open(user_file, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, ensure_ascii=False, indent=4)

                session_token = self.create_session(username)
                return True, {"session_token": session_token, "user_data": user_data}
            else:
                return False, "Невірний пароль"
        except Exception as e:
            return False, f"Помилка при автентифікації: {str(e)}"

    def check_session(self, session_token):
        """Перевірка сесії користувача"""
        return self.sessions.get(session_token)

    def logout_user(self, session_token):
        """Вихід користувача"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False

    def add_news(self, username, news_data):
        """Додавання новини користувачем"""
        user_file = os.path.join(self.users_dir, f"{username}.json")

        if not os.path.exists(user_file):
            return False, "Користувача не знайдено"

        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                user_data = json.load(f)

            news_item = {
                "id": len(user_data["news"]) + 1,
                "title": news_data["title"],
                "content": news_data["content"],
                "created_at": datetime.now().isoformat()
            }

            user_data["news"].append(news_item)

            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=4)

            return True, news_item
        except Exception as e:
            return False, f"Помилка при додаванні новини: {str(e)}"