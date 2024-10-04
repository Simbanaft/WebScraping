import requests
import csv
import os
import time


def get_exchange_rate_by_date(date_url):
    """
    Получает данные о курсе валюты по указанной дате.
    """
    # Если URL относительный, добавляем протокол и домен
    if date_url.startswith("/"):
        url = f"https://www.cbr-xml-daily.ru{date_url}"  # Добавляем протокол и домен
    else:
        url = date_url  # Если уже полный URL.

    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    return None


def extract_value(data, currency_code):
    """
    Извлекает значение валюты по её коду из данных.
    """
    try:
        return data['Valute'][currency_code]['Value']
    except KeyError:
        return None


def write_to_csv(dataset, output_path):
    """
    Записывает данные в CSV файл.
    """
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['date', 'Value']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

        writer.writeheader()
        for row in dataset:
            writer.writerow(row)


def create_directory(directory):
    """
    Создает директорию, если она не существует.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def main():
    """
    Основная функция программы. Запрашивает начальную и конечную дату,
    собирает данные о валюте за этот период и сохраняет их в CSV файл.
    """
    # Запрос начальной и конечной даты
    start_date_str = input("Введите начальную дату (гггг/мм/дд): ")
    end_date_str = input("Введите конечную дату (гггг/мм/дд): ")

    # Преобразуем строки в формат, пригодный для имени файла (замена слэшей)
    start_date_filename = start_date_str.replace("/", "-")
    end_date_filename = end_date_str.replace("/", "-")

    # Код валюты для AMD
    currency_code = "AMD"

    # Путь для сохранения файла
    output_directory = "currency_datasets"
    create_directory(output_directory)

    # Формируем корректный путь к файлу
    output_path = os.path.join(output_directory, f"{start_date_filename}_{end_date_filename}.csv")

    # Список для хранения данных
    dataset = []

    # Начальный URL для конца периода
    current_url = f"/archive/{end_date_str}/daily_json.js"

    while True:
        # Запрашиваем данные
        data = get_exchange_rate_by_date(current_url)

        if data:
            # Извлекаем дату и значение для валюты AMD
            date = data['Date'][:10].replace("-", "/")
            value = extract_value(data, currency_code)

            if value is not None:
                dataset.append({'date': date, 'Value': value})
            else:
                print(f"Валюта {currency_code} не найдена на дату {date}")

            # Проверяем, не дошли ли до начальной даты
            if date <= start_date_str:
                print("Достигнута начальная дата")
                break

            # Получаем предыдущий URL
            previous_url = data.get('PreviousURL')
            if not previous_url:
                print("Не удалось найти предыдущую дату")
                break

            # Формируем следующий URL
            current_url = previous_url.replace("//", "https://")
        else:
            print(f"Не удалось получить данные за URL {current_url}")
            break

        # Пауза между запросами (не более 5 запросов в секунду)
        time.sleep(0.2)

    # Записываем данные в CSV файл
    write_to_csv(dataset, output_path)
    print(f"Данные сохранены в файл: {output_path}")


if __name__ == "__main__":
    main()