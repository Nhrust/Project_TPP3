from flask import *
from sql import *
from clients import *


base = SQL_base("base") # base это БД
accounts = AccountsManager(base)
clients = ClientManager()
app = Flask(__name__)

#accounts.reset()
if not accounts.check_login("admin"):
	base["users"].add("admin", 1549191368, params=("login", "password")) #hash(admin)
base.commit()




def LOG(*args):
	f = open("logs.txt", "a")
	print(*args, file=f)
	f.close()



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

@app.route("/home")
def home():
	ip = request.remote_addr
	user = clients[ip]
	
	if user == None:
		return redirect("/login",code=302)
	
	return str(user)

@app.route("/admin")
def admin():
	ip = request.remote_addr
	user = clients[ip]

	if user == None:
		return redirect("/login",code=302)
	
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
		user = accounts.get(login, password)
		
		if isinstance(user, User):
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
		
		LOG("> unexpected", user)
		resp = make_response(redirect("/",code=302))
		return resp
	
	return render_template(redirect("/login",code=302))

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



if __name__ == "__main__":
	app.run(debug=True)