from .models import Session, Word


def list_words():
    with Session.begin() as session:
        for word in session.query(Word).all():
            print(word.word)


def add_word(word: str):
    with Session.begin() as session:
        session.add(Word(word=word))


def delete_word(word: str):
    with Session.begin() as session:
        session.query(Word).filter_by(word=word).delete()
