from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import relationship
import os

# Creating DB Engine
def getEngine():
    load_dotenv()
    DATABASE_URL = f"{os.getenv('DB_TYPE')}://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

    # Create an engine
    engine = create_engine(DATABASE_URL)

    return engine

# Create an engine
engine = getEngine()

# Create a base class for our classes definitions
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)

    address = Column(String)
    name = Column(String)
    phone = Column(String)
    city = Column(String)
    country = Column(String)
    language = Column(String)
    thread_id = Column(String)
    assistant_id = Column(String)
    update_time = Column(String)
    gender = Column(String)
    age = Column(String)
    socioeconomic = Column(String)
    TypeOfFarm = Column(String)
    crop = Column(String)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    readings = relationship("Reading", back_populates="user")
    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    message = Column(String)
    response = Column(String)
    actionable = Column(String)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    user = relationship("User", back_populates="messages")

class Reading(Base):
    __tablename__ = 'readings'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    pH = Column(Float)
    nitrogen = Column(Float)
    phosphorus = Column(Float)
    potassium = Column(Float)
    temperature = Column(Float)
    moisture = Column(Float)
    conductivity = Column(Float)
    battery = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    user = relationship("User", back_populates="readings")

Base.metadata.create_all(engine)