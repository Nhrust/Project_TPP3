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

function use_theme(packed_theme) {
    var style = document.documentElement.style;

    for (var i = 0; i < 16; i++) {
        style.setProperty(props[i], "#" + packed_theme.slice(i * 6, (i + 1) * 6));
    }
}