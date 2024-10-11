const socket = io();

var chat_opened = false;
var opened_chat = -1;

socket.on('find_response', (arg) => {
    const finded = document.querySelectorAll(".account");
    finded.forEach(element => {
        element.parentNode.removeChild(element);
    });

    if (arg != "") {
        arg.split(";").forEach(element => {
            const values = element.split(",");

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

            const link = document.createElement("a");
            link.classList.add("link");
            link.href = "/view_profile/" + values[2];
            link.textContent = ">";
            div.appendChild(link);

            const FIND_FIELD = document.querySelector(".FIND_FIELD");
            FIND_FIELD.after(div);

            const find = document.querySelector(".find");
            
        });
    }
})

function send_message() {
    const message = document.querySelector(".send_input").value;
    console.log(message);
    if (message != null) {
        if (message.length != 0) {
            socket.emit("send_message", message);
            console.log("sended");
        }
    }
}

function open_chat(chat_id) {
    chat_opened = true;
    opened_chat = Number(chat_id);

    const right = document.querySelector(".right");

    document.querySelectorAll(".main")
        .forEach(element => {
            element.parentNode.removeChild(element);
        })
    document.querySelectorAll(".send")
        .forEach(element => {
            element.parentNode.removeChild(element);
        })
    
    const main = document.createElement("div");
    main.classList.add("main");
    right.appendChild(main);

    const send = document.createElement("div");
    send.classList.add("send");
        
        const form = document.createElement("form");
        form.classList.add("send_form");
            
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
    
    right.appendChild(send)

    socket.emit('get_chat_name', chat_id);
}

socket.on("set_chat_name", (arg) => {
    const chat_name = document.querySelector(".chat_name");
    chat_name.textContent = arg;
    console.log("set_chat_name");
})