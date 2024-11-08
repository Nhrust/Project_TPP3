const socket = io();




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

            const link = document.createElement("a");
            link.href = "/view_profile/" + values[2];

                const div = document.createElement("div");
                div.classList.add("account");

                    const img = document.createElement("img");
                    img.src = "static/Images/" + values[0];
                    div.appendChild(img);

                    const name = document.createElement("p");
                    name.classList.add("name");
                    name.textContent = values[1];
                    div.appendChild(name);

                    const status = document.createElement("p");
                    status.classList.add("status");
                    status.textContent = "status";
                    div.appendChild(status);

                    const symbol = document.createElement("p");
                    symbol.classList.add("symbol");
                    symbol.textContent = ">";
                    div.appendChild(symbol);
                
                link.appendChild(div);

            var FIND_FIELD = document.querySelector(".FIND_FIELD");
            FIND_FIELD.after(link);
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
            console.log("sended_message_sync - Success");
        }
    });
})




function send_message() {
    var send_input = document.querySelector(".send_input");
    var message = send_input.value;
    if (message != null) {
        if (message.length != 0) {
            last_message_ID += 1;
            socket.emit("send_message", message, last_message_ID);
            appendMessage(last_message_ID, self_id, message, "203100", "0", 1);
            send_input.value = "";
        }
    }
}




function open_chat(chat_id) {
    const right = document.querySelector(".right");
    
    opened_chat = Number(chat_id);

    if (chat_opened && chat_id == opened_chat) {
        return;
    }

    document.querySelectorAll(".main").forEach(element => {
        element.parentNode.removeChild(element);
    })
    document.querySelectorAll(".send").forEach(element => {
        element.parentNode.removeChild(element);
    })
    
    const main = document.createElement("div");
    main.classList.add("main");
    right.appendChild(main);

    const send = document.createElement("div");
    send.classList.add("send");
        
        const form = document.createElement("form");
        form.classList.add("send_form");
        form.onsubmit = function(event) {
            event.preventDefault();
            send_message();
        }
            
            const input = document.createElement("input");
            input.type = "text";
            input.classList.add("send_input");
            form.appendChild(input);

            const submit = document.createElement("input");
            submit.type = "submit";
            submit.classList.add("send_submit");
            submit.value = "Отправить";
            form.appendChild(submit);
        
        send.appendChild(form);
    
    right.appendChild(send);

    socket.emit('get_chat_name', chat_id);
}




function appendMessage(an_ID, a_sender, a_data, a_time, a_visible, position) {
    var main = document.querySelector(".main");

    const message = document.createElement("div");
    message.classList.add("message");
    if (position == 1) {
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
                time.textContent = String(a_time).slice(0, 2) + ":" + String(a_time).slice(2, 4) + ":" + String(a_time).slice(4, 6);
                info.appendChild(time)

                const symbol = document.createElement("p");
                symbol.classList.add("symbol");
                symbol.textContent = "?";
                info.appendChild(symbol);
            
            box.appendChild(info);

            const _ID = document.createElement("meta_");
            _ID.classList.add("_ID");
            _ID.textContent = String(an_ID);
            box.appendChild(_ID);

            const _visible = document.createElement("meta_");
            _visible.classList.add("_visible");
            _visible.textContent = a_visible;
            box.appendChild(_visible);
        
        message.appendChild(box);

    main.appendChild(message);
}