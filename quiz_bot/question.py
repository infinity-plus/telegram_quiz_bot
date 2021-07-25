from random import shuffle
from autologging import logged, traced


@traced
@logged
class Question:
    """
    A class representing a Question.

    + Args:
        - `statement: str` - Statement of the question.
        - `option1`, `option2`, `option3`, `option4: str` - The options for the question.
        - `correct_option: str` - The correct option.
    + Methods:
        - `is_correct(option: str) -> bool`: Returns whether the option is True or not.
        - `get_options() -> list[str]`: Returns the list of options.
        - `get_question() -> str:` Returns the Question statement.
        - `get_correct() -> str:` Returns the correct option.
        - `shuffle_options() -> None:` Shuffle the options.
        - `ask_question() -> str:` Returns a string with Question Statement and list of options.
    """

    def __init__(self, statement: str, option1: str, option2: str,
                 option3: str, option4: str, correct_option: str) -> None:
        self.statement: str = statement
        self.options: list[str] = [option1, option2, option3, option4]
        self.correct_option: str = correct_option

    def __repr__(self) -> str:
        newline = '\n'
        return f'''Question: {self.statement}
        Options: {newline.join(self.options)}
        Correct Option: {self.correct_option}'''

    def __str__(self) -> str:
        return self.__repr__()

    def is_correct(self, option: str) -> bool:
        """Method to check whether the given option is True or not.

        + Args:
            - `option: str` - The option to be checked.
        + Returns:
            - `True` if the option and the correct options are equal.
            - `False` if the option and the correct options are not equal.
        """
        return self.correct_option == option

    def get_options(self) -> list[str]:
        """Method to get the list of options.

        + Args:
            - `None`
        + Returns:
            - `list[str]` of options.
        """
        return self.options

    def get_correct(self) -> str:
        """Method to get the correct option.

        + Args:
            - `None`
        + Returns:
            - `str`
        """
        return self.correct_option

    def get_question(self) -> str:
        """Method to get the question statement.

        + Args:
            - `None`
        + Returns:
            - `str`
        """
        return self.statement

    def shuffle_options(self) -> None:
        """Method to shuffle the options.

        + Args:
            - `None`
        + Returns:
            - `None`
        """
        shuffle(self.options)

    def ask_question(self) -> str:
        """Method to get the question as asked.

        + Args:
            - `None`
        + Returns:
            - `str`
        """
        newline = '\n'
        return f'''Question: {self.statement}

Options:
{newline.join([f"{number}. {option}"
    for number, option in enumerate(self.options, start=1)])}'''