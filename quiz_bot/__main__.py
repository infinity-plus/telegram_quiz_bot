from quiz_bot import TOKEN, HEROKU, PORT, OWNER
from quiz_bot.bot import Quiz
from quiz_bot.sql.quizmasters import add_quizmaster, rm_quizmaster, get_quizmasters
from telegram import Update, User
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,
                          CallbackContext, Filters)
from ptbcontrib.roles import setup_roles, RolesHandler


def add_to_quizmasters(update: Update, context: CallbackContext):
    if update.effective_message:
        user: User = update.effective_message.reply_to_message.from_user
        msg = add_quizmaster(user.id)
        context.roles['quizmasters'].add_member(user.id)
        update.effective_message.reply_text(text=msg)


def remove_from_quizmasters(update: Update, context: CallbackContext):
    if update.effective_message:
        user: User = update.effective_message.reply_to_message.from_user
        msg = rm_quizmaster(user.id)
        context.roles['quizmasters'].kick_member(user.id)
        update.effective_message.reply_text(text=msg)


def list_quizmasters(update: Update, context: CallbackContext):
    if update.effective_message:
        msg = '\n'.join(map(str, get_quizmasters()))
        update.effective_message.reply_text(text=msg)


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    roles = setup_roles(dispatcher)
    if 'quizmasters' not in roles:
        roles.add_role('quizmasters')
    quizmasters = roles['quizmasters']
    curr_list = get_quizmasters()
    quizmasters.add_member(curr_list)
    if OWNER not in quizmasters.chat_ids:
        quizmasters.add_member(OWNER)

    add_role_handler = CommandHandler('add',
                                      add_to_quizmasters,
                                      filters=Filters.reply)
    remove_role_handler = CommandHandler('remove',
                                         remove_from_quizmasters,
                                         filters=Filters.reply)
    quiz_handler = CommandHandler('quiz', Quiz.new_quiz)
    choose_quiz_handler = CallbackQueryHandler(Quiz.choose_quiz,
                                               pattern=r'^quiz[1-2]$')
    start_button_handler = CallbackQueryHandler(Quiz.start_quiz,
                                                pattern=r'^start_quiz$')
    check_option_handler = CallbackQueryHandler(Quiz.check_option,
                                                pattern=r'^option\_[0-3]$')
    next_question_handler = CallbackQueryHandler(Quiz.next_question,
                                                 pattern=r'^next$')
    stop_button_handler = CommandHandler('stop', Quiz.stop_quiz)

    dispatcher.add_handler(RolesHandler(add_role_handler, quizmasters))
    dispatcher.add_handler(RolesHandler(remove_role_handler, quizmasters))
    dispatcher.add_handler(CommandHandler('start', Quiz.start))
    dispatcher.add_handler(RolesHandler(quiz_handler, quizmasters))
    dispatcher.add_handler(RolesHandler(choose_quiz_handler, quizmasters))
    dispatcher.add_handler(RolesHandler(start_button_handler, quizmasters))
    dispatcher.add_handler(check_option_handler)
    dispatcher.add_handler(RolesHandler(next_question_handler, quizmasters))
    dispatcher.add_handler(RolesHandler(stop_button_handler, quizmasters))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN,
                          webhook_url=HEROKU + TOKEN)


if __name__ == "__main__":
    main()
