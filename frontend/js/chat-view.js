import {
    getChat,
    getMessages,
    getChatPhotoUrl
} from "./api.js";

const app =
    document.getElementById(
        "app"
    );

const chatTitle =
    document.getElementById(
        "chat-title"
    );

const chatStatus =
    document.getElementById(
        "chat-status"
    );

const chatAvatar =
    document.getElementById(
        "chat-avatar"
    );

const messagesElement =
    document.getElementById(
        "messages"
    );

const messageInput =
    document.getElementById(
        "message-input"
    );

const sendButton =
    document.getElementById(
        "send-button"
    );

const mobileBack =
    document.getElementById(
        "mobile-back"
    );

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getInitial(title) {
    return (
        String(title || "T")
            .trim()
            .charAt(0)
            .toUpperCase() || "T"
    );
}

function setChatAvatar(chat) {
    chatAvatar.innerHTML =
        "";

    if (chat.photo) {
        const image =
            document.createElement(
                "img"
            );

        image.src =
            getChatPhotoUrl(
                chat.id
            );

        image.alt =
            chat.title ||
            "Chat";

        image.className =
            "chat-avatar-image";

        image.onerror =
            () => {
                chatAvatar.textContent =
                    getInitial(
                        chat.title
                    );
            };

        chatAvatar.appendChild(
            image
        );

        return;
    }

    chatAvatar.textContent =
        getInitial(
            chat.title
        );
}

function formatTime(
    dateValue
) {
    if (!dateValue) {
        return "";
    }

    const date =
        new Date(
            dateValue
        );

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
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

function renderMessages(
    messages
) {
    messagesElement.innerHTML =
        "";

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
            document.createElement(
                "div"
            );

        row.className =
            "message-row";

        if (message.outgoing) {
            row.classList.add(
                "outgoing"
            );
        }

        const text =
            message.text || "";

        row.innerHTML = `
            <div class="message-bubble">

                <div class="message-text">
                    ${escapeHtml(
                        text
                    )}
                </div>

                <div class="message-meta">
                    ${formatTime(
                        message.date
                    )}
                    ${
                        message.edited
                            ? " · edited"
                            : ""
                    }
                </div>

            </div>
        `;

        messagesElement.appendChild(
            row
        );
    }

    messagesElement.scrollTop =
        messagesElement.scrollHeight;
}

async function openChat(
    chat
) {
    app.classList.add(
        "chat-open"
    );

    chatTitle.textContent =
        chat.title ||
        "Unknown";

    chatStatus.textContent =
        chat.chat_type ||
        "";

    setChatAvatar(chat);

    messageInput.disabled =
        false;

    sendButton.disabled =
        false;

    messagesElement.innerHTML = `
        <div class="loading-state">
            Loading messages...
        </div>
    `;

    try {
        const response =
            await getChat(
                chat.id
            );

        const currentChat =
            response.chat ||
            chat;

        chatTitle.textContent =
            currentChat.title ||
            chat.title ||
            "Unknown";

        chatStatus.textContent =
            currentChat.chat_type ||
            chat.chat_type ||
            "";

        setChatAvatar(
            currentChat
        );

        const responseMessages =
            await getMessages(
                chat.id,
                50
            );

        const messages =
            responseMessages.messages ||
            [];

        renderMessages(
            messages
        );

    } catch (error) {
        messagesElement.innerHTML = `
            <div class="empty-state">
                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>
            </div>
        `;

        console.error(error);
    }
}

window.addEventListener(
    "telefarm:chat-selected",
    event => {
        openChat(
            event.detail
        );
    }
);

mobileBack.addEventListener(
    "click",
    () => {
        app.classList.remove(
            "chat-open"
        );

        messageInput.disabled =
            true;

        sendButton.disabled =
            true;
    }
);
