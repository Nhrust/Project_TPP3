function Open(name, eman){
    var name = document.querySelector(name);
    var eman = document.querySelector(eman);
    var active = document.querySelector(".active");
    var selected = document.querySelector(".SELECTED");
    active .classList.remove("active");
    selected .classList.remove("SELECTED");
    name.classList.add("active");
    eman.classList.add("SELECTED");
}

qwerty = {
"Light":["white", "lightblue", "black", "grey", "#7e7e7e", "#2e2e2e", "#444444", "#777777", "yellow", "orange", "#7c7c7c", "#84dadd", "#bbc3c4", "#d0e3e6", "#ffffff", "#3fe5ff"]
}
elem1 = document.querySelector(".BG_clr"),
elem2 = document.querySelector(".F_clr"),
elem3 = document.querySelector(".Text_clr"),

function UpdateTheme(){
    var style = document.documentElement.style;
    var index1 = Number(elem1.value);
    style.setProperty('--bg-color', color[index1]);
    var style = document.documentElement.style;
    var index2 = Number(elem2.value);
    style.setProperty('--bg-color-alt', color[index2]);
    var style = document.documentElement.style;
    var index3 = Number(elem3.value);
    style.setProperty('--button-color', color[index3]);

}

function Theme(namelist){
    var list = qwerty[namelist];
    var style = document.documentElement.style;
    style.setProperty('--bg-color', list[0]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', list[1]);
    var style = document.documentElement.style;
    style.setProperty('--color', list[2]);
    var style = document.documentElement.style;
    style.setProperty('--color-alt', list[3]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', list[4]);
    var style = document.documentElement.style;
    style.setProperty('--button-color-alt', list[5]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', list[6]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', list[7]);
    var style = document.documentElement.style;
    style.setProperty('--link-color', list[8]);
    var style = document.documentElement.style;
    style.setProperty('--link-color-used', list[9]);
    var style = document.documentElement.style;
    style.setProperty('--self-text', list[10]);
    var style = document.documentElement.style;
    style.setProperty('--other-text', list[11]);
    var style = document.documentElement.style;
    style.setProperty('--border-color', list[12]);
    var style = document.documentElement.style;
    style.setProperty('--border-color-hover', list[13]);
    var style = document.documentElement.style;
    style.setProperty('--message-send', list[14]);
    var style = document.documentElement.style;
    style.setProperty('--message-checked', list[15]);
}