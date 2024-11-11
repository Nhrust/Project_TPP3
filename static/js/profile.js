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
        "white", "lightblue", "black", "grey",
        "black", "#2e2e2e", "#444444", "#777777",
        "yellow", "orange", "#7c7c7c", "#84dadd",
        "#bbc3c4", "#d0e3e6", "#ffffff", "#3fe5ff"],
    "Dark": [
        "black", "rgb(56, 56, 56)", "lightred", "darkred",
        "white", "#7e7e7e", "rgb(68,68,68)", "rgb(255,72,72)",
        "rgb(55,232,255)", "rgb(176,58,255)", "rgb(255,102,102)", "rgb(155,50,50)",
        "rgb(201, 32, 32)", "rgb(132, 22, 22)", "#000000", "#000000"],
    "Monochrome": [
        "Black", "rgb(189, 189, 189)", "rgb(209, 209, 209)", "rgb(122,122,122)",
        "black", "rgb(194,194,194", "rgb(163, 163, 163)", "rgb(94,94,94)",
        "rgb(145, 173, 186)", "rgb(143, 116, 170)", "rgb(178, 149, 149)", "rgb(181, 120, 120",
        "white", "white", "#000000", "#000000"],
    "Mint": [
        "#22d889", "#369b67", "#ffffff", "#ddddff",
        "#ffffff", "#ddddff", "#3ed08c", "#ff4848",
        "#45ff38", "#a5ff38", "#57c185", "#329a64",
        "#29d19e", "#168886", "#000000", "#000000"],
    "RedAndBlack": [
        "#000000", "#1c1c1c", "#ff0000", "#700000",
        "#ff0000", "#700000", "#000000", "#000000",
        "#c15757", "#612929", "#b83d3d", "#6d5454",
        "#ff0000", "#000000", "#000000", "#000000"],
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