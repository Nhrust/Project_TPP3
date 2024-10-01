document.querySelector(".find_form")
    .onsubmit = function(event) {
        console.log("find_request");
        event.preventDefault();
        var request = document.querySelector(".find_input").value;
        socket.emit('find_request', request);
    }
console.log("Success find form");

document.querySelector(".send_form")
    .onsubmit = function(event) {
        console.log("event prevent default");
        event.preventDefault();
        send_message();
    }
console.log("Success send submit");