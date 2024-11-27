import datetime
from pathlib import Path

from sqlalchemy import Column, Integer, String, Date, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..profile import profile


engine = create_engine("sqlite:///" + str(profile.db_path), echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()

SCHEDULE_DAYS = [0, 1, 3, 7, 14, 30, 90, 180, 360]


class Word(Base):
    __tablename__ = "words"

    word = Column(String(64), primary_key=True)
    review_count = Column(Integer, default=0)
    master_count = Column(Integer, default=0)   # Continuous mastery
    forget_count = Column(Integer, default=0)
    schedule_day = Column(Date, default=datetime.date.today())
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(),
                        onupdate=datetime.datetime.now())

    def to_dict(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != '_'])


class ReviewHistory(Base):
    __tablename__ = "review_history"

    date = Column(Date, default=datetime.date.today(), primary_key=True)
    word_count = Column(Integer, default=0)


Base.metadata.create_all(engine)
