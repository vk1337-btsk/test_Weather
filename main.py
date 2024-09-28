import asyncio

from src.API_manager import APIManager
from src.DB_manager import DBManager
from src.Excel_manager import ExcelManager
from src.utils import fetch_and_store_weather_data, get_data_from_env, menu


async def main() -> None:
    """Основная асинхронная функция приложения."""

    # Получаем переменные окружения
    LATITUDE, LONGITUDE, FREQUENCY = get_data_from_env()
    print(LATITUDE, LONGITUDE, FREQUENCY)
    # Инициализия: менеджера API; менеджера БД с инициализацией БД; менеджера для работы с Excel
    weather_api = APIManager(LATITUDE, LONGITUDE)

    db_manager = DBManager()
    await db_manager.init_db()

    excel_manager = ExcelManager()

    print(
        f"Запуск программы получения данных о погоде по координатам: {LATITUDE}° c.ш. и {LONGITUDE}° в.д.\n",
        f"Периодичность отправки запросов: {FREQUENCY} c.",
        sep="",
    )

    # Создаем событие для остановки
    stop_event = asyncio.Event()

    # Параллельный запуск в фоновом режиме функций для запроса и сохранения данных в БД и фунции управления приложением
    await asyncio.gather(
        fetch_and_store_weather_data(weather_api, db_manager, FREQUENCY, stop_event),
        menu(db_manager, excel_manager, stop_event),
    )


if __name__ == "__main__":

    asyncio.run(main())
