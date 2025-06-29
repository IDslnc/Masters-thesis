from PyQt5.QtWidgets import (QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt
from db.database import SessionLocal
from db.models import User

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 180)

        self.db = SessionLocal()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit()

        self.pass_label = QLabel("Пароль:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.handle_login)

        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.pass_label)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def handle_login(self):
        login = self.login_input.text().strip()
        password = self.pass_input.text().strip()

        user = self.db.query(User).filter_by(login=login, password_hash=password).first()
        if user:
            self.accept()
            self.user = user
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
