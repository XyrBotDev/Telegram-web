import {
    getChat,
    getMessages
} from "./api.js";

const app =
    document.getElementById("app");

const chatTitle =
    document.getElementById("chat-title");

const chatStatus =
    document.getElementById("chat-status");

const chatAvatar =
    document.getElementById("chat-avatar");

const messagesElement =
    document.getElementById("messages");

const messageInput =
    document.getElementById("message-input");

const sendButton =
    document.getElementById("send-button");

const mobileBack =
    document.getElementById("mobile-back");

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getInitial(title) {
    if (!title) {
        return "T";
    }

    return title
        .trim()
        .charAt(0)
        .toUpperCase();
}

function formatTime(dateValue) {
    if (!dateValue) {
        return "";
    }

    const date =
        new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

    return date.toLocaleTimeString(
        [],
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}

function renderMessages(messages) {
    messagesElement.innerHTML = "";

    if (!messages.length) {
        messagesElement.innerHTML = `
            <div class="empty-state">
                <p>No messages yet.</p>
            </div>
        `;

        return;
    }

    const ordered =
        [...messages].reverse();

    for (const message of ordered) {
        const row =
            document.createElement("div");

        row.className =
            "message-row";

        if (message.outgoing) {
            row.classList.add("outgoing");
        }

        const text =
            message.text || "";

        row.innerHTML = `
            <div class="message-bubble">

                <div class="message-text">
                    ${escapeHtml(text)}
                </div>

                <div class="message-meta">
                    ${formatTime(message.date)}
                    ${
                        message.edited
                            ? " · edited"
                            : ""
                    }
                </div>

            </div>
        `;

        messagesElement.appendChild(row);
    }

    messagesElement.scrollTop =
        messagesElement.scrollHeight;
}

async function openChat(chat) {
    app.classList.add("chat-open");

    chatTitle.textContent =
        chat.title || "Unknown";

    chatAvatar.textContent =
        getInitial(chat.title);

    chatStatus.textContent =
        chat.chat_type || "";

    messageInput.disabled = false;
    sendButton.disabled = false;

    messagesElement.innerHTML = `
        <div class="loading-state">
            Loading messages...
        </div>
    `;

    try {
        const response =
            await getChat(chat.id);

        if (response.chat) {
            chatTitle.textContent =
                response.chat.title ||
                chat.title ||
                "Unknown";

            chatAvatar.textContent =
                getInitial(
                    response.chat.title ||
                    chat.title
                );
        }

        const messages =
            await getMessages(
                chat.id,
                50
            );

        renderMessages(messages);

    } catch (error) {
        messagesElement.innerHTML = `
            <div class="empty-state">
                <p>${escapeHtml(error.message)}</p>
            </div>
        `;

        console.error(error);
    }
}

window.addEventListener(
    "telefarm:chat-selected",
    event => {
        openChat(event.detail);
    }
);

mobileBack.addEventListener(
    "click",
    () => {
        app.classList.remove("chat-open");

        messageInput.disabled = true;
        sendButton.disabled = true;
    }
);
