from flask import *
from sql import *
from classes import *
from flask_socketio import SocketIO, emit


def init(DEBUG: bool, app: Flask, base: SQL_base, accounts: AccountsManager, clients: ClientManager, chats: ChatManager, socketio: SocketIO):

    def get_account():	
        ip = request.remote_addr
        return ip, clients[ip]


    @socketio.on('find_request')
    def find_request(_request: str):
        if DEBUG: print("> find_request", _request)

        if _request == "":
            if DEBUG: print("> find_request\n? request is empty")
            return

        ip, account = get_account()

        finded = accounts.find(account.index, _request)
        response = ";".join(list(map(str, finded)))
        
        socketio.emit("find_response", response, room=request.sid)
        if DEBUG: print("< find_response", response)

    @socketio.on('get_chat_name')
    def get_chat_name(chat_id: str):
        if DEBUG: print("> get_chat_name", chat_id)

        if chat_id == "EMPTY":
            print("!!! try to open chat when chat_id not set")
            return
        
        chat_id = int(chat_id)
        ip, account = get_account()
        second_id = chats.get_second(chat_id, account.index)
        chat_name = base.table("users").get("id", second_id, "name")[0][0]

        socketio.emit("set_chat_name", decode(chat_name), room=request.sid)
        if DEBUG: print("< set_chat_name", decode(chat_name), "for client", request.sid)

    @socketio.on('send_message')
    def send_message(raw_message: str):
        if DEBUG: print("> send_message", raw_message)

        ip, account = get_account()

        if account == None:
            print("!!! sender not in accaunts")
            return
        
        if account.opened_chat == -1:
            print("!!! CHAT NOT OPENED")
            return
        
        if DEBUG: print("chats send_message()")
        chats[account.opened_chat].send_message(account, raw_message)

    @socketio.on('get_message')
    def get_message(index: int):
        if DEBUG: print("> get_message", index)

        ip, account = get_account()

        message = chats[account.opened_chat].get_message(int(index))
        if message == None:
            print("!!! get_message_response fail")
            return

        # response = message.pack()
        # if DEBUG: print("< get_message_response", response)

        # socketio.emit("get_message_response", response, room=request.sid)