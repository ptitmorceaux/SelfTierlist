from sqlalchemy import Column, ForeignKey, Integer, String

from db.base import Base


class ImageTierlist(Base):

    __tablename__ = "image_tierlist"

    image_hash = Column(String(64), ForeignKey("image.hash", ondelete="CASCADE"), primary_key=True)
    tierlist_id = Column(Integer, ForeignKey("tierlist.id", ondelete="CASCADE"), primary_key=True)
