from flask import *
from sql import *
from classes import *


def init(DEBUG: bool, app: Flask, base: SQL_base, accounts: AccountsManager, clients: ClientManager, chats: ChatManager):

    def get_account():	
        ip = request.remote_addr
        return ip, clients[ip]


    @app.route("/")
    def index():
        resp = make_response(redirect("/login",code=302))
        resp.set_cookie("last_login", '', expires=0)
        resp.set_cookie("last_signin", '', expires=0)
        resp.set_cookie("login_log", '', expires=0)
        resp.set_cookie("signin_log", '', expires=0)
        return resp

    @app.route("/auth", methods=['POST'])
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
    
    @app.route("/fast_auth", methods=["POST"])
    def fast_auth():
        login = request.form['login']
        user_id = base.table("users").get("login", login, "id")[0][0]
        account = Account.load(base, user_id)
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
            
            if DEBUG: print(f"> accounts.add({login}, {password1})")
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
            
            ip, account = get_account()
            
            if account == None:
                return redirect("/home")
            
            account.name, account.age, account.gender, account.description = new_name, new_age, new_gender, new_description
            account.update_on_base(base)
            base.commit()
        return redirect("/profile")

    @app.route("/view_profile/<index>")
    def view_profile(index: str):
        viewed_user = Account.unpack(base.table("users").get("id", index)[0])
        if DEBUG: print("view profile", index)
        if DEBUG: print("viewed_user index", viewed_user.index)
        return render_template("view.html", user=viewed_user)

    @app.route("/open_chat_with_user/<index>")
    def open_chat_with_user(index: str):
        ip, account = get_account()

        if account == None:
            return redirect("/login", code=302)
        
        print(f"chats.get({account.index}, {int(index)})")
        chat_id = chats.get(account.index, int(index))
        if DEBUG: print("open chat", chat_id)
        
        account.chat_opened = True
        account.opened_chat = chat_id
        
        return redirect("/home")