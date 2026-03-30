from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import relationship

from db.base import Base


class Image(Base):
    __tablename__ = "image"

    hash = Column(String(64), primary_key=True)
    path = Column(String(1024), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tierlists = relationship("Tierlist", secondary="image_tierlist", back_populates="images")
