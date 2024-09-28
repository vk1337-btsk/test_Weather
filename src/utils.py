import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from .API_manager import APIManager
from .DB_manager import DBManager
from .Excel_manager import ExcelManager


def get_data_from_env() -> None:
    """Получает данные из переменных окружения.

    Returns:
        args: широта, долгота и периодичность запросов.
    """

    # Получаем путь к файлу, находящемуся на уровень выше
    BASE_DIR = Path(__file__).resolve().parent.parent
    dotenv_path = BASE_DIR / ".env"

    # Проверяем существование файла
    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=True)

    LATITUDE = float(os.environ.get("LATITUDE", 52.54))  # Широта
    LONGITUDE = float(os.environ.get("LONGITUDE", 13.41))  # Долгота
    FREQUENCY = int(os.environ.get("FREQUENCY", 180))  # Периодичность запросов

    return LATITUDE, LONGITUDE, FREQUENCY


async def fetch_and_store_weather_data(
    weather_api: APIManager, db_manager: DBManager, frequency: int, stop_event: asyncio.Event
) -> None:
    """Асинхронная функция для периодической выборки данных о погоде и их сохранения в базу данных.

    Args:
        weather_api (APIManager): менеджер api.
        db_manager (DBManager): менеджер базы данных.
        frequency (int): периодичность запросов.
        stop_event (asyncio.Event): сигнал о завершении программы.
    """

    while not stop_event.is_set():
        try:
            data = await weather_api.get_weather_data()
            await db_manager.add_weather_data(data)
        except Exception as e:
            print(f"Ошибка при получении или сохранении данных: {e}")

        # Проверяем, установлено ли событие после ожидания
        if stop_event.is_set():
            break

        # Ожидание перед перед следующим запросом
        await asyncio.sleep(frequency)


async def menu(db_manager: DBManager, excel_manager: ExcelManager, stop_event: asyncio.Event) -> None:
    """Асинхронное меню для управления программой.

    Args:
        db_manager (DBManager): менеджер базы данных.
        excel_manager (ExcelManager): менеджер Excel.
        stop_event (asyncio.Event): сигнал о завершении программы.
    """

    while True:
        print("\nМеню:")
        print("1. Экспорт данных в Excel.")
        print("2. Выйти из программы.")

        choice = await asyncio.get_event_loop().run_in_executor(None, input, "Выберите действие (1 или 2): ")

        if choice == "1":
            print("Экспорт данных в Excel...")
            await excel_manager.create_excel_file()
            data = await db_manager.get_all_weather_data()
            await excel_manager.add_weather_data_to_excel(data)
            print("Экспорт завершен.")
        elif choice == "2":
            print("Выход из программы...")
            stop_event.set()
            break
        else:
            print("Неверный выбор. Пожалуйста, попробуйте снова.")
