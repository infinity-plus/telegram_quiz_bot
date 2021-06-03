from random import shuffle
from requests import get
from autologging import logged, traced


@traced
@logged
class Question:
    statement: str = ""
    options: list[str] = []
    correct_option: str = ""

    def __init__(self, statement: str, option1: str, option2: str, option3: str, option4: str, correct_option: str) -> None:
        self.statement = statement
        self.options = [option1, option2, option3, option4]
        self.correct_option = correct_option

    def __repr__(self) -> str:
        newline = '\n'
        return f'''Question: {self.statement}
        Options: {newline.join(self.options)}
        Correct Option: {self.correct_option}'''

    def __str__(self) -> str:
        return self.__repr__()

    def is_correct(self, option: str) -> bool:
        return self.correct_option == option

    def get_options(self) -> list[str]:
        return self.options

    def get_correct(self) -> str:
        return self.correct_option

    def get_question(self) -> str:
        return self.statement

    def shuffle_options(self) -> None:
        shuffle(self.options)

    def ask_question(self) -> str:
        newline = '\n'
        return f'''Question: {self.statement}{newline}{newline}
        Options:{newline}{newline.join([f"{number}. {option}" for number, option in enumerate(self.options, start=1)])}'''


@traced
@logged
class QuestionList:
    questions: list[Question] = []

    def __init__(self, qlist: list[dict]) -> None:
        self.questions = [Question(**i) for i in qlist]

    def __repr__(self) -> str:
        newline = '\n'
        return f'''Questions: {newline} {[i.__repr__() for i in self.questions]}'''

    def __len__(self) -> int:
        return len(self.questions)

    def __getitem__(self, index: int) -> Question:
        return self.questions[index]
