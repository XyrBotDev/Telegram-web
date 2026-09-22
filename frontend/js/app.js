import {
    loadChats
} from "./chat-list.js";

const themeToggle =
    document.getElementById("theme-toggle");

function loadTheme() {
    const saved =
        localStorage.getItem(
            "telefarm-theme"
        );

    if (saved === "dark") {
        document.documentElement
            .setAttribute(
                "data-theme",
                "dark"
            );
    } else {
        document.documentElement
            .setAttribute(
                "data-theme",
                "light"
            );
    }
}

function toggleTheme() {
    const current =
        document.documentElement
            .getAttribute(
                "data-theme"
            );

    const next =
        current === "dark"
            ? "light"
            : "dark";

    document.documentElement
        .setAttribute(
            "data-theme",
            next
        );

    localStorage.setItem(
        "telefarm-theme",
        next
    );
}

themeToggle.addEventListener(
    "click",
    toggleTheme
);

loadTheme();

loadChats();
