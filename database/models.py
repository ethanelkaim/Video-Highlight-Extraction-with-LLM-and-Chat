from sqlalchemy import Column, Integer, String, Float, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False, unique=True)
    path = Column(String, nullable=False)


class Highlight(Base):
    __tablename__ = "highlights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key
    timestamp = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    embedding = Column(LargeBinary, nullable=False)  # Store as bytes
    summary = Column(String, nullable=True)
