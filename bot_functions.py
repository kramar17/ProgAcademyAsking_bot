import json


class Question:
    def __init__(self, text, sort_order, answers):
        self.text = text
        self.sort_order = sort_order
        self.answers = answers

    def to_dict(self):
        return {
            'text': self.text,
            'sort_order': self.sort_order,
            'answers': self.answers
        }


def create_question(animal_list, filename):
    question_text = input("Введите текст вопроса: ")

    while True:
        sort_order_input = input("Введите порядок вопроса (число): ")
        try:
            sort_order = int(sort_order_input)
            break
        except ValueError:
            print("Пожалуйста, введите корректное число для порядка вопроса.")

    answers = {}
    print("\nДобавление вариантов ответа (нажмите Enter, чтобы завершить)")
    while True:
        answer_text = input("Введите текст ответа: (Enter чтоб завершить")
        if not answer_text:
            break
        categories_input = input("Введите категории (через запятую), к которым этот ответ добавляет балл: ")
        categories = [category.strip() for category in categories_input.split(',')]

        # Проверка на существование категории
        for category in categories:
            if category.lower() not in (animal.lower() for animal in animal_list):
                print(f"Категория '{category}' не является допустимой. Пожалуйста, введите другое животное.")
                break
        else:
            answers[answer_text] = categories

    question = Question(question_text, sort_order, answers)

    # Сохранение в файл после завершения вопроса
    save_question_to_file(question, filename)

    return question


def save_question_to_file(question, filename):
    try:
        # Чтение существующих вопросов из файла
        with open(filename, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        questions = []  # Если файл не существует, создаем новый список

    questions.append(question.to_dict())

    # Сохранение обновленного списка вопросов в файл
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)

    print(f"\nВопрос '{question.text}' успешно сохранен в {filename}")


# Пример использования
if __name__ == "__main__":
    animal_list = ["Кот", "Собака", "Попугай", "Рыбка"]
    filename = "questions.json"

    print("Создание вопросов для опроса")
    while True:
        create_question(animal_list, filename)
        more_questions = input("Хотите добавить еще один вопрос? (да/нет): ").strip().lower()
        if more_questions != 'да':
            break


def load_questions(filename="questions.json"):
    with open(filename, 'r', encoding='utf-8') as f:
        questions = json.load(f)
    return questions


def save_results(user_id, results, filename="results.txt"):
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"User ID: {user_id}\n")
        for question, answer in results.items():
            f.write(f"{question}: {answer}\n")
        f.write("\n")


def consolidate_scores_and_recommend(score_dict):
    consolidated = {}
    for animal, score in score_dict.items():
        key = animal.lower()  # Игнорируем регистр
        if key in consolidated:
            consolidated[key] += score
        else:
            consolidated[key] = score

    # Находим максимальное количество баллов
    max_score = max(consolidated.values())
    # Находим животных с максимальным количеством баллов
    recommendations = [animal for animal, score in consolidated.items() if score == max_score]

    # Формируем текст с рекомендациями
    recommendation_text = "Исходя из ваших ответов мы рекомендуем вам: " + ", ".join(recommendations)

    return recommendation_text