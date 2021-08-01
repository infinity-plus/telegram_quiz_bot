from quiz_bot import TOKEN, HEROKU, PORT
from quiz_bot.bot import Quiz
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from ptbcontrib.roles import setup_roles, RolesHandler


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    roles = setup_roles(dispatcher)

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

    dispatcher.add_handler(CommandHandler('start', Quiz.start))
    dispatcher.add_handler(RolesHandler(quiz_handler, roles.chat_admins))
    dispatcher.add_handler(RolesHandler(choose_quiz_handler,
                                        roles.chat_admins))
    dispatcher.add_handler(
        RolesHandler(start_button_handler, roles.chat_admins))
    dispatcher.add_handler(check_option_handler)
    dispatcher.add_handler(
        RolesHandler(next_question_handler, roles.chat_admins))
    dispatcher.add_handler(RolesHandler(stop_button_handler,
                                        roles.chat_admins))

    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook(HEROKU + TOKEN)


if __name__ == "__main__":
    main()