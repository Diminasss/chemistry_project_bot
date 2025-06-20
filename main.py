from telebot import TeleBot
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from time import sleep

from questions import questions, answers
from os import getenv
from dotenv import load_dotenv

load_dotenv()

bot: TeleBot = TeleBot(getenv("TELEGRAM_TOKEN"))

users_and_pages: dict[int, int] = {}


def make_pages_text() -> list[str]:
    page: str = "Выберите вопрос: \n"
    counter: int = 0
    pages: list[str] = []
    for question in questions:
        counter += 1
        page += f"{str(counter)}. {question}\n"
        if counter % 9 == 0:
            pages.append(page)
            page = "Выберите вопрос: \n"
    if counter != 0:
        pages.append(page)
    return pages


def make_pages_markup() -> list[InlineKeyboardMarkup]:
    temporary_buttons: list[InlineKeyboardButton] = []
    markups: list[InlineKeyboardMarkup] = []
    counter: int = 0
    for x in range(len(questions)):
        counter += 1
        temporary_buttons.append(InlineKeyboardButton(text=str(x + 1), callback_data=str(x)))
        if counter % 9 == 0:
            markup: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=3).add(*temporary_buttons)
            temporary_buttons = []
            markups.append(markup)
    if len(temporary_buttons) != 0:
        markups.append(InlineKeyboardMarkup(row_width=3).add(*temporary_buttons))

    markups[0].add(InlineKeyboardButton(text=">", callback_data=">"))
    markups[len(markups) - 1].add(InlineKeyboardButton(text="<", callback_data="<"))
    for x in range(1, len(markups) - 1):
        markups[x].add(InlineKeyboardButton(text="<", callback_data="<"),
                       InlineKeyboardButton(text=">", callback_data=">"))

    return markups


text_pages: list[str] = make_pages_text()
markup_pages: list[InlineKeyboardMarkup] = make_pages_markup()


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    print(message.chat.id)
    inline_button: InlineKeyboardButton = InlineKeyboardButton(text="Главное меню", callback_data="main_menu")
    inline_markup: InlineKeyboardMarkup = InlineKeyboardMarkup().add(inline_button)
    bot.send_message(
        chat_id=message.chat.id,
        text="Вас приветствует Бот Антигастрит. \n\nВы можете узнать ответ на интересующие вас вопросы в главном меню!",
        reply_markup=inline_markup,
        disable_notification=True
    )


@bot.message_handler(commands=['menu'])
def menu(message: Message) -> None:
    users_and_pages[message.chat.id] = 0

    bot.send_message(chat_id=message.chat.id, text=text_pages[users_and_pages[message.chat.id]],
                     reply_markup=markup_pages[users_and_pages[message.chat.id]])


def fuse(chat_id: int) -> None:
    if chat_id not in users_and_pages:
        users_and_pages[chat_id] = 0


@bot.callback_query_handler(func=lambda call: True)
def answer_question(call: CallbackQuery) -> None:
    print(call.data)
    if call.data.isdigit():
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=answers[int(call.data)],
                              reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Назад", callback_data="back")))
    elif call.data == "back":
        fuse(call.message.chat.id)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text_pages[users_and_pages[call.message.chat.id]],
                              reply_markup=markup_pages[users_and_pages[call.message.chat.id]])
    elif call.data == "main_menu":
        menu(call.message)
    elif call.data == ">":
        fuse(call.message.chat.id)
        users_and_pages[call.message.chat.id] += 1
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text_pages[users_and_pages[call.message.chat.id]],
                              reply_markup=markup_pages[users_and_pages[call.message.chat.id]])
    elif call.data == "<":
        if call.message.chat.id not in users_and_pages:
            users_and_pages[call.message.chat.id] = 1
        users_and_pages[call.message.chat.id] -= 1
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=text_pages[users_and_pages[call.message.chat.id]],
                              reply_markup=markup_pages[users_and_pages[call.message.chat.id]])


if __name__ == "__main__":
    if len(questions) != len(answers):
        print("Внимание, программа не может работать, так как количество вопросов отличается от количества ответов.")
        exit(228)
    while True:
        try:
            print('Запуск')
            bot.polling(none_stop=True)

        except KeyboardInterrupt as e:
            print("Ручной выход")
            exit(0)

        except Exception as e:
            print(f"Ошибка {e}")
            sleep(5)
