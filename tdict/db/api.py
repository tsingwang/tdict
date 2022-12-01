import datetime

from .models import Session, Word, SCHEDULE_DAYS


def list_words():
    with Session.begin() as session:
        for w in session.query(Word):
            yield w.to_dict()


def list_today_words():
    today = datetime.date.today()
    with Session.begin() as session:
        for w in session.query(Word).filter(Word.schedule_day <= today):
            yield w.to_dict()


def add_word(word: str):
    with Session.begin() as session:
        session.add(Word(word=word))


def delete_word(word: str):
    with Session.begin() as session:
        session.query(Word).filter_by(word=word).delete()


def master_word(word: str):
    with Session.begin() as session:
        word = session.query(Word).filter_by(word=word).first()
        i = min(word.master_count, len(SCHEDULE_DAYS) - 1)
        word.schedule_day += datetime.timedelta(days=SCHEDULE_DAYS[i])
        word.master_count += 1
        word.review_count += 1


def forget_word(word: str):
    with Session.begin() as session:
        word = session.query(Word).filter_by(word=word).first()
        word.schedule_day = datetime.date.today()
        word.master_count = 0
        word.forget_count += 1
        word.review_count += 1
