document.querySelector(".find_form")
    .onsubmit = function(event) {
        event.preventDefault();
        var request = document.querySelector(".find_input").value;
        socket.emit('find_request', request);
    }