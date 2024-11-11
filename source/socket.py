from source.classes import *


@socketio.on('login')
def io_login():
	debug_object.socket_receive("login")
	account = get_account()
	clients.add_sid(account.ID, request.sid)

@socketio.on('logout')
def io_logout():
	debug_object.socket_receive("logout")

@socketio.on('find_request')
def find_request(_request: str):
	debug_object.socket_receive("find_request", _request)

	if _request == "":
		return

	account = get_account()

	finded = accounts.find(account.ID, _request)
	response = ";".join(list(map(str, finded)))
	
	socketio.emit("find_response", response, room=request.sid)
	debug_object.socket_send("find_response", response)

@socketio.on('get_chat_name')
def get_chat_name(chat_ID: str):
	debug_object.socket_receive("get_chat_name", chat_ID)

	if chat_ID == "-1":
		return
	
	account = get_account()
	chat_ID = int(chat_ID)
	
	with TableHandler(base, Manager.ChatsHead) as handle:
		chat = Chat(manager, *( handle.get_row(chat_ID) ), account.ID)
		socketio.emit("set_chat_name", chat.user2.name, room=request.sid)
		debug_object.socket_send("set_chat_name", chat.user2.name)

@socketio.on('send_message')
def send_message(raw_message: str, client_message_ID: str):
	debug_object.socket_receive("send_message", raw_message, client_message_ID)

	account = get_account()
	client_message_ID = int(client_message_ID)

	with TableHandler(base, account.opened_chat.Head) as handle:
		new_ID = handle.add_row(account.ID, raw_message, "HHMMSSDDMMYYYY", 0)
		
		reciver = clients.get_sid(account.opened_chat.user2.ID)
		if reciver != None:
			response = Message(*handle.get_row(new_ID)).pack()
			socketio.emit("get_messages_response", response, room=reciver)
			debug_object.socket_send("sended_message_sync", response)
		
		response = f"{client_message_ID},{new_ID}"
		socketio.emit("sended_message_sync", response, room=request.sid)
		debug_object.socket_send("sended_message_sync", response)

@socketio.on('get_last_messages')
def get_last_messages():
	debug_object.socket_receive("get_last_messages")

	account = get_account()

	finded = account.opened_chat.get_last_messages()
	response = ";".join([i.pack() for i in finded])
	socketio.emit("get_messages_response", response, room=request.sid)
	debug_object.socket_send("get_messages_response", response)

@socketio.on('save_theme')
def save_theme(packed_theme: str):
	debug_object.socket_receive("save_theme")

	account = get_account()
	
	account.theme = packed_theme.ljust(96, "0") + account.theme[96:]
	account.update_on_base(base)