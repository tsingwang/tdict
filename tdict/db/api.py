import datetime
from typing import Iterator

from .models import Session, Word, SCHEDULE_DAYS


def list_words(order: str = "schedule_day",
               offset: int = 0, limit: int = 20) -> Iterator[dict]:
    with Session.begin() as session:
        for w in session.query(Word).order_by(order).offset(offset).limit(limit):
            yield w.to_dict()


def list_today_words() -> Iterator[dict]:
    today = datetime.date.today()
    with Session.begin() as session:
        for w in session.query(Word).filter(Word.schedule_day <= today):
            yield w.to_dict()


def add_word(word: str) -> None:
    with Session.begin() as session:
        if session.query(Word).get(word):
            return
        session.add(Word(word=word))


def delete_word(word: str) -> None:
    with Session.begin() as session:
        session.query(Word).filter_by(word=word).delete()


def master_word(word: str) -> None:
    with Session.begin() as session:
        word = session.query(Word).get(word)
        if word is None:
            return

        i = min(word.master_count, len(SCHEDULE_DAYS) - 1)
        word.schedule_day = datetime.date.today() + \
                datetime.timedelta(days=SCHEDULE_DAYS[i])
        # limit 20 words every day, for schedule balance
        while session.query(Word).\
                filter_by(schedule_day=word.schedule_day).count() > 20:
            word.schedule_day += datetime.timedelta(days=1)

        word.master_count += 1
        word.review_count += 1


def forget_word(word: str) -> None:
    with Session.begin() as session:
        word = session.query(Word).get(word)
        if word is None:
            return

        word.schedule_day = datetime.date.today()
        word.master_count = 0
        word.forget_count += 1
        word.review_count += 1
