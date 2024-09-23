import flask
from sql import *
from clients import *


base = SQL_base("SUSSYBAKA\\SQLEXPRESS", "base") # base это БД
accounts = AccountsManager(base)
clients = ClientManager()
app = flask.Flask(__name__)

# accounts.reset()
if not accounts.check_login("admin"):
	base["users"].add("admin", 1549191368, params=("login", "password"))
base.commit()




def LOG(*args):
	f = open("logs.txt", "a")
	print(*args, file=f)
	f.close()




# # # # # # # # # # PAGES # # # # # # # # # #

@app.route("/login")
def login():
	last_login = flask.request.cookies.get("last_login")
	log = flask.request.cookies.get("log")
	
	if last_login == None:
		last_login = ""
	
	if log != None:
		return flask.render_template("login.html", show=True, log=log, last_login=last_login)
	
	return flask.render_template("login.html", show=False, log=log, last_login=last_login)

@app.route("/signin")
def signin():
	last_login = flask.request.cookies.get("last_login")
	log = flask.request.cookies.get("log")

	if last_login == None:
		last_login = ""

	if log != None:
		log = eval(log)
		if len(log) != 0:
			return flask.render_template("signin.html", last_login=last_login, show=True, log=log)
	
	return flask.render_template("signin.html")

@app.route("/home")
def home():
	ip = flask.request.remote_addr
	user = clients[ip]
	
	if user == None:
		return flask.redirect("/login",code=302)
	
	return str(user)

@app.route("/admin")
def admin():
	ip = flask.request.remote_addr
	user = clients[ip]

	if user == None:
		return flask.redirect("/login",code=302)
	
	return flask.render_template("admin.html")




# # # # # # # # # # REQUESTS # # # # # # # # # #

@app.route("/")
def index():
	resp = flask.make_response(flask.redirect("/login",code=302))
	resp.set_cookie("last_login", '', expires=0)
	resp.set_cookie("log", '', expires=0)
	return resp

@app.route("/auth", methods=['GET', 'POST'])
def auth():
	if flask.request.method == "POST":
		login = flask.request.form['login']
		password = flask.request.form['password']
		user = accounts.get(login, password)
		
		if isinstance(user, User):
			clients.add(flask.request.remote_addr, user)
			resp = flask.make_response(flask.redirect("/home",code=302))
			resp.set_cookie("last_login", '', expires=0)
			resp.set_cookie("log", '', expires=0)
			return resp
		
		elif user == UserNotFind:
			resp = flask.make_response(flask.redirect("/login",code=302))
			resp.set_cookie("last_login", "")
			resp.set_cookie("log", user)
			return resp
		
		elif user == WrongPass:
			resp = flask.make_response(flask.redirect("/login",code=302))
			resp.set_cookie("last_login", login)
			resp.set_cookie("log", user)
			return resp
		
		LOG("> unexpected", user)
		resp = flask.make_response(flask.redirect("/",code=302))
		return resp
	
	return flask.render_template(flask.redirect("/login",code=302))

@app.route("/new_auth", methods=['GET', 'POST'])
def new_auth():
	if flask.request.method == "POST":
		login = flask.request.form['login']
		password1 = flask.request.form['password1']
		password2 = flask.request.form['password2']
		
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
			resp = flask.make_response(flask.redirect("/signin",code=302))
			resp.set_cookie("last_login", login)
			resp.set_cookie("log", str(log))
			return resp
		
		user = accounts.add(login, password1)
		clients.add(flask.request.remote_addr, user)

		resp = flask.make_response(flask.redirect("/home",code=302))
		resp.set_cookie("last_login", '', expires=0)
		resp.set_cookie("log", '', expires=0)
		return resp
		
	return flask.render_template(flask.redirect("/login",code=302))


if __name__ == "__main__":
	app.run()