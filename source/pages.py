from flask import *

from source.sql import *
from source.classes import *


def init(app: Flask, base: Base, accounts: AccountsManager, clients: ClientManager, manager: Manager):
    
    def get_account() -> tuple[str, Account]:
        ip = request.remote_addr
        return ip, clients[ip]


    @app.route("/login")
    def login():
        last_login = request.cookies.get("last_login")
        log = request.cookies.get("login_log")
        
        if last_login == None:
            last_login = ""
        
        if log != None:
            return render_template("login.html", show_logs=True, log=log, last_login=last_login, accs=accounts._debug_get_all())
        else:
            return render_template("login.html", show_logs=False, log=log, last_login=last_login, accs=accounts._debug_get_all())

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
                return render_template("signin.html", show_logs=True, last_login=last_login, log=log)
        
        return render_template("signin.html")

    @app.route("/home", methods=["GET", "POST"])
    def home():
        ip, account = get_account()
        
        if account == None:
            return redirect("/login",code=302)
        
        client_chats = manager.get_all_chats_for_user(account.ID)
        
        return render_template("home.html", account=account, chats=client_chats)

    @app.route("/profile")
    def profile():
        ip, account = get_account()

        if account == None:
            return redirect("/")

        return render_template("profile.html", account=account)

    @app.route("/admin")
    def admin():
        ip, account = get_account()

        if account == None:
            return redirect("/login", code=302)
        
        return render_template("admin.html")