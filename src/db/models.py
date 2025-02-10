from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Integer, unique=True, nullable=False)

    pairs = relationship("Pairs", back_populates="user")


class Pairs(Base):
    __tablename__ = 'pairs'

    id = Column(Integer, primary_key=True, index=True)
    written = Column(String)
    intended = Column(String)
    written_ipm = Column(Float)
    intended_ipm = Column(Float)
    wi_ratio = Column(Float)
    datetime = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="pairs")

    def to_dict(self):
        return {
            "id": self.id,
            "written": self.written,
            "intended": self.intended,
            "written_ipm": self.written_ipm,
            "intended_ipm": self.intended_ipm,
            "wi_ratio": self.wi_ratio,
            "datetime": self.datetime.isoformat(),
            "user_id": self.user_id,
        }
