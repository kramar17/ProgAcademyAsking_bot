import telebot
from dotenv import load_dotenv
import os
import json
from bot_functions import load_questions, save_results, consolidate_scores_and_recommend

load_dotenv('.env')

# Создание объекта бота
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(token=TOKEN)

# Загружаем вопросы из JSON файла
def load_questions(filename="questions.json"):
    with open(filename, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    return questions

# handler the /start command
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создаем клавиатуру
    button = telebot.types.KeyboardButton("Начать")  # Создаем кнопку
    markup.add(button)  # Добавляем кнопку на клавиатуру

    bot.send_message(message.chat.id, "Привет! Нажмите на кнопку ниже, чтобы пройти опрос:", reply_markup=markup)


# Обработчик для кнопки "Начать"
@bot.message_handler(func=lambda message: message.text == "Начать")
def handle_start_survey(message):
    survey(message)


# handler the /help command
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Для начала опроса используйте команду /survey.")

# handler the /survey command
@bot.message_handler(commands=['survey'])
def survey(message):
    questions = load_questions()  # Загружаем вопросы
    user_results = {}
    user_scores = {animal.lower(): 0 for animal in
                   set(animal for question in questions for ans in question['answers'].values() for animal in ans)}

    # Начинаем задавать вопросы
    ask_question(message, questions, user_results, user_scores, 0)


def ask_question(message, questions, user_results, user_scores, question_index):
    if question_index < len(questions):
        question = questions[question_index]
        question_text = question['text']
        answers = question['answers']

        # Формирование кнопок для ответов
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for answer_text in answers.keys():
            markup.add(answer_text)

        # Отправка вопроса с вариантами ответов
        bot.send_message(message.chat.id, question_text, reply_markup=markup)
        bot.register_next_step_handler(message, process_answer, answers, user_results, user_scores, question_index)
    else:
        # Если все вопросы заданы, сохраняем результаты
        save_results(message, user_results, user_scores)  # Передаем объект message для доступа к данным пользователя
        bot.send_message(message.chat.id, consolidate_scores_and_recommend(user_scores))
        bot.send_message(message.chat.id, "Спасибо за участие в опросе!")


def process_answer(message, answers, user_results, user_scores, question_index):
    user_answer = message.text
    question = load_questions()[question_index]

    if user_answer in answers:
        user_results[question['text']] = {
            'answer': user_answer,
            'categories': answers[user_answer]  # Сохраняем категории, к которым добавляется балл
        }
        for category in answers[user_answer]:
            # Приводим категорию к нижнему регистру
            user_scores[category.lower()] += 1  # Увеличиваем счетчик баллов за ответ
        bot.send_message(message.chat.id, f"Вы выбрали: {user_answer}.")
        ask_question(message, load_questions(), user_results, user_scores, question_index + 1)  # Задаем следующий вопрос
    else:
        bot.send_message(message.chat.id, "Некорректный ответ. Пожалуйста, выберите вариант из списка.")
        bot.register_next_step_handler(message, process_answer, answers, user_results, user_scores, question_index)


def save_results(message, user_results, user_scores, filename="results.txt"):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"User ID: {message.chat.id}\n")
        if message.from_user.username:
            f.write(f"Username: @{message.from_user.username}\n")
        f.write(f"User Full Name: {message.from_user.first_name} {message.from_user.last_name}\n")
        for question, result in user_results.items():
            f.write(f"{question}: {result['answer']} (категории: {', '.join(result['categories'])})\n")
        f.write(f"{user_scores}\n\n")


if __name__ == '__main__':
    bot.polling()
