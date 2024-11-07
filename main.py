from flask import *
from flask_socketio import SocketIO

from source.sql import *
from source.classes import *
from source.pages    import init as init_pages
from source.requests import init as init_requests
from source.socket   import init as init_socket

base = Base("base")
# base._drop_all_tables()
accounts = AccountsManager(base)
clients = ClientManager()
manager = Manager(base)

app = Flask(__name__, static_folder="static")
socketio = SocketIO(app, async_mode='threading')

if not accounts.check_login("admin"):
	admin = Account(base, "admin", 2902063403365090132)
	admin.name = "Админ"
	admin.update_on_base(base)

init_pages   (app, base, accounts, clients, manager)
init_requests(app, base, accounts, clients, manager)
init_socket  (app, base, accounts, clients, manager, socketio)

app.run(debug=True, host="0.0.0.0")