import logging
from weather_providers.base_provider import BaseWeatherProvider


class AccuWeather(BaseWeatherProvider):
    def __init__(self, accuweather_apikey, location_lat, location_long, location_key, units):
        self.accuweather_apikey = accuweather_apikey
        self.location_lat = location_lat
        self.location_long = location_long
        self.location_key = location_key
        self.units = units

    # Map Accuweather icons to local icons
    # Reference: https://developer.accuweather.com/weather-icons
    def get_icon_from_accuweather_weathercode(self, weathercode, is_daytime):

        icon_dict = {
                        1: "clear_sky_day" if is_daytime else "clearnight",  # Day - Sunny
                        2: "clear_sky_day" if is_daytime else "clearnight",  # Day - Mostly Sunny
                        3: "few_clouds" if is_daytime else "partlycloudynight",  # Day - Partly Sunny
                        4: "scattered_clouds" if is_daytime else "partlycloudynight",  # Day - Intermittent Clouds
                        5: "haze",  # Day - Hazy Sunshine
                        6: "mostly_cloudy" if is_daytime else "mostly_cloudy_night",  # Day - Mostly Cloudy
                        7: "climacell_cloudy" if is_daytime else 'mostly_cloudy_night',  # DayNight - Cloudy
                        8: "overcast",  # DayNight - Dreary (Overcast)
                        11: "climacell_fog",  # DayNight - Fog
                        12: 'climacell_rain_light' if is_daytime else 'rain_night_light',  # DayNight - Showers
                        13: 'day_partly_cloudy_rain' if is_daytime else 'night_partly_cloudy_rain',  # Day - Mostly Cloudy w/ Showers
                        14: 'day_partly_cloudy_rain' if is_daytime else 'night_partly_cloudy_rain',  # Day - Partly Sunny w/ Showers
                        15: "thundershower_rain",  # DayNight - T-Storms
                        16: "scattered_thundershowers",  # Day - Mostly Cloudy w/ T-Storms
                        17: "scattered_thundershowers",  # Day - Partly Sunny w/ T-Storms
                        18: "climacell_rain" if is_daytime else "rain_night",  # DayNight - Rain
                        19: "climacell_flurries",  # DayNight - Flurries
                        20: "climacell_flurries",  # Day - Mostly Cloudy w/ Flurries
                        21: "climacell_flurries",  # Day - Partly Sunny w/ Flurries
                        22: "snow",  # DayNight - Snow
                        23: "snow",  # Day - Mostly Cloudy w/ Snow
                        24: "climacell_freezing_rain",  # DayNight - Ice
                        25: "sleet",  # DayNight - Sleet
                        26: "climacell_freezing_rain",  # DayNight - Freezing Rain
                        29: "sleet",  # DayNight - Rain and Snow
                        30: "very_hot",  # DayNight - Hot
                        31: "cold",  # DayNight - Cold
                        32: "wind",  # DayNight - Windy
                        33: "clear_sky_day" if is_daytime else "clearnight",  # Night - Clear
                        34: "clear_sky_day" if is_daytime else "clearnight",  # Night - Mostly Clear
                        35: "few_clouds" if is_daytime else "partlycloudynight",  # Night - Partly Cloudy
                        36: "scattered_clouds" if is_daytime else "partlycloudynight",  # Night - Intermittent Clouds
                        37: "haze",  # Night - Hazy Moonlight
                        38: "mostly_cloudy" if is_daytime else "mostly_cloudy_night",  # Night - Mostly Cloudy
                        39: 'day_partly_cloudy_rain' if is_daytime else 'night_partly_cloudy_rain',  # Night - Partly Cloudy w/ Showers
                        40: 'day_partly_cloudy_rain' if is_daytime else 'night_partly_cloudy_rain',  # Night - Mostly Cloudy w/ Showers
                        41: "thundershower_rain",  # Night - Partly Cloudy w/ T-Storms
                        42: "thundershower_rain",  # Night - Mostly Cloudy w/ T-Storms
                        43: "climacell_flurries",  # Night - Mostly Cloudy w/ Flurries
                        44: "snow"  # Night - Mostly Cloudy w/ Snow
                    }

        icon = icon_dict[weathercode]
        logging.debug(
            "get_icon_by_weathercode({}, {}) - {}"
            .format(weathercode, is_daytime, icon))

        return icon

    # Get weather from Accuweather APIs

    # https://developer.accuweather.com/accuweather-current-conditions-api/apis/get/currentconditions/v1/%7BlocationKey%7D
    def get_weather_current(self):

        url = ("http://dataservice.accuweather.com/currentconditions/v1/{}?apikey={}&details=true&metric={}"
                .format(self.location_key, self.accuweather_apikey, "true" if self.units == "metric" else "false"))

        response_data_current = self.get_response_json_current(url)
        weather_data_current = response_data_current
        logging.debug("get_weather_current() - {}".format(weather_data_current))

        daytime_str = str(weather_data_current[0]["IsDayTime"])
		if daytime_str == "True":
            daytime = True
        else:
            daytime = False

        logging.info(daytime_str)
        logging.info(daytime)

        accuweather_icon_current = weather_data_current[0]["WeatherIcon"]

        weather_current = {}

        weather_current["current_temperature"] = weather_data_current[0]["Temperature"]["Imperial"]["Value"]
        weather_current["current_icon"] = self.get_icon_from_accuweather_weathercode(accuweather_icon_current, daytime)
        weather_current["current_description"] = weather_data_current[0]["WeatherText"]
        logging.debug(weather_current)

        return weather_current

    # https://developer.accuweather.com/accuweather-forecast-api/apis/get/forecasts/v1/daily/1day/%7BlocationKey%7D
    def get_weather_forecast(self):

        url = ("http://dataservice.accuweather.com/forecasts/v1/daily/1day/{}?apikey={}&details=true&metric={}"
                .format(self.location_key, self.accuweather_apikey, "true" if self.units == "metric" else "false"))

        response_data_forecast = self.get_response_json_forecast(url)
        weather_data_forecast = response_data_forecast
        logging.debug("get_weather_forecast() - {}".format(weather_data_forecast))

        daytime = self.is_daytime(self.location_lat, self.location_long)
        accuweather_icon_forecast = weather_data_forecast["DailyForecasts"][0]["Day"]["Icon"] if daytime else weather_data_forecast["DailyForecasts"][0]["Night"]["Icon"]

        weather_forecast = {}
        weather_forecast["forecast_temperatureMin"] = weather_data_forecast["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
        weather_forecast["forecast_temperatureMax"] = weather_data_forecast["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
        weather_forecast["forecast_icon"] = self.get_icon_from_accuweather_weathercode(accuweather_icon_forecast, daytime)
        weather_forecast["forecast_description"] = weather_data_forecast["DailyForecasts"][0]["Day"]["ShortPhrase"] if daytime else weather_data_forecast["DailyForecasts"][0]["Night"]["ShortPhrase"]
		weather_forecast["is_it_daytime"] = daytime
        logging.debug(weather_forecast)

        return weather_forecast
