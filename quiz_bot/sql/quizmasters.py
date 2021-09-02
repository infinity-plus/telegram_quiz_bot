import threading

from quiz_bot.sql import BASE, SESSION
from sqlalchemy import Column, Integer


class QuizMaster(BASE):
    """
    A table class representing a QuizMaster.
    Args:
        - user_id: User ID of telegram account of Quizmaster.
    """
    __tablename__ = "quiz_master"
    user_id = Column(Integer, primary_key=True)

    def __init__(self, user_id) -> None:
        self.user_id = user_id

    def __repr__(self) -> str:
        return f"QuizMaster {self.user_id}"


QuizMaster.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()


def get_quizmasters() -> list[int]:
    try:
        return [
            int(user_id[0]) for user_id in SESSION.query(QuizMaster.user_id)
        ]
    finally:
        SESSION.close()


def add_quizmaster(user_id: int) -> str:
    with INSERTION_LOCK:
        curr = SESSION.query(QuizMaster).get(user_id)

        if not curr:
            curr = QuizMaster(user_id)
            SESSION.add(curr)
            SESSION.commit()
            return f"Successfully added {user_id} to database."
        else:
            return f"{user_id} Already in database."


def rm_quizmaster(user_id: int) -> str:
    with INSERTION_LOCK:
        curr = SESSION.query(QuizMaster).get(user_id)

        if curr:
            SESSION.delete(curr)
            SESSION.commit()
            return f"Successfully removed {user_id} from database."
        else:
            return f"{user_id} is not in database."
