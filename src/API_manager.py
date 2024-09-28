from datetime import datetime

import httpx


class APIManager:
    """Класс для получения данных с API Open-Meteo."""

    URL = "https://api.open-meteo.com/v1/forecast"
    CURRENT_PARAMETERS = [
        "temperature_2m",
        "precipitation",
        "rain",
        "snowfall",
        "pressure_msl",
        "wind_speed_10m",
        "wind_direction_10m",
    ]

    def __init__(self, latitude: float, longitude: float) -> None:
        """Инициализирует объект для работы с API Open-Meteo, формирует координаты и параметры для запроса.

        Args:
            latitude (float): широта.
            longitude (float): долгота.
        """

        self.latitude = latitude
        self.longitude = longitude
        self.coordinates = {"latitude": self.latitude, "longitude": self.longitude}
        self.params = {"current": self.CURRENT_PARAMETERS}

    async def get_response_from_openmeteo(self) -> list[object]:
        """Асинхронно отправляет запрос к API Open-Meteo с заданными координатами и параметрами, возвращает ответ.

        Returns:
            list[object]: список с объектами ответа от API, содержащими данные о погоде.
        """

        params = {**self.coordinates, **self.params}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.URL, params=params)
                response.raise_for_status()
                return response.json()

            except httpx.RequestError as e:
                print(f"Ошибка запроса: {e}")
            except httpx.HTTPStatusError as e:
                print(f"Ошибка HTTP: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                print(f"Неизвестная ошибка: {e}")

    def convert_data(self, response: list[object]) -> dict:
        """Преобразует данные, полученные из объекта response, и формирует словарь с характеристиками текущей погоды.

        Args:
            response (list[object]): список объектов, содержащих данные о погоде.

        Returns:
            dict: словарь с характеристиками погоды.
        """

        data = {}

        data["latitude"] = self.latitude  # Широта
        data["longitude"] = self.longitude  # Долгота
        data["timezone"] = response["timezone"]  # Часовой пояс
        data["utc_offset_seconds"] = response["utc_offset_seconds"]  # Смещение часового пояса
        data["datetime_request"] = datetime.now()  # Время и дата запроса данных
        data["datetime_weather"] = datetime.fromisoformat(response["current"]["time"])  # Время и дата измерения погоды

        data["temperature_2m"] = response["current"]["temperature_2m"]  # Температура воздуха (градусы Цельсия)

        data["precipitation"] = response["current"]["precipitation"]  # Сумма осадков (мм)
        rain = response["current"]["rain"]  # Количество осадков (дождь)
        snowfall = response["current"]["snowfall"]  # Количество осадков (снег)
        data["type_precipitation"] = self.determine_type_precipitation(rain, snowfall)  # Тип осадков

        data["pressure_msl"] = self.convert_hpa_to_mmhg(
            response["current"]["pressure_msl"]
        )  # Атмосферное давление (мм рт.ст.)

        data["wind_speed_10m"] = self.convert_speed_kmh_to_ms(
            response["current"]["wind_speed_10m"]
        )  # Скорость ветра (м/с)
        data["wind_direction_10m"] = self.convert_degrees_to_direction(
            response["current"]["wind_direction_10m"]
        )  # Направление ветра

        return data

    async def get_weather_data(self) -> dict:
        """Асинхронно получает данные о погоде из API Open-Meteo и преобразует их в удобный формат.

        Returns:
            dict: словарь с текущими погодными данными, преобразованными в удобный формат.
        """

        response = await self.get_response_from_openmeteo()

        return self.convert_data(response)

    @staticmethod
    def determine_type_precipitation(precipitation_rain: float, precipitation_snow: float) -> str:
        """Определяет тип осадков.

        Args:
            precipitation_rain (float): количество осадков (дождь)
            precipitation_snow (float): количество осадков (снег)

        Returns:
            str: тип осадков (дождь, снег, дождь и снег, отсутствуют).
        """

        if precipitation_rain > 0 and precipitation_snow > 0:
            return "снег"
        elif precipitation_rain > 0 and precipitation_snow == 0:
            return "дождь"
        elif precipitation_rain > 0 and precipitation_snow > 0:
            return "дождь и снег"
        else:
            return "отсутствуют"

    @staticmethod
    def convert_speed_kmh_to_ms(speed: float) -> float:
        """Преобразовывает скорость км/ч в м/с.

        Args:
            speed (float): скорость в километрах в час.

        Returns:
            float: скорость в метрах в час.
        """

        return round(speed * 1000 / 3600, 2)

    @staticmethod
    def convert_degrees_to_direction(degrees: float) -> str:
        """Преобразовывает градусы в направление ("С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ").

        Args:
            degrees (float): направление ветра в градусах.

        Returns:
            str: направление ветра в сокращении.
        """

        directions = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
        index = round(degrees / 45) % 8

        return directions[index]

    @staticmethod
    def convert_hpa_to_mmhg(pressure_hpa: float) -> float:
        """Преобразовывает гектопаскали в миллиметры ртутного столба.

        Args:
            pressure_hpa (float): давление в гектопаскалях.

        Returns:
            float: давление в миллиметрах ртутного столба.
        """

        return round(pressure_hpa / 1.333, 2)
