import telebot
import os
import dotenv
from src import gemini_api
from src.get_all_agents import get_agents
import json
from src.create_agent import add_agent

dotenv.load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT"))

with open('users.json', 'r', encoding='utf-8') as file:
    user_data = json.load(file)

agents = get_agents()


def draw_buttons_under_message():
    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.add(telebot.types.InlineKeyboardButton(text="Стандарт", callback_data="default"))

    for agent in agents:
        button = telebot.types.InlineKeyboardButton(text=agent, callback_data=agent)
        keyboard.add(button)

    keyboard.add(telebot.types.InlineKeyboardButton(text="Добавить агента", callback_data="create_agent"))

    return keyboard


def mini_markup():
    markup = telebot.types.InlineKeyboardMarkup()

    button = telebot.types.InlineKeyboardButton(
        text="Поменять агента",
        callback_data="change_agent")

    markup.add(button)

    return markup


@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.chat.id
    with open('users.json', 'r+', encoding='utf-8') as f:
        users = json.load(f)

        if user_id not in users:  # если пользователь новый - добавляем его в user_data
            users[user_id] = {"agent": "default"}

            f.seek(0)
            json.dump(users, f, ensure_ascii=False, indent=4)
            f.truncate()

    buttons = draw_buttons_under_message()
    bot.send_message(message.chat.id, "Hello, I'm your virtual AI assistant. If you want, you can first choose"
                                      " an agent. If not, then ask any question and I'll try to answer",
                     reply_markup=buttons)


@bot.message_handler(content_types=["text"])
def send_message(message):
    current_agent = user_data[str(message.chat.id)]["agent"]
    print(current_agent)  # проверка

    msg = bot.send_message(message.chat.id, "Ваш запрос обрабатывается...")

    bot.edit_message_text(
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        text=gemini_api.gemini_answer(message.text, agent=current_agent),
        reply_markup=mini_markup()
    )


@bot.message_handler(commands=agents)
def agent_work(message):
    bot.send_message(message.chat.id, f"Вы выбрали агента {message}. Напишите ваш запрос")

    user_id = message.chat.id
    user_data[user_id]["agent"] = message  # присвоение пользователю agent


@bot.callback_query_handler(func=lambda call: call.data == 'return')
def handle_callback(call):
    buttons = draw_buttons_under_message()
    bot.send_message(call.message.chat.id, "Вы можете выбрать бота или просто ввести сообщение", reply_markup=buttons)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(text="Вернуться назад", callback_data="return"))

    user_id = str(call.message.chat.id)
    if call.data == "change_agent":
        bot.send_message(call.message.chat.id, text="Выбираем нового агента", reply_markup=draw_buttons_under_message())
    elif call.data == "create_agent":
        msg = bot.send_message(call.message.chat.id, text="Введите название нового агента", reply_markup=keyboard)
        bot.register_next_step_handler(msg, get_name)
    else:
        bot.send_message(call.message.chat.id, text=f"Вы выбрали {call.data}. Напишите ваш запрос",
                         reply_markup=mini_markup())
        with open('users.json', 'r+', encoding='utf-8') as f1:
            users = json.load(f1)
            users[user_id]["agent"] = call.data
            user_data[user_id]["agent"] = call.data

            f1.seek(0)
            json.dump(users, f1, ensure_ascii=False, indent=4)
            f1.truncate()


def get_name(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(text="Вернуться назад", callback_data="return"))  # дописать или переписать

    agent_name = message.text  # Текст, который ввел пользователь
    bot.send_message(message.chat.id, f"Имя вашего агента - {agent_name}!")

    msg2 = bot.send_message(message.chat.id, f"Теперь введите характеристику для вашего агента", reply_markup=keyboard)
    bot.register_next_step_handler(msg2, get_characteristics, agent_name)


def get_characteristics(message, agent_name):
    agent_characteristics = message.text
    try:
        add_agent(agent_name, agent_characteristics)
        global agents
        agents = get_agents()
        bot.send_message(message.chat.id, f"Характеристика нового агента записана!")
        bot.send_message(message.chat.id, "Теперь вы можете выбрать бота!", reply_markup=draw_buttons_under_message())
    except Exception as e:
        bot.send_message(message.chat.id, f"Что-то пошло не так")
        print(e)


if __name__ == "__main__":
    bot.infinity_polling()
