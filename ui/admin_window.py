from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout,
    QLineEdit, QComboBox, QMessageBox, QFileDialog
)
import os
from db.database import SessionLocal
from db.models import User, AIModel
from datetime import date

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Окно администратора")
        self.setGeometry(150, 150, 650, 500)

        self.db = SessionLocal()
        self.init_ui()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout()

        # Таблица пользователей
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Логин", "Роль"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(QLabel("Пользователи:"))
        layout.addWidget(self.table)

        # Форма добавления пользователя
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ФИО")
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Пароль")
        self.role_input = QComboBox()
        self.role_input.addItems(["врач", "администратор"])

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.login_input)
        form_layout.addWidget(self.pass_input)
        form_layout.addWidget(self.role_input)

        layout.addLayout(form_layout)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить пользователя")
        delete_btn = QPushButton("Удалить выбранного")
        add_btn.clicked.connect(self.add_user)
        delete_btn.clicked.connect(self.delete_user)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)

        # Кнопка обновления модели
        model_btn = QPushButton("Загрузить новую модель (.pt)")
        model_btn.clicked.connect(self.upload_model)
        layout.addWidget(QLabel("\nМодель ИИ:"))
        layout.addWidget(model_btn)

        self.setLayout(layout)

    def load_users(self):
        self.table.setRowCount(0)
        users = self.db.query(User).all()
        for row_idx, u in enumerate(users):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(u.user_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(u.full_name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(u.login))
            self.table.setItem(row_idx, 3, QTableWidgetItem(u.user_role))

    def add_user(self):
        name = self.name_input.text().strip()
        login = self.login_input.text().strip()
        password = self.pass_input.text().strip()
        role = self.role_input.currentText()

        if not (name and login and password):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        existing = self.db.query(User).filter_by(login=login).first()
        if existing:
            QMessageBox.warning(self, "Ошибка", "Логин уже существует")
            return

        user = User(full_name=name, login=login, password_hash=password, user_role=role)
        self.db.add(user)
        self.db.commit()
        self.load_users()

        self.name_input.clear()
        self.login_input.clear()
        self.pass_input.clear()

    def delete_user(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления")
            return

        user_id = int(self.table.item(selected, 0).text())
        user = self.db.query(User).filter_by(user_id=user_id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
            self.load_users()

    def upload_model(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите .pt модель", "", "Model files (*.pt)")
        if file_path and os.path.exists(file_path):
            model = AIModel(
                last_update=date.today(),
                version="v" + date.today().strftime("%Y%m%d"),
                weights_path=file_path
            )
            self.db.add(model)
            self.db.commit()
            QMessageBox.information(self, "Готово", "Модель загружена и сохранена.")
