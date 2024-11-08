from source.classes import *


@app.route("/")
def index():
	resp = make_response(redirect("/login", code=302))
	resp.set_cookie("last_login",  '', expires=0)
	resp.set_cookie("last_signin", '', expires=0)
	resp.set_cookie("login_log",   '', expires=0)
	resp.set_cookie("signin_log",  '', expires=0)
	return resp

@app.route("/auth", methods=['POST'])
def auth():
	if request.method == "POST":
		login = request.form['login']
		password = request.form['password']
		account = accounts.try_to_login(login, password)
		
		if isinstance(account, Account):
			clients.add(request.remote_addr, account)
			resp = make_response(redirect("/home",code=302))
			resp.set_cookie("last_login", '', expires=0)
			resp.set_cookie("login_log", '', expires=0)
			return resp
		
		elif account == UI_texts.UserNotFind:
			resp = make_response(redirect("/login",code=302))
			resp.set_cookie("last_login", "")
			resp.set_cookie("login_log", account)
			return resp
		
		elif account == UI_texts.WrongPass:
			resp = make_response(redirect("/login",code=302))
			resp.set_cookie("last_login", login)
			resp.set_cookie("login_log", account)
			return resp
		
		debug_object.error("Unexpected error in /auth request")
		return redirect("/",code=302)
	
	return redirect("/login",code=302)

@app.route("/fast_auth", methods=["POST"])
def fast_auth():
	login = request.form['login']
	with TableHandler(base, AccountsManager.Head) as handle:
		accaunt_ID = handle.get_by("login", login)[0][0]
		account = Account.unpack(base, handle.get_row(accaunt_ID))
		clients.add(request.remote_addr, account)
		return redirect("/home")

@app.route("/new_auth", methods=['POST'])
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
		new_age = request.form["age"]
		new_gender = request.form["gender"]
		new_about = request.form["about"]
		
		account = get_account()
		
		if account == None:
			return redirect("/home")
		
		account.name, account.age, account.gender, account.about = new_name, new_age, new_gender, new_about
		account.update_on_base(base)
	return redirect("/profile")

@app.route("/view_profile/<ID>")
def view_profile(ID: str):
	with TableHandler(base, AccountsManager.Head) as handle:
		account = Account.unpack(base, handle.get_row(int(ID)))
		return render_template("view.html", account=account)

@app.route("/open_chat_with_user/<find_account_ID>")
def open_chat_with_user(find_account_ID: str):
	account = get_account()

	if account == None:
		return redirect("/login", code=302)
	
	find_account_ID = int(find_account_ID)

	with TableHandler(base, Manager.ChatsHead) as handle:
		account.chat_opened = True
		account.opened_chat = manager.get_chat(account.ID, find_account_ID)
	
	return redirect("/home")