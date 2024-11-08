from source.classes import *


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
def send_message(raw_message: str, client_mesaage_ID: str):
	debug_object.socket_receive("send_message", raw_message, client_mesaage_ID)

	account = get_account()
	client_mesaage_ID = int(client_mesaage_ID)

	with TableHandler(base, account.opened_chat.Head) as handle:
		new_ID = handle.add_row(account.ID, raw_message, "HHMMSSDDMMYYYY", 0)
		response = f"{client_mesaage_ID},{new_ID}"
		socketio.emit("sended_message_sync", response, room=request.sid)
		debug_object.socket_send("sended_message_sync", response)

@socketio.on('get_last_messages')
def get_last_messages():
	debug_object.socket_receive("get_last_messages")

	account = get_account()
	client_mesaage_ID = int(client_mesaage_ID)

	finded = account.opened_chat.get_last_messages()
	response = ";".join([i.pack() for i in finded])
	debug_object.socket_send("get_messages_response", response, room=request.sid)