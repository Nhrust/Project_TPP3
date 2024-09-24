const socket = io();

function find_users() {
    var request = document.querySelector(".find").value;
    socket.emit('find_request', request);
}

socket.on('find_response', (arg) => {
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

            const link = document.createElement("a");
            link.classList.add("link");
            link.href = values[2];
            link.textContent = "+";
            div.appendChild(link);

            const FIND = document.querySelector(".FIND");
            FIND.after(div);
        });
    }
})