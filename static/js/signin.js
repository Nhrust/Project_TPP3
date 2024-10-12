const pass1 = document.querySelector("#pass1");
const pass2 = document.querySelector("#pass2");

function check_passwords() {
    var password1 = String(pass1.value);
    var password2 = String(pass2.value);
    var wrong1 = (password1.length < 4) && (password1.length != 0);
    var wrong2 = (password1 != password2) && (password2 != "") && (!wrong1);

    if (pass1.classList.contains("wrong")) {
        if (!wrong1) {
            pass1.classList.remove("wrong");
        }
    }
    else {
        if (wrong1) {
            pass1.classList.add("wrong");
        }
    }
    if (pass2.classList.contains("wrong")) {
        if (!wrong2) {
            pass2.classList.remove("wrong");
        }
    }
    else {
        if (wrong2) {
            pass2.classList.add("wrong");
        }
    }
}