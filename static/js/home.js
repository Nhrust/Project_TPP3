const socket = io();


socket.emit("login");


function CreateElement(type, Class=null) {
	var element = document.createElement(type);
	
	if (Class != null) {
		element.classList.add(Class);
	}
	
	return element;
}

var chat_opened = false;
var opened_chat = -1;
var chat_type = 0;
var last_message_ID = 0;
var self_id = 0;
function setup(_chat_opened, _opened_chat, _chat_type, _last_message_ID, _self_id) {
	chat_opened = Boolean(_chat_opened);
	opened_chat = Number(_opened_chat);
	chat_type = Number(_chat_type);
	last_message_ID = Number(_last_message_ID);
	self_id = Number(_self_id);
}

function setup_find() {
	document.querySelector(".find_form").onsubmit = function(event) {
		event.preventDefault();
		socket.emit('find_request', document.querySelector(".find_input").value);
	}
}

function send_setup() {
	document.querySelector(".send_form").onsubmit = function(event) {
		event.preventDefault();
		send_message();
	}
}




socket.on('find_response', (arg) => {
	var finded = document.querySelectorAll(".account");
	finded.forEach(element => {
		element.parentNode.removeChild(element);
	});

	if (arg != "") {
		arg.split(";").forEach(element => {
			const values = element.split(",");
			const img = CreateElement("img");
			img.src = values[0];
			const name = CreateElement("p", "name");
			name.textContent = values[1];
			const status = CreateElement("p", "status");
			status.textContent = "status";
			const symbol = CreateElement("p", "symbol");
			symbol.textContent = "?";

			const div = CreateElement("div", "account");
			div.appendChild(img);
			div.appendChild(name);
			div.appendChild(status);
			div.appendChild(symbol);

			const link = CreateElement("a");
			link.href = "/view_profile/" + values[2];
			link.title = "View profile";
			link.appendChild(div);
			document.querySelector(".FIND_FIELD").after(link);
		});
	}
})

socket.on("set_chat_name", (arg) => {
	var chat_name = document.querySelector(".chat_name");
	chat_name.textContent = arg;
})

socket.on("sended_message_sync", (response) => {
	response = response.split(",");
	local_ID = String(response[0]);
	server_ID = String(response[1]);
	document.querySelectorAll("._ID").forEach(element => {
		if (element.textContent == local_ID) {
			element.textContent = server_ID;
		}
		element.parentNode.querySelector(".info .symbol").textContent = "+";
	});
})

socket.on("get_messages_response", (response) => {
	while (response.length != 0) {
		var ID, sender, time, visible, data_length, data, index;

		function find_next() {
			for (var i = 0; i < response.length; i++) {
				if (response[i] == ",") {
					result = response.slice(0, i);
					response = response.slice(i + 1);
					return result;
				}
			}
		}

		ID          = Number(find_next(response));
		sender      = Number(find_next(response));
		time        = String(find_next(response));
		visible     = Number(find_next(response));
		data_length = Number(find_next(response));
		data        = String(response.slice(0, data_length));
		response = response.slice(data_length + 1);

		var existed = null;
		document.querySelectorAll("._ID").forEach(element => {
			if (Number(element.textContent) == ID) {
				message = element.parentNode.parentNode;
				message.parentNode.removeChild(message);
			}
		})

		appendMessage(ID, sender, data, time, visible);
	}
})




function update() {
	socket.emit("get_last_messages");
}




function send_message() {
	var send_input = document.querySelector(".send_input");
	var message = send_input.value;
	
	if (message != null) {
		if (message.length != 0) {
			last_message_ID += 1;
			socket.emit("send_message", message, last_message_ID);
			appendMessage(last_message_ID, self_id, message, null, "0", 1);
			send_input.value = "";
		}
	}
}




function recreate_chat(chat_id) {
	const right = document.querySelector(".right");

	document.querySelectorAll(".main").forEach(element => {
		element.parentNode.removeChild(element);
	})
	document.querySelectorAll(".send").forEach(element => {
		element.parentNode.removeChild(element);
	})
	
	const main = CreateElement("div", "main");
	right.appendChild(main);

	const send = CreateElement("div", "send");
		
		const form = CreateElement("form", "send_form");
		form.onsubmit = function(event) {
			event.preventDefault();
			send_message();
		}
			
			const input = CreateElement("input", "send_input");
			input.type = "text";
			form.appendChild(input);

			const submit = CreateElement("input", "send_submit");
			submit.type = "submit";
			submit.value = "Отправить";
			form.appendChild(submit);
		
		send.appendChild(form);
	
	right.appendChild(send);

	socket.emit("get_last_messages");
}




function appendMessage(an_ID, a_sender, a_data, a_time, a_visible) {
	var main = document.querySelector(".main");

	var position = (a_sender == self_id);
	const message = document.createElement("div");
	message.classList.add("message");
	if (position) {
		message.id = "my";
	}
	
		const box = document.createElement("div");
		box.classList.add("box");

			if (chat_type == 1) {
				const sender = document.createElement("p");
				sender.classList.add("sender");
				sender.textContent = a_sender;
				box.appendChild(sender);
			}

			const data = document.createElement("div");
			data.classList.add("data");
			data.textContent = a_data;
			box.appendChild(data);

			const info = document.createElement("div");
			info.classList.add("info");

				const time = document.createElement("p");
				time.classList.add("time");
				if (a_time == null) {
					time.textContent = "Сейчас";
				}
				else {
					time.textContent = String(a_time).slice(0, 2) + ":" + String(a_time).slice(2, 4) + ":" + String(a_time).slice(4, 6);
				}
				info.appendChild(time)

				const symbol = document.createElement("p");
				symbol.classList.add("symbol");
				symbol.textContent = "?";
				info.appendChild(symbol);
			
			box.appendChild(info);

			const _ID = document.createElement("meta_");
			_ID.classList.add("_ID");
			_ID.id = String(an_ID);
			_ID.textContent = String(an_ID);
			box.appendChild(_ID);

			const _visible = document.createElement("meta_");
			_visible.classList.add("_visible");
			_visible.textContent = a_visible;
			box.appendChild(_visible);
		
		message.appendChild(box);

	if (last_message_ID < an_ID) {
		last_message_ID = an_ID;
	}

	main.appendChild(message);
}