from flask import *
from sql import *
from classes import *


def init(DEBUG: bool, app: Flask, base: SQL_base, accounts: AccountsManager, clients: ClientManager, chats: ChatManager):
    
    def get_account():	
        ip = request.remote_addr
        return ip, clients[ip]


    @app.route("/login")
    def login():
        last_login = request.cookies.get("last_login")
        log = request.cookies.get("login_log")
        
        if last_login == None:
            last_login = ""
        
        if log != None:
            return render_template("login.html", show=True, log=log, last_login=last_login, accs=accounts.get_all())
        
        return render_template("login.html", show=False, log=log, last_login=last_login, accs=accounts.get_all())

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
        ip, account = get_account()
        
        if account == None:
            return redirect("/login",code=302)
        
        finded = chats.get_all_chats_for_user(account.index)
        user_chats = [Chat_Preview(base, account.index, i) for i in finded]
        
        return render_template("home.html", chats=user_chats, chat_opened=account.chat_opened, current_chat=account.get_opened_chat(base))

    @app.route("/profile")
    def profile():
        ip, account = get_account()

        if account == None:
            return redirect("/")

        return render_template("profile.html", user=account)

    @app.route("/admin")
    def admin():
        ip, account = get_account()

        if account == None:
            return redirect("/login", code=302)
        
        return render_template("admin.html")