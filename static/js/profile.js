const socket = io();


function CreateElement(type, Class=null) {
	var element = document.createElement(type);
	
	if (Class != null) {
		element.classList.add(Class);
	}
	
	return element;
}

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
    "Light": [
        "#dddddd", "#bbbbbb", "#1f1f1f", "#3f3f3f",
        "#555555", "#777777", "#999999", "#dddddd",
        "#0f263d", "#2d1e3d", "#999999", "#aaaaaa",
        "#000000", "#000000", "#000000", "#000000"],
    "Dark": [
        "#1f1f1f", "#2f2f2f", "#bfbfbf", "#dfdfdf",
        "#9f9f9f", "#dfdfdf", "#3f3f3f", "#5f5f5f",
        "#4e80e5", "#aa80bf", "#2f2f2f", "#3f3f3f",
        "#000000", "#000000", "#000000", "#000000"],
    "Contrast": [
        "#000000", "#0f0f0f", "#ffffff", "#ffffff",
        "#ffffff", "#ff8f0f", "#000000", "#0f0700",
        "#007fff", "#7f00ff", "#000000", "#0f0f0f",
        "#000000", "#000000", "#000000", "#000000"],
    "Mint": [
        "#a6ddcb", "#8bbaaa", "#003f2a", "#005e3e",
        "#2a5446", "#3b7763", "#72998c", "#a6ddcb",
        "#0f263d", "#2d1e3d", "#4a997e", "#5dba9b",
        "#000000", "#000000", "#000000", "#000000"],
    "RedAndBlack": [
        "#000000", "#000000", "#000000", "#000000",
        "#000000", "#000000", "#000000", "#000000",
        "#000000", "#000000", "#000000", "#000000",
        "#000000", "#000000", "#000000", "#000000"],
}

function UpdateTheme() {
    var style = document.documentElement.style;
    var value = "", packed_theme = "";
    
    for (var i = 0; i < 16; i++) {
        value = document.querySelector("#" + props[i] + " .color").value;
        style.setProperty(props[i], value);
        packed_theme += value.slice(1);
    }

    socket.emit("save_theme", packed_theme);
}

function Theme(theme_name) {
    var theme_list = themes[theme_name];
    var style = document.documentElement.style;
    
    for (var i = 0; i < 16; i++) {
        style.setProperty(props[i], theme_list[i]);
        document.querySelector("#" + props[i] + " .color").value = theme_list[i];
    }
}

function setup_theme_values() {
    const butone = document.querySelector(".Butone1");
    var style = window.getComputedStyle(document.documentElement);
    
    for (var i = 0; i < 16; i++) {
        var elem = CreateElement("div", "theme_value");
        elem.id = props[i];
        var color = CreateElement("input", "color");
        color.type = "color";
        color.value = style.getPropertyValue(props[i]);
        var name = CreateElement("p", "name");
        name.textContent = props_names[i];
        elem.appendChild(color);
        elem.appendChild(name);
        butone.before(elem);
    }
}