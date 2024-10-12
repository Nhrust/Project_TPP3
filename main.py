from flask import *
from sql import *
from classes import *
from flask_socketio import SocketIO

from aPages    import init as init_pages
from aRequests import init as init_requests
from aSocket   import init as init_socket


DEBUG = True
base = SQL_base("base")
# base.RESET() # !!! полностью чистит БД
accounts = AccountsManager(base)
clients = ClientManager()
chats = ChatManager(base)

app = Flask(__name__, static_folder="static")
socketio = SocketIO(app, async_mode='threading')
base.commit()


if not accounts.check_login("admin"):
	admin = Account(None, "admin", hash("admin"))
	admin.create_on_base(base)
	admin.name = "Админ"
	admin.update_on_base(base)
base.commit()


init_pages   (DEBUG, app, base, accounts, clients, chats)
init_requests(DEBUG, app, base, accounts, clients, chats)
init_socket  (DEBUG, app, base, accounts, clients, chats, socketio)


if __name__ == "__main__":
	app.run(debug=DEBUG)
	# app.run(debug=True, host="0.0.0.0")