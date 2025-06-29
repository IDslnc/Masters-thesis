import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PIL import Image as PILImage
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QHBoxLayout, QLineEdit, QMessageBox,
    QListWidget, QSplitter
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import datetime

from db.database import SessionLocal
from db.models import Patient, Image, Report
from ai.preprocess import preprocess_image
from ai.model import run_prediction
from reports.report_gen import generate_report

class DentalApp(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Система распознавания кариеса и периодонтита - окно врача")
        self.setGeometry(100, 100, 1000, 800)

        self.db = SessionLocal()
        self.init_ui()
        self.load_patients()

        # Отключить функции анализа для администратора
        if self.user.user_role.lower() == 'администратор':
            self.upload_btn.setDisabled(True)
            self.analyze_btn.setDisabled(True)
            self.name_input.setDisabled(True)
            self.date_input.setDisabled(True)
            self.result_text.setReadOnly(True)

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.left_panel = QVBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ФИО или дате приёма")
        self.search_input.textChanged.connect(self.filter_patients)

        self.patient_list = QListWidget()
        self.patient_list.itemClicked.connect(self.load_patient_history)

        self.image_history_list = QListWidget()
        self.image_history_list.itemClicked.connect(self.show_selected_history_item)

        self.left_panel.addWidget(self.search_input)
        self.left_panel.addWidget(QLabel("Пациенты:"))
        self.left_panel.addWidget(self.patient_list)
        self.left_panel.addWidget(QLabel("История снимков:"))
        self.left_panel.addWidget(self.image_history_list)

        self.right_panel = QVBoxLayout()

        patient_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ФИО пациента")
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("Дата приёма (ДД.ММ.ГГГГ)")
        patient_layout.addWidget(self.name_input)
        patient_layout.addWidget(self.date_input)
        self.right_panel.addLayout(patient_layout)

        self.upload_btn = QPushButton("Загрузить ОПТГ-снимок")
        self.upload_btn.clicked.connect(self.upload_image)
        self.right_panel.addWidget(self.upload_btn)

        self.image_label = QLabel("Снимок не выбран")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.right_panel.addWidget(self.image_label)

        self.annotated_label = QLabel("Аннотированный снимок появится после анализа")
        self.annotated_label.setAlignment(Qt.AlignCenter)
        self.right_panel.addWidget(self.annotated_label)

        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("Здесь появятся результаты анализа")
        self.right_panel.addWidget(self.result_text)

        self.analyze_btn = QPushButton("Анализировать снимок")
        self.analyze_btn.clicked.connect(self.analyze_image)
        self.right_panel.addWidget(self.analyze_btn)

        splitter = QSplitter()
        left_container = QWidget()
        left_container.setLayout(self.left_panel)
        right_container = QWidget()
        right_container.setLayout(self.right_panel)

        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setSizes([300, 700])

        self.layout.addWidget(splitter)

    def load_patients(self):
        self.patients = self.db.query(Patient).order_by(Patient.full_name).all()
        self.update_patient_list(self.patients)

    def update_patient_list(self, patients):
        self.patient_list.clear()
        for p in patients:
            last_image = self.db.query(Image).filter_by(patient_id=p.patient_id).order_by(Image.date_of_shot.desc()).first()
            last_date = last_image.date_of_shot.strftime("%d.%m.%Y") if last_image and last_image.date_of_shot else "-"
            self.patient_list.addItem(f"{p.full_name} ({last_date})")

    def filter_patients(self):
        text = self.search_input.text().lower()
        filtered = []
        for p in self.patients:
            last_image = self.db.query(Image).filter_by(patient_id=p.patient_id).order_by(Image.date_of_shot.desc()).first()
            last_date_str = last_image.date_of_shot.strftime("%d.%m.%Y") if last_image and last_image.date_of_shot else ""
            if text in p.full_name.lower() or text in last_date_str:
                filtered.append(p)
        self.update_patient_list(filtered)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.xpm *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path).scaled(640, 320, Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
            self.annotated_label.clear()
            self.result_text.setText("")

    def analyze_image(self):
        if not hasattr(self, 'image_path'):
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите снимок!")
            return

        name = self.name_input.text().strip()
        birth = self.date_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите ФИО пациента!")
            return
        
        if not birth:
            QMessageBox.warning(self, "Ошибка", "Введите дату приёма пациента!")
            return

        patient = self.db.query(Patient).filter_by(full_name=name).first()
        if not patient:
            patient = Patient(full_name=name)
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)

        preproc_path = self.image_path.replace(".jpg", "_pre.jpg")
        preprocess_image(self.image_path, preproc_path)

        results = run_prediction(preproc_path)
        ann_path = self.image_path.replace(".jpg", "_ann.jpg")
        
        img = results.plot(labels=False, conf=False, line_width=3, color_mode='class')
        pil_img = PILImage.fromarray(img)
        pil_img.save(ann_path)


        # Перевод классов
        translation_map = {
            "karies": "Кариес",
            "periodontit": "Периодонтит"
        }

        classes = [results.names[c] for c in results.boxes.cls.int().tolist()] if results.boxes else []
        if classes:
            from collections import Counter
            counter = Counter(classes)
            translated = [f"{count} {translation_map.get(name, name)}" for name, count in counter.items()]
            result_text = "Обнаружены патологии: " + ", ".join(translated)
        else:
            result_text = "Патологии не обнаружены."

        self.result_text.setText(result_text)

        record = Image(
            patient_id=patient.patient_id,
            date_of_shot=datetime.datetime.strptime(birth, "%d.%m.%Y").date() if birth else None,
            file_path=self.image_path,
            other_metadata=result_text
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        report_path = self.image_path.replace(".jpg", "_report.docx")
        generate_report(patient.full_name, ann_path, result_text, report_path)

        report = Report(image_id=record.image_id, patient_id=patient.patient_id, report_text=result_text, pdf_path=report_path)
        self.db.add(report)
        self.db.commit()

        if os.path.exists(ann_path):
            ann_pixmap = QPixmap(ann_path).scaled(640, 320, Qt.KeepAspectRatio)
            self.annotated_label.setPixmap(ann_pixmap)

        QMessageBox.information(self, "Готово", "Анализ завершён, отчёт сохранён.")
        self.load_patients()

    def load_patient_history(self, item):
        selected_text = item.text()
        name = selected_text.split(' (')[0]
        self.selected_patient = self.db.query(Patient).filter_by(full_name=name).first()
        if not self.selected_patient:
            return

        self.name_input.setText(self.selected_patient.full_name)
        self.date_input.setText(str(self.selected_patient.birth_date or ''))

        images = self.db.query(Image).filter_by(patient_id=self.selected_patient.patient_id).order_by(Image.image_id.desc()).all()
        self.image_history_list.clear()
        for img in images:
            date_str = img.date_of_shot.strftime("%d.%m.%Y") if img.date_of_shot else "-"
            self.image_history_list.addItem(f"{img.image_id} | {os.path.basename(img.file_path)} | {date_str}")

        if images:
            self.show_image(images[0])

    def show_selected_history_item(self, item):
        if not hasattr(self, 'selected_patient'):
            return
        image_id = int(item.text().split(' | ')[0])
        img = self.db.query(Image).filter_by(image_id=image_id).first()
        if img:
            self.show_image(img)

    def show_image(self, img):
        self.image_label.setPixmap(QPixmap(img.file_path).scaled(640, 320, Qt.KeepAspectRatio))
        ann_path = img.file_path.replace(".jpg", "_ann.jpg")
        if os.path.exists(ann_path):
            self.annotated_label.setPixmap(QPixmap(ann_path).scaled(640, 320, Qt.KeepAspectRatio))
        self.result_text.setText(img.other_metadata or '')