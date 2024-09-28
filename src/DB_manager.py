from sqlalchemy import Column, DateTime, Float, Integer, String, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class WeatherDataModel(Base):
    """Модель для хранения данных о погоде."""

    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(Float, nullable=False)  # Широта
    longitude = Column(Float, nullable=False)  # Долгота

    timezone = Column(String, nullable=False)  # Часовой пояс
    utc_offset_seconds = Column(Integer, nullable=False)  # Смещение часового пояса
    datetime_request = Column(DateTime, nullable=False)  # Дата и время запроса данных
    datetime_weather = Column(DateTime, nullable=False)  # Дата и время измерения погоды

    temperature_2m = Column(Float, nullable=False)  # Температура воздуха (°C)
    precipitation = Column(Float, nullable=False)  # Количество осадков (мм)
    type_precipitation = Column(String, nullable=False)  # Тип осадков (дождь, снег, дождь и снег, отсутствует)
    pressure_msl = Column(Float, nullable=False)  # Атмосферное давление на уровне моря (мм рт.ст.)
    wind_speed_10m = Column(Float, nullable=False)  # Скорость ветра на высоте 10 метров (м/с)
    wind_direction_10m = Column(String, nullable=False)  # Направление ветра на высоте 10 метров

    def to_dict(self) -> dict:
        """Метод преобразующий объекты модели в словарь.

        Returns:
            dict: словарь с данными.
        """

        data = {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "utc_offset_seconds": self.utc_offset_seconds,
            "datetime_request": self.datetime_request,
            "datetime_weather": self.datetime_weather,
            "temperature_2m": self.temperature_2m,
            "precipitation": self.precipitation,
            "type_precipitation": self.type_precipitation,
            "pressure_msl": self.pressure_msl,
            "wind_speed_10m": self.wind_speed_10m,
            "wind_direction_10m": self.wind_direction_10m,
        }

        return data


class DBManager:
    """Класс-менеджер для работы с базой данных."""

    def __init__(self, db_url="sqlite+aiosqlite:///weather_data.db") -> None:
        """Инициализация менеджера базы данных.

        Args:
            db_url (str): url базы данных (по умолчанию SQLite).
        """

        self.engine = create_async_engine(db_url, echo=False)
        self.AsyncSession = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def init_db(self) -> None:
        """Асинхронная инициализация базы данных, создание таблиц."""

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def add_weather_data(self, weather_data: dict) -> None:
        """Асинхронно добавляет новую запись о погоде в базу данных.

        Args:
            weather_data (dict): словарь с данными о погоде.
        """
        async with self.AsyncSession() as session:
            async with session.begin():
                new_data = WeatherDataModel(
                    latitude=weather_data["latitude"],
                    longitude=weather_data["longitude"],
                    timezone=weather_data["timezone"],
                    utc_offset_seconds=weather_data["utc_offset_seconds"],
                    datetime_request=weather_data["datetime_request"],
                    datetime_weather=weather_data["datetime_weather"],
                    temperature_2m=weather_data["temperature_2m"],
                    precipitation=weather_data["precipitation"],
                    type_precipitation=weather_data["type_precipitation"],
                    pressure_msl=weather_data["pressure_msl"],
                    wind_speed_10m=weather_data["wind_speed_10m"],
                    wind_direction_10m=weather_data["wind_direction_10m"],
                )
                session.add(new_data)
                await session.commit()

    async def get_all_weather_data(self) -> list[dict]:
        """Асинхронно возвращает все записи о погоде из базы данных.

        Returns:
            list: список всех записей о погоде
        """

        async with self.AsyncSession() as session:

            result = await session.execute(select(WeatherDataModel))
            weather_data_list = result.mappings().all()
            data = [item["WeatherDataModel"].to_dict() for item in weather_data_list]

            return data
