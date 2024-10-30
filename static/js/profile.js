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