"""Handlers Package - Modular action handlers."""

from controller.handlers.base_handler import BaseHandler
from controller.handlers.time_handler import TimeHandler
from controller.handlers.weather_handler import WeatherHandler
from controller.handlers.system_handler import SystemHandler
from controller.handlers.search_handler import SearchHandler
from controller.handlers.app_handler import AppHandler
from controller.handlers.greeting_handler import GreetingHandler
from controller.handlers.file_handler import FileHandler
from controller.handlers.habit_handler import HabitHandler

__all__ = [
    'BaseHandler',
    'TimeHandler',
    'WeatherHandler',
    'SystemHandler',
    'SearchHandler',
    'AppHandler',
    'GreetingHandler',
    'FileHandler',
    'HabitHandler'
]
