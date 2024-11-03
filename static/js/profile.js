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

const color=['red', 'orange', 'yellow', 'green', 'lightblue', "blue", "purple", "pink", "broun", "white", "grey", "black"];
const dtcolors=["#000", "#222", "#fff", "#444", "rgba(255, 72, 72, 0.493)"];
const elem1 = document.querySelector(".BG_clr");
const elem2 = document.querySelector(".F_clr");
const elem3 = document.querySelector(".Text_clr");



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

function LightTheme(){
    var style = document.documentElement.style;
    style.setProperty('--bg-color', color[9]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', color[4]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', color[5]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', color[4]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', color[5]);
}

function DarkTheme(){
    var style = document.documentElement.style;
    style.setProperty('--bg-color', dtcolors[0]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', dtcolors[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', dtcolors[2]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', dtcolors[3]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', dtcolors[4]);
}