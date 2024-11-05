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
const wtcolors=["white", "lightblue", "blue", "rgba(72, 182, 255, 0.493)"];
const dtcolors=["#000", "#222", "#fff", "#444", "rgba(255, 72, 72, 0.493)"];
const monochrome=["white", 'black', "#707070"];
const mint=["#00ffaa", "#01ffd5", "#fff", "#42be95", "#64f1c2"];
const red_black=["red", "black", "#250505"];
const pink=["#fff", "#ff4ce1", "#c444b9"];
const scyfi=["#3f1a7a", "#3a24b8", "#4ab7ff", "#4a677a", "#25167a"];
const neon=["#1c115c", "#49c6ff", "#e358ff", "#0b0624"];
const mini=["#d3d3d3", "#7e7e7e", "#000000", "#5c5c5c"];
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
    style.setProperty('--bg-color', wtcolors[0]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', wtcolors[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', wtcolors[2]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', wtcolors[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', wtcolors[3]);
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

function Monochrome(){
    var style = document.documentElement.style;
    style.setProperty('--bg-color', monochrome[0]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', monochrome[2]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', monochrome[0]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', monochrome[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', monochrome[0]);
}

function Mint(){
    var style = document.documentElement.style;
    style.setProperty('--bg-color', mint[0]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', mint[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', mint[2]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', mint[4]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', mint[3]);
}

function RedBlack(){
    var style = document.documentElement.style;
    style.setProperty('--bg-color', red_black[2]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', red_black[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', red_black[0]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', red_black[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', red_black[0]);
}

function Pink(){
    var style = document.documentElement.style;
    style.setProperty('--bg-color', pink[1]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', pink[2]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', pink[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', pink[0]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', pink[1]);
}

function ScyFi(){
    var style = document.documentElement.style;
    style.setProperty('--bg-color', scyfi[0]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', scyfi[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', scyfi[3]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', scyfi[2]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', scyfi[4]);
}

function Neon(){
    var style = document.documentElement.style;
    style.setProperty('--bg-color', neon[3]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', neon[0]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', neon[2]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', neon[0]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', neon[1]);
}

function Minimalism(){
    var style = document.documentElement.style;
    style.setProperty('--bg-color', mini[0]);
    var style = document.documentElement.style;
    style.setProperty('--bg-color-alt', mini[1]);
    var style = document.documentElement.style;
    style.setProperty('--button-color', mini[2]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg', mini[0]);
    var style = document.documentElement.style;
    style.setProperty('--button-bg-hover', mini[3]);
}