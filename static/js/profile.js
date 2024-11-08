function Open(view_class, menu_class) {
    var active = document.querySelector(".active_view");
    var selected = document.querySelector(".selected_menu");
    active.classList.remove("active_view");
    selected.classList.remove("selected_menu");

    var view_elem = document.querySelector(view_class);
    var menu_item = document.querySelector(menu_class);
    view_elem.classList.add("active_view");
    menu_item.classList.add("selected_menu");
}

const props = [
    "--bg-color",     "--bg-color-alt",
    "--color",        "--color-alt",
    "--button-color", "--button-color-alt",
    "--button-bg",    "--button-bg-hover",
    "--link-color",   "--link-color-used",
    "--self-text",    "--other-text",
    "--border-color", "--border-color-hover",
    "--message-send", "--message-checked"
];

const props_names = [
    "Цвет фона",              "Цвет фона альтернативный",
    "Цвет текста",            "Цвет текста альтернативный",
    "Цвет текста интерфейса", "Цвет текста интерфейса альтернативный",
    "Цвет фона интерфейса",   "Цвет фона интерфейса альтернативный",
    "Цвет ссылок",            "Цвет ссылок альтернативный",
    "Цвет моих сообщений",    "Цвет сообщений собеседника",
    "Цвет границ",            "Цвет границ альтернативный",
    "???",                    "???",
];

const themes = {
    "Light": ["white", "lightblue", "black", "grey", "#7e7e7e", "#2e2e2e", "#444444", "#777777", "yellow", "orange", "#7c7c7c", "#84dadd", "#bbc3c4", "#d0e3e6", "#ffffff", "#3fe5ff"]
}

function UpdateTheme() {
    var index1 = Number(document.querySelector(".BG_clr"  ).value);
    var index2 = Number(document.querySelector(".F_clr"   ).value);
    var index3 = Number(document.querySelector(".Text_clr").value);

    var style = document.documentElement.style;
    style.setProperty('--bg-color', color[index1]);
    style.setProperty('--bg-color-alt', color[index2]);
    style.setProperty('--button-color', color[index3]);
}

function Theme(theme_name) {
    var theme_list = themes[theme_name];
    var style = document.documentElement.style;
    
    for (var i = 0; i < 16; i++) {
        style.setProperty(props[i], theme_list[i]);
    }
}