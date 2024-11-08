from flask import *
from flask_socketio import SocketIO
from random import randint
from cryptography.fernet import Fernet

from source.sql import *


class UI_texts:
	UserNotFind = "Пользователь не найден"
	WrongPass   = "Неверный пароль"

DEBUG = True

base = Base("base")
# base._drop_all_tables()

app = Flask(__name__, static_folder="static")
socketio = SocketIO(app, async_mode='threading')