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

const props = [
    "--bg-color",     "--bg-color-alt",
    "--color",        "--color-alt",
    "--button-color", "--button-color-hover",
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
    "Light": ["white", "lightblue", "black", "grey", "#7e7e7e", "#2e2e2e", "#444444", "#777777", "yellow", "orange", "#7c7c7c", "#84dadd", "#bbc3c4", "#d0e3e6", "#ffffff", "#3fe5ff"],
    "New": [
        "#0f0f0f", "#1f1f1f",
        "#ffffff", "#ffefdf",
        "#ffdfbf", "#000000",
        "#2f2f2f", "#ffdfbf",
        "#000000", "#000000",
        "#000000", "#000000",
        "#000000", "#000000",
        "#000000", "#000000",
    ],
}

function UpdateTheme() {
    var style = document.documentElement.style;
    var value;
    
    for (var i = 0; i < 16; i++) {
        value = document.querySelector("#" + props[i] + " .color").value;
        style.setProperty(props[i], value);
    }
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