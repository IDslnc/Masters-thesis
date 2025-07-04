# Masters-thesis
Дипломный проект магистерской диссертации

# Masters-thesis

**Дипломный проект магистерской диссертации**  
*Система распознавания кариеса и периодонтита на основе компьютерного зрения*

---

## Описание проекта

В рамках проекта разработана десктопная интеллектуальная система для предварительного анализа ортопантомограмм (ОПТГ). Система помогает врачу выявлять признаки кариеса и периодонтита на рентгеновских снимках с использованием модели глубокого обучения (YOLOv8n).

Проект ориентирован на применение в частных клиниках и направлен на сокращение времени анализа и повышение точности диагностики при сохранении автономной работы (без необходимости подключения к интернету).

---

## Основные возможности

- Автоматическое распознавание патологий на ОПТГ-снимках
- Использование обученной модели YOLOv8n
- Предобработка изображений и фильтрация шумов
- Графический интерфейс для врача (PyQt)
- Сохранение аннотированных снимков и текстовых заключений
- Работа в оффлайн-режиме с соблюдением конфиденциальности

---

## Технологии

- Python 3.10+
- YOLOv8
- PyQt5
- PostgreSQL
- OpenCV, NumPy

---

## Структура репозитория

ai/ Логика работы с нейросетью

db/ Работа с базой данных PostgreSQL

reports/ Отчеты и визуализация

ui/ GUI-интерфейс на PyQt

add_user.py Добавление пользователя

init_db.py Инициализация базы данных

main.py Точка входа в приложение

yolov8n.pt модель YOLOv8n

best_v5.pt обученная модель

Untitled.ipynb Jupyter Notebook с обучением модели

requirements.txt Зависимости проекта
