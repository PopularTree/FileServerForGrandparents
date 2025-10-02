# models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'metadata.db')
engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    filename = Column(String)          # 保存先のファイルパス（相対）
    original_name = Column(String)     # 元ファイル名
    media_type = Column(String)        # 'image' or 'video'
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    sender = Column(String)            # オプション: 送信者名等

Base.metadata.create_all(engine)
