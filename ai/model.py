from ultralytics import YOLO
from db.database import SessionLocal
from db.models import AIModel

# Получаем путь к последней модели из БД
db = SessionLocal()
latest_model = db.query(AIModel).order_by(AIModel.last_update.desc()).first()

if latest_model and latest_model.weights_path:
    model = YOLO(latest_model.weights_path)
else:
    model = YOLO("best.pt")  # запасной вариант по умолчанию

def run_prediction(image_path: str):
    results = model(image_path, iou=0.75, conf=0.3)
    return results[0]
