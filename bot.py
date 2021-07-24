#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
import logging
from question import Question, QuestionList
from config import Config
from requests import get
from ptbcontrib.roles import setup_roles, RolesHandler
from autologging import logged, traced
from telegram.utils.helpers import mention_markdown, escape_markdown


@traced
@logged
class Quiz:
    def __init__(self, token: str) -> None:
        self.TOKEN = token

    def initilize(self) -> None:
        updater = Updater(token=Config.api)
        dispatcher = updater.dispatcher
        roles = setup_roles(dispatcher)

        quiz_handler = CommandHandler('quiz', self.new_quiz)
        choose_quiz_handler = CallbackQueryHandler(self.choose_quiz,
                                                   pattern=r'^quiz[1-2]$')
        start_button_handler = CallbackQueryHandler(self.start_quiz,
                                                    pattern=r'^start_quiz$')
        check_option_handler = CallbackQueryHandler(self.check_option,
                                                    pattern=r'^option\_[0-3]$')
        next_question_handler = CallbackQueryHandler(self.next_question,
                                                     pattern=r'^next$')
        stop_button_handler = CommandHandler('stop', self.stop_quiz)

        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(RolesHandler(quiz_handler, roles.chat_admins))
        dispatcher.add_handler(
            RolesHandler(choose_quiz_handler, roles.chat_admins))
        dispatcher.add_handler(
            RolesHandler(start_button_handler, roles.chat_admins))
        dispatcher.add_handler(check_option_handler)
        dispatcher.add_handler(
            RolesHandler(next_question_handler, roles.chat_admins))
        dispatcher.add_handler(
            RolesHandler(stop_button_handler, roles.chat_admins))

        updater.start_webhook(listen="0.0.0.0",
                              port=int(Config.PORT),
                              url_path=self.TOKEN)
        updater.bot.setWebhook(Config.heroku + self.TOKEN)

    @staticmethod
    def start(update: Update, context: CallbackContext) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm a bot, please talk to me!")

    def new_quiz(self, update: Update, context: CallbackContext):
        if context.chat_data.get('question_number', -1) == -1:
            options = ['quiz1', 'quiz2']
            keyboard = [[
                InlineKeyboardButton(i, callback_data=i) for i in options
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.message = context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Choose your quiz. (Admin only)",
                reply_markup=reply_markup)
        else:
            self.message = context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="A quiz is already running, close it first!")

    def choose_quiz(self, update: Update, context: CallbackContext) -> None:
        chosen = update.callback_query.data
        if chosen == "quiz1":
            self.current = Config.sheet1
        elif chosen == "quiz2":
            self.current = Config.sheet2
        response = get(self.current)
        result = response.json()
        context.chat_data["qlist"] = QuestionList(result)
        keyboard = [[
            InlineKeyboardButton("start", callback_data="start_quiz")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.message = context.bot.edit_message_text(
            text=f"{chosen} selected!",
            chat_id=self.message.chat.id,
            message_id=self.message.message_id,
            reply_markup=reply_markup)

    @staticmethod
    def parse_question(
            question: Question
    ) -> tuple[str, list[list[InlineKeyboardButton]]]:
        statement = question.ask_question()
        options = question.get_options()
        keyboard = [[
            InlineKeyboardButton(str(i + 1), callback_data=f'option_{i}')
            for i in range(len(options))
        ]]

        return (statement, keyboard)

    def start_quiz(self, update: Update, context: CallbackContext) -> None:
        context.chat_data['question_number'] = 0
        context.chat_data['marksheet'] = {}
        context.chat_data['question_attempted_by'] = []
        msg_text, option_keyboard = self.parse_question(
            context.chat_data['qlist'][context.chat_data['question_number']])
        option_keyboard.append(
            [InlineKeyboardButton("Next (Admin Only)", callback_data="next")])
        self.message = context.bot.edit_message_text(
            text=msg_text,
            chat_id=self.message.chat.id,
            message_id=self.message.message_id,
            reply_markup=InlineKeyboardMarkup(option_keyboard))
        self.message.pin()

    @staticmethod
    def check_option(update: Update, context: CallbackContext) -> None:
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
                    text=
                    f"Incorrect!, the correct answer is: {que.get_correct()}",
                    show_alert=True)
            context.chat_data['question_attempted_by'].append(
                update.effective_user.id)
        else:
            context.bot.answer_callback_query(
                callback_query_id=update.callback_query.id,
                text="You can only attempt once!",
                show_alert=True)

    def next_question(self, update: Update, context: CallbackContext) -> None:
        update.callback_query.answer()
        if context.chat_data['question_number'] < (
                len(context.chat_data['qlist']) - 1):
            context.chat_data['question_number'] += 1
            context.chat_data['question_attempted_by'] = []
            msg_text, option_keyboard = self.parse_question(
                context.chat_data['qlist'][
                    context.chat_data['question_number']])
            option_keyboard.append([
                InlineKeyboardButton("Next (Admin Only)", callback_data="next")
            ])
            self.message = context.bot.edit_message_text(
                text=msg_text,
                chat_id=self.message.chat.id,
                message_id=self.message.message_id,
                reply_markup=InlineKeyboardMarkup(option_keyboard),
                parse_mode=ParseMode.MARKDOWN)
        else:
            context.chat_data['question_number'] = -1
            msg_text = "**Quiz Over**!"
            data = [
                f"{mention_markdown(id, attendee['name'])} : {attendee['score']}"
                for id, attendee in context.chat_data['marksheet'].items()
            ]
            scoreboard = "\n".join(data)
            msg_text += "\n" + '**Scoreboard:**' + "\n" + f'{scoreboard}'
            context.bot.delete_message(chat_id=self.message.chat.id,
                                       message_id=self.message.message_id)
            score_msg = context.bot.send_message(text=msg_text,
                                                 chat_id=self.message.chat.id,
                                                 parse_mode=ParseMode.MARKDOWN)
            score_msg.pin()

    def stop_quiz(self, update: Update, context: CallbackContext) -> None:
        if context.chat_data.get('question_number', 0) != -1:
            context.chat_data['question_number'] = -1
            msg = "Quiz stopped successfully."
            data = []
            data = [
                f"{mention_markdown(id, attendee['name'])} : {attendee['score']}"
                for id, attendee in context.chat_data['marksheet'].items()
            ]
            scoreboard = "\n".join(data)
            msg += "\n" + '**Scoreboard:**' + "\n" + f'{scoreboard}'
            context.bot.delete_message(chat_id=self.message.chat.id,
                                       message_id=self.message.message_id)
        else:
            msg = "No quiz was there to stop :p"
        score_msg = update.message.reply_text(msg,
                                              parse_mode=ParseMode.MARKDOWN)
        score_msg.pin()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format=
        '%(levelname)s:%(asctime)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s',
        level=logging.WARN)
    if not (Config.api == "None" or Config.sheet1 == "None"
            or Config.sheet2 == "None" or Config.heroku == "None"):
        quiz_bot = Quiz(Config.api)
        quiz_bot.initilize()
    else:
        logger.error("Check environment variables")
