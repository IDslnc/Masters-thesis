from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime
from sqlalchemy import Text

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float, Text
from sqlalchemy.orm import relationship
from db.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_role = Column(String(20), nullable=False)  # 'Врач' или 'Администратор'
    full_name = Column(String(100), nullable=False)
    login = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    patients = relationship("Patient", back_populates="user")

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    birth_date = Column(Date)
    contact_info = Column(String(100))
    user_id = Column(Integer, ForeignKey("users.user_id"))

    user = relationship("User", back_populates="patients")
    images = relationship("Image", back_populates="patient")
    medical_history = relationship("MedicalHistory", back_populates="patient")

class Image(Base):
    __tablename__ = "images"

    image_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    date_of_shot = Column(Date)
    file_path = Column(String(255))
    #other_metadata = Column(String(255))
    other_metadata = Column(Text)


    patient = relationship("Patient", back_populates="images")
    analysis = relationship("Analysis", back_populates="image", uselist=False)
    reports = relationship("Report", back_populates="image")

class Analysis(Base):
    __tablename__ = "analysis"

    analysis_id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.image_id"))
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    analysis_date = Column(Date)
    pathologies_found = Column(Text)
    annotation_data = Column(Text)
    confidence_score = Column(Float)

    image = relationship("Image", back_populates="analysis")
    reports = relationship("Report", back_populates="analysis")

class Report(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis.analysis_id"))
    image_id = Column(Integer, ForeignKey("images.image_id"))
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    report_text = Column(Text)
    pdf_path = Column(String(255))

    analysis = relationship("Analysis", back_populates="reports")
    image = relationship("Image", back_populates="reports")
    patient = relationship("Patient")

class MedicalHistory(Base):
    __tablename__ = "medical_history"

    history_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    analysis_id = Column(Integer, ForeignKey("analysis.analysis_id"))
    record_date = Column(Date)
    treatment = Column(Text)
    diagnosis = Column(String(255))

    patient = relationship("Patient", back_populates="medical_history")

class AIModel(Base):
    __tablename__ = "ai_model"

    model_id = Column(Integer, primary_key=True, index=True)
    last_update = Column(Date)
    version = Column(String(50))
    weights_path = Column(String(255))
