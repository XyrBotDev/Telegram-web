import {
    getChats
} from "./api.js";

let chats = [];
let selectedChatId = null;

const chatListElement =
    document.getElementById("chat-list");

const searchElement =
    document.getElementById("chat-search");

function getInitial(title) {
    if (!title) {
        return "T";
    }

    return title
        .trim()
        .charAt(0)
        .toUpperCase();
}

function renderChatList(items) {
    chatListElement.innerHTML = "";

    if (!items.length) {
        chatListElement.innerHTML = `
            <div class="loading-state">
                No chats found.
            </div>
        `;

        return;
    }

    for (const chat of items) {
        const element =
            document.createElement("div");

        element.className = "chat-item";

        if (String(chat.id) === String(selectedChatId)) {
            element.classList.add("active");
        }

        const unread =
            Number(chat.unread_count || 0);

        element.innerHTML = `
            <div class="chat-item-avatar">
                ${escapeHtml(getInitial(chat.title))}
            </div>

            <div class="chat-item-content">

                <div class="chat-item-top">
                    <div class="chat-item-title">
                        ${escapeHtml(chat.title || "Unknown")}
                    </div>
                </div>

                <div class="chat-item-bottom">
                    <div class="chat-item-preview">
                        ${escapeHtml(
                            chat.chat_type || ""
                        )}
                    </div>

                    ${
                        unread > 0
                            ? `
                                <div class="unread-badge">
                                    ${unread}
                                </div>
                            `
                            : ""
                    }
                </div>

            </div>
        `;

        element.addEventListener(
            "click",
            () => {
                selectedChatId = chat.id;

                renderChatList(
                    getFilteredChats()
                );

                window.dispatchEvent(
                    new CustomEvent(
                        "telefarm:chat-selected",
                        {
                            detail: chat
                        }
                    )
                );
            }
        );

        chatListElement.appendChild(element);
    }
}

function getFilteredChats() {
    const query =
        searchElement.value
            .trim()
            .toLowerCase();

    if (!query) {
        return chats;
    }

    return chats.filter(chat =>
        String(chat.title || "")
            .toLowerCase()
            .includes(query)
    );
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

export async function loadChats() {
    chatListElement.innerHTML = `
        <div class="loading-state">
            Loading chats...
        </div>
    `;

    try {
        const response =
            await getChats(50);

        chats = response.chats || [];

        renderChatList(chats);

    } catch (error) {
        chatListElement.innerHTML = `
            <div class="loading-state">
                ${escapeHtml(error.message)}
            </div>
        `;

        console.error(error);
    }
}

searchElement.addEventListener(
    "input",
    () => {
        renderChatList(
            getFilteredChats()
        );
    }
);
