from flask import *
from sql import *
from classes import *
from flask_socketio import SocketIO, emit


DEBUG = True
base = SQL_base("base")
base.RESET() # !!! полностью чистит БД
accounts = AccountsManager(base)
clients = ClientManager()
chats = ChatManager(base)

app = Flask(__name__, static_folder="static")
socketio = SocketIO(app, async_mode='threading')
base.commit()


if not accounts.check_login("admin"):
	admin = Account(None, "admin", 1549191368)
	admin.create_on_base(base)
	admin.name = "Админ"
	admin.update_on_base(base)
base.commit()




# # # # # # # # # # PAGES # # # # # # # # # #

@app.route("/login")
def login():
	last_login = request.cookies.get("last_login")
	log = request.cookies.get("login_log")
	
	if last_login == None:
		last_login = ""
	
	if log != None:
		return render_template("login.html", show=True, log=log, last_login=last_login)
	
	return render_template("login.html", show=False, log=log, last_login=last_login)

@app.route("/signin")
def signin():
	last_login = request.cookies.get("last_signin")
	log = request.cookies.get("signin_log")

	if last_login == None:
		last_login = ""

	if log != None:
		try:
			log = eval(log)
		except:
			log = (log, )
		
		if len(log) != 0:
			return render_template("signin.html", last_login=last_login, show=True, log=log)
	
	return render_template("signin.html")

@app.route("/home", methods=["GET", "POST"])
def home():
	ip = request.remote_addr
	account = clients[ip]
	
	if account == None:
		return redirect("/login",code=302)
	
	finded = chats.get_all_chats_for_user(account.index)
	_chats = [Chat_Preview(base, account.index, i) for i in finded]
	
	return render_template("home.html", chats=_chats, chat_opened=account.chat_opened, chat_id=account.opened_chat)

@app.route("/profile")
def profile():
	ip = request.remote_addr
	account = clients[ip]

	if account == None:
		return redirect("/")

	return render_template("profile.html", user=account)

@app.route("/admin")
def admin():
	ip = request.remote_addr
	account = clients[ip]

	if account == None:
		return redirect("/login", code=302)
	
	return render_template("admin.html")




# # # # # # # # # # REQUESTS # # # # # # # # # #

@app.route("/")
def index():
	resp = make_response(redirect("/login",code=302))
	resp.set_cookie("last_login", '', expires=0)
	resp.set_cookie("last_signin", '', expires=0)
	resp.set_cookie("login_log", '', expires=0)
	resp.set_cookie("signin_log", '', expires=0)
	return resp

@app.route("/auth", methods=['GET', 'POST'])
def auth():
	if request.method == "POST":
		login = request.form['login']
		password = request.form['password']
		print("try to auth", login, password)
		account = accounts.get(login, password)
		
		if isinstance(account, Account):
			clients.add(request.remote_addr, account)
			resp = make_response(redirect("/home",code=302))
			resp.set_cookie("last_login", '', expires=0)
			resp.set_cookie("login_log", '', expires=0)
			return resp
		
		elif account == UserNotFind:
			resp = make_response(redirect("/login",code=302))
			resp.set_cookie("last_login", "")
			resp.set_cookie("login_log", account)
			return resp
		
		elif account == WrongPass:
			resp = make_response(redirect("/login",code=302))
			resp.set_cookie("last_login", login)
			resp.set_cookie("login_log", account)
			return resp
		
		print("unexpected error")
		resp = make_response(redirect("/",code=302))
		return resp
	
	return redirect("/login",code=302)

@app.route("/new_auth", methods=['GET', 'POST'])
def new_auth():
	if request.method == "POST":
		login = request.form['login']
		password1 = request.form['password1']
		password2 = request.form['password2']
		
		log = []
		
		if len(login) < 4:
			log.append("Login minimum length is 4")
		elif accounts.check_login(login):
			log.append("Login already exist")
		
		if password1 != password2:
			log.append("Passwords not math")
		elif len(password1) < 4:
			log.append("Password minimum length is 4")
		
		if len(log) != 0:
			resp = make_response(redirect("/signin",code=302))
			resp.set_cookie("last_signin", login)
			resp.set_cookie("signin_log", str(log))
			return resp
		
		account = accounts.add(login, password1)
		clients.add(request.remote_addr, account)

		resp = make_response(redirect("/home",code=302))
		resp.set_cookie("last_signin", '', expires=0)
		resp.set_cookie("signin_log", '', expires=0)
		return resp
		
	return render_template(redirect("/login",code=302))

@app.route("/logout")
def logout():
	ip = request.remote_addr
	clients.remove(ip)
	return redirect("/")

@app.route("/edit_profile", methods=["POST"])
def edit_profile():
	if request.method == "POST":
		new_name = request.form["name"]
		new_age = int(request.form["age"])
		new_gender = int(request.form["gender"])
		new_description = request.form["description"]
		
		ip = request.remote_addr
		account = clients[ip]
		
		if account == None:
			return redirect("/home")
		
		account.name, account.age, account.gender, account.description = new_name, new_age, new_gender, new_description
		account.update_on_base(base)
		base.commit()
	return redirect("/profile")

@app.route("/view_profile/<index>")
def view_profile(index):
	viewed_user = Account.unpack(base["users"].get("id", index)[0])
	if DEBUG: print("view profile", index)
	if DEBUG: print("viewed_user index", viewed_user.index)
	return render_template("view.html", user=viewed_user)

@app.route("/open_chat_with_user/<index>")
def open_chat_with_user(index):
	ip = request.remote_addr
	account = clients[ip]

	if account == None:
		return redirect("/login", code=302)
	
	print(f"chats.get({account.index}, {int(index)})")
	chat_id = chats.get(account.index, int(index))
	if DEBUG: print("open chat", chat_id)
	
	account.chat_opened = True
	account.opened_chat = chat_id
	
	return redirect("/home")




@socketio.on('find_request')
def find_request(_request):
	if DEBUG: print("> find_requesr", _request)
	print("find_request", _request)
	ip = request.remote_addr
	account = clients[ip]
	finded = accounts.find(account.index, _request)
	response = ";".join(list(map(str, finded)))
	if DEBUG: print("< find_response", response)

	socketio.emit("find_response", response, room=request.sid)

@socketio.on('get_chat_name')
def get_chat_name(chat_id):
	if chat_id == "EMPTY":
		print("try to open chat when chat_id not set")
		return
	chat_id = int(chat_id)
	ip = request.remote_addr
	account = clients[ip]
	second_id = chats.get_second(chat_id, account.index)
	chat_name = base["users"].get("id", second_id, "name")[0][0]

	socketio.emit("set_chat_name", decode(chat_name), room=request.sid)




if __name__ == "__main__":
	app.run(debug=DEBUG)
	# app.run(debug=True, host="0.0.0.0")