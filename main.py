from flask import *
from sql import *
from classes import *
from flask_socketio import SocketIO, emit


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
	admin = Account(None, "admin", 1549191368)
	admin.create_on_base(base)
	admin.name = "Админ"
	admin.update_on_base(base)
base.commit()




# # # # # # # # # # PAGES # # # # # # # # # #

@app.route("/login")
def login():
	last_login = request.cookies.get("last_login")
	log = request.cookies.get("log")
	
	if last_login == None:
		last_login = ""
	
	if log != None:
		return render_template("login.html", show=True, log=log, last_login=last_login)
	
	return render_template("login.html", show=False, log=log, last_login=last_login)

@app.route("/signin")
def signin():
	last_login = request.cookies.get("last_login")
	log = request.cookies.get("log")

	if last_login == None:
		last_login = ""

	if log != None:
		log = eval(log)
		if len(log) != 0:
			return render_template("signin.html", last_login=last_login, show=True, log=log)
	
	return render_template("signin.html")

@app.route("/home", methods=["GET", "POST"])
def home():
	ip = request.remote_addr
	user = clients[ip]
	
	if user == None:
		return redirect("/login",code=302)
	
	if "open_chat" in request.args:
		return render_template("home.html", chat_opened=True, chat=request.args["open_chat"])
	
	return render_template("home.html", chat_opened=False)

@app.route("/profile")
def profile():
	ip = request.remote_addr
	user = clients[ip]

	if user == None:
		return redirect("/")

	return render_template("profile.html", user=user)

@app.route("/admin")
def admin():
	ip = request.remote_addr
	user = clients[ip]

	if user == None:
		return redirect("/login", code=302)
	
	return render_template("admin.html")



# # # # # # # # # # REQUESTS # # # # # # # # # #

@app.route("/")
def index():
	resp = make_response(redirect("/login",code=302))
	resp.set_cookie("last_login", '', expires=0)
	resp.set_cookie("log", '', expires=0)
	return resp

@app.route("/auth", methods=['GET', 'POST'])
def auth():
	if request.method == "POST":
		login = request.form['login']
		password = request.form['password']
		print("try to auth", login, password)
		user = accounts.get(login, password)
		
		if isinstance(user, Account):
			clients.add(request.remote_addr, user)
			resp = make_response(redirect("/home",code=302))
			resp.set_cookie("last_login", '', expires=0)
			resp.set_cookie("log", '', expires=0)
			return resp
		
		elif user == UserNotFind:
			resp = make_response(redirect("/login",code=302))
			resp.set_cookie("last_login", "")
			resp.set_cookie("log", user)
			return resp
		
		elif user == WrongPass:
			resp = make_response(redirect("/login",code=302))
			resp.set_cookie("last_login", login)
			resp.set_cookie("log", user)
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
			resp.set_cookie("last_login", login)
			resp.set_cookie("log", str(log))
			return resp
		
		user = accounts.add(login, password1)
		clients.add(request.remote_addr, user)

		resp = make_response(redirect("/home",code=302))
		resp.set_cookie("last_login", '', expires=0)
		resp.set_cookie("log", '', expires=0)
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
		user = clients[ip]
		
		if user == None:
			return redirect("/home")
		
		user.name, user.age, user.gender, user.description = new_name, new_age, new_gender, new_description
		user.update_on_base(base)
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
	user = clients[ip]

	if user == None:
		return redirect("/login", code=302)
	
	print(f"chats.get({user.index}, {int(index)})")
	chat_id = chats.get(user.index, int(index))
	if DEBUG: print("open chat", chat_id)

	return redirect(f"/home?open_chat={chat_id}")




@socketio.on('find_request')
def find_request(_request):
	if DEBUG: print("> find_requesr", _request)
	print("find_request", _request)
	ip = request.remote_addr
	account = clients[ip]
	finded = accounts.find(account.index, _request)
	response = ";".join(list(map(str, finded)))
	if DEBUG: print("< find_response", response)
	socketio.emit("find_response", response)


if __name__ == "__main__":
	app.run(debug=DEBUG)
	# app.run(debug=True, host="0.0.0.0")