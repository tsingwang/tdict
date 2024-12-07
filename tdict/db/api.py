from datetime import date, timedelta
from typing import Iterator

from sqlalchemy import func

from .models import Session, Word, ReviewHistory, SCHEDULE_DAYS


def list_words(order: str = "schedule_day",
               offset: int = 0, limit: int = 20) -> Iterator[dict]:
    with Session.begin() as session:
        for w in session.query(Word).order_by(order).offset(offset).limit(limit):
            yield w.to_dict()


def list_today_words() -> Iterator[dict]:
    today = date.today()
    with Session.begin() as session:
        for w in session.query(Word).filter(Word.schedule_day <= today).\
                order_by("schedule_day"):
            yield w.to_dict()


def query_word(word: str) -> None:
    with Session.begin() as session:
        w = session.query(Word).get(word)
        return w.to_dict() if w else None


def _schedule_day(day: date = None) -> date:
    """Limit 20 words every day, for schedule balance."""
    day = day if day is not None else date.today()
    with Session.begin() as session:
        while session.query(Word).filter_by(schedule_day=day).count() >= 20:
            day += timedelta(days=1)
    return day


def add_word(word: str) -> None:
    with Session.begin() as session:
        if session.query(Word).get(word):
            return
        session.add(Word(word=word, schedule_day=_schedule_day()))


def delete_word(word: str) -> None:
    with Session.begin() as session:
        session.query(Word).filter_by(word=word).delete()


def master_word(word: str) -> None:
    with Session.begin() as session:
        word = session.query(Word).get(word)
        if word is None:
            return

        word.review_count += 1
        word.master_count += 1
        i = min(word.master_count, len(SCHEDULE_DAYS) - 1)
        word.schedule_day = _schedule_day(
                date.today() + timedelta(days=SCHEDULE_DAYS[i]))


def forget_word(word: str) -> None:
    with Session.begin() as session:
        word = session.query(Word).get(word)
        if word is None:
            return

        word.review_count += 1
        word.forget_count += 1
        word.master_count = 0
        word.schedule_day = _schedule_day()


def update_review_history(total_master: int, total_forget: int):
    today = date.today()
    with Session.begin() as session:
        history = session.query(ReviewHistory).get(today)
        if history:
            history.total_master = total_master
            history.total_forget = total_forget
        else:
            session.add(ReviewHistory(date=today, total_master=total_master,
                                      total_forget=total_forget))


def get_review_history(date: date = date.today()) -> dict:
    with Session.begin() as session:
        r = session.query(ReviewHistory).get(date)
        return r.to_dict() if r else None


def list_review_history(year: int|None = None) -> dict:
    with Session.begin() as session:
        if year:
            first_day = date(year, 1, 1)
            last_day = date(year, 12, 31)
        else:
            last_day = date.today()
            first_day = last_day - timedelta(days=last_day.weekday() + 52 * 7)

        data = {
            r.date: {"total_master": r.total_master,
                     "total_forget": r.total_forget} \
                for r in session.query(ReviewHistory).\
                filter(func.DATE(ReviewHistory.date) >= first_day).\
                filter(func.DATE(ReviewHistory.date) <= last_day)
        }

        while first_day <= last_day:
            if first_day not in data:
                data[first_day] = {"total_master": 0, "total_forget": 0}
            first_day += timedelta(days=1)

        return {k: v for k, v in sorted(data.items())}


def get_review_schedule() -> list:
    """Only support sqlite3 now."""
    with Session.begin() as session:
        return session.query(
            func.strftime("%Y-%m", Word.schedule_day).label("month"),
            func.count("*").label("count")
        ).group_by("month").all()
