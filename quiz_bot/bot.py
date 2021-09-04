#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from requests import get

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      Update, Message)
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_markdown, escape_markdown

from .question import Question
from quiz_bot import SHEET1, SHEET2
from autologging import logged, traced


@traced
@logged
class Quiz:
    """
    A class representing a quiz.

    + Args:
        - `TOKEN: str` - Bot Token from @botfather

    + Methods:
        - `initialize()`: Initialize all the handlers and start bot.
        - `start()`: `/start` handler (static method).
        - `new_quiz()`: - Handler to initiate a quiz session (static method).
        - `choose_quiz()`: Handler to choose amongst the two quizzes (static method).
        - `parse_question(question: Question) -> tuple`: A method returning a question
         statement with options as buttons.
        - `start_quiz()`: A handler to start the quiz.
        - `check_option()`: A handler to validate the option opted.
        - `send_scoreboard()`: A handler to send scoreboard to the chat.
        - `next_question()`: A handler to send next question.
        - `stop_quiz()`: A handler to stop quiz immediately.
    """
    @staticmethod
    def start(update: Update, context: CallbackContext) -> None:
        """`/start` handler (static method)."""
        if update.effective_chat:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="I'm a bot, please talk to me!")

    @staticmethod
    def new_quiz(update: Update, context: CallbackContext) -> None:
        """Handler to initiate a quiz session (static method)."""
        if not isinstance(context.chat_data, dict):
            raise AssertionError
        if update.effective_chat:
            if context.chat_data.get('question_number', -1) == -1:
                options = ['quiz1', 'quiz2']
                keyboard = [[
                    InlineKeyboardButton(i, callback_data=i) for i in options
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                context.chat_data['message'] = context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Choose your quiz. (Admin only)",
                    reply_markup=reply_markup)
            else:
                context.chat_data['message'] = context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="A quiz is already running, close it first!")

    @staticmethod
    def choose_quiz(update: Update, context: CallbackContext) -> None:
        """Handler to choose amongst the two quizzes (static method)."""
        chosen = update.callback_query.data
        if not isinstance(context.chat_data, dict):
            raise AssertionError
        if chosen == "quiz1":
            context.chat_data['current'] = SHEET1
        elif chosen == "quiz2":
            context.chat_data['current'] = SHEET2
        response = get(context.chat_data['current'])
        result = response.json()
        context.chat_data["qlist"] = [Question(**i) for i in result]
        keyboard = [[
            InlineKeyboardButton("start", callback_data="start_quiz")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.chat_data['message'] = context.bot.edit_message_text(
            text=f"{chosen} selected!",
            chat_id=context.chat_data['message'].chat.id,
            message_id=context.chat_data['message'].message_id,
            reply_markup=reply_markup)

    @staticmethod
    def parse_question(
            question: Question
    ) -> tuple[str, list[list[InlineKeyboardButton]]]:
        """A method returning a question statement with options as buttons."""
        statement = question.ask_question()
        options = question.get_options()
        keyboard = [[
            InlineKeyboardButton(str(i + 1), callback_data=f'option_{i}')
            for i in range(len(options))
        ]]

        return (statement, keyboard)

    @staticmethod
    def start_quiz(update: Update, context: CallbackContext) -> None:
        """A handler to start the quiz."""
        if not isinstance(context.chat_data, dict):
            raise AssertionError
        context.chat_data['question_number'] = 0
        context.chat_data['marksheet'] = {}
        context.chat_data['question_attempted_by'] = []
        msg_text, option_keyboard = Quiz.parse_question(
            context.chat_data['qlist'][context.chat_data['question_number']])
        option_keyboard.append(
            [InlineKeyboardButton("Next (Admin Only)", callback_data="next")])
        context.chat_data['message'] = context.bot.edit_message_text(
            text=msg_text,
            chat_id=context.chat_data['message'].chat.id,
            message_id=context.chat_data['message'].message_id,
            reply_markup=InlineKeyboardMarkup(option_keyboard))
        if not isinstance(context.chat_data['message'], Message):
            raise AssertionError
        context.chat_data['message'].pin()

    @staticmethod
    def check_option(update: Update, context: CallbackContext) -> None:
        """A handler to validate the option opted."""
        if not update.effective_chat or not update.effective_user:
            return
        if not isinstance(context.chat_data, dict):
            raise AssertionError
        if update.effective_user.id not in context.chat_data[
                'question_attempted_by']:
            chosen = int(update.callback_query.data.split('_')[1])
            que: Question = context.chat_data['qlist'][
                context.chat_data['question_number']]
            if context.chat_data['marksheet'].get(update.effective_user.id,
                                                  None) is None:
                context.chat_data['marksheet'][int(
                    update.effective_user.id)] = {
                        'name':
                        escape_markdown(update.effective_user.full_name),
                        'score': 0
                    }
            if que.is_correct(que.get_options()[chosen]):
                context.chat_data['marksheet'][
                    update.effective_user.id]['score'] += 1
                context.bot.answer_callback_query(
                    callback_query_id=update.callback_query.id,
                    text="Correct!",
                    show_alert=True)
                context.chat_data['question_attempted_by'].append(
                    update.effective_user.id)
            else:
                context.bot.answer_callback_query(
                    callback_query_id=update.callback_query.id,
                    text="Incorrect!, " +
                    f"the correct answer is: {que.get_correct()}",
                    show_alert=True)
            context.chat_data['question_attempted_by'].append(
                update.effective_user.id)
        else:
            context.bot.answer_callback_query(
                callback_query_id=update.callback_query.id,
                text="You can only attempt once!",
                show_alert=True)

    @staticmethod
    def send_scoreboard(context: CallbackContext) -> None:
        """A handler to send scoreboard to the chat."""
        if not isinstance(context.chat_data, dict):
            raise AssertionError
        context.chat_data['question_number'] = -1
        msg_text = "*Quiz Over*! \n*ScoreBoard*: \n\n"
        values = sorted(context.chat_data['marksheet'].items(),
                        key=lambda x: x[1]['score'],
                        reverse=True)
        data = [
            f"{mention_markdown(id, attendee['name'])} : {attendee['score']}"
            for id, attendee in values
        ]
        data_str = [
            f"{rank}. {name_score}"
            for rank, name_score in enumerate(data, start=1)
        ]
        scoreboard = "\n".join(data_str)
        msg_text += f'{scoreboard}'
        context.bot.delete_message(
            chat_id=context.chat_data['message'].chat.id,
            message_id=context.chat_data['message'].message_id)
        context.bot.send_message(text=msg_text,
                                 chat_id=context.chat_data['message'].chat.id,
                                 parse_mode=ParseMode.MARKDOWN).pin()

    @staticmethod
    def next_question(update: Update, context: CallbackContext) -> None:
        """A handler to send next question."""
        update.callback_query.answer()
        if not isinstance(context.chat_data, dict):
            raise AssertionError
        if context.chat_data['question_number'] < (
                len(context.chat_data['qlist']) - 1):
            context.chat_data['question_number'] += 1
            context.chat_data['question_attempted_by'] = []
            msg_text, option_keyboard = Quiz.parse_question(
                context.chat_data['qlist'][
                    context.chat_data['question_number']])
            option_keyboard.append([
                InlineKeyboardButton("Next (Admin Only)", callback_data="next")
            ])
            context.chat_data['message'] = context.bot.edit_message_text(
                text=msg_text,
                chat_id=context.chat_data['message'].chat.id,
                message_id=context.chat_data['message'].message_id,
                reply_markup=InlineKeyboardMarkup(option_keyboard),
                parse_mode=ParseMode.MARKDOWN)
        else:
            Quiz.send_scoreboard(context=context)

    @staticmethod
    def stop_quiz(update: Update, context: CallbackContext) -> None:
        """A handler to stop quiz immediately."""
        if not isinstance(context.chat_data, dict):
            raise AssertionError
        if context.chat_data.get('question_number', -1) != -1:
            Quiz.send_scoreboard(context=context)
        elif update.effective_message:
            update.effective_message.reply_text(
                "No quiz was there to stop :p")
