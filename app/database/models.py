from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    document_name = Column(String, nullable=False)

    upload_time = Column(DateTime, default=datetime.utcnow)

    total_pages = Column(Integer, default=0)

    total_chunks = Column(Integer, default=0)

    category = Column(String, default="Unknown")

    status = Column(String, default="Uploaded")