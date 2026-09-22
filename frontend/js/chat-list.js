import {
    getChats,
    searchMessages,
    getChatPhotoUrl
} from "./api.js";

let chats = [];
let selectedChatId = null;
let searchTimer = null;

const chatListElement =
    document.getElementById(
        "chat-list"
    );

const searchElement =
    document.getElementById(
        "chat-search"
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

function createAvatar(
    chat,
    className = "chat-item-avatar"
) {
    const initial =
        getInitial(chat.title);

    if (chat.photo) {
        const image =
            document.createElement(
                "img"
            );

        image.className =
            className;

        image.src =
            getChatPhotoUrl(chat.id);

        image.alt =
            chat.title || "Chat";

        image.loading =
            "lazy";

        image.onerror =
            () => {
                image.replaceWith(
                    createTextAvatar(
                        chat,
                        className
                    )
                );
            };

        return image;
    }

    return createTextAvatar(
        chat,
        className
    );
}

function createTextAvatar(
    chat,
    className
) {
    const element =
        document.createElement(
            "div"
        );

    element.className =
        className;

    element.textContent =
        getInitial(chat.title);

    return element;
}

function renderChatList(items) {
    chatListElement.innerHTML =
        "";

    if (!items.length) {
        chatListElement.innerHTML = `
            <div class="search-empty">
                No chats found.
            </div>
        `;

        return;
    }

    for (const chat of items) {
        const element =
            document.createElement(
                "div"
            );

        element.className =
            "chat-item";

        if (
            String(chat.id) ===
            String(selectedChatId)
        ) {
            element.classList.add(
                "active"
            );
        }

        const avatar =
            createAvatar(chat);

        const content =
            document.createElement(
                "div"
            );

        content.className =
            "chat-item-content";

        const top =
            document.createElement(
                "div"
            );

        top.className =
            "chat-item-top";

        top.innerHTML = `
            <div class="chat-item-title">
                ${escapeHtml(
                    chat.title ||
                    "Unknown"
                )}
            </div>
        `;

        const bottom =
            document.createElement(
                "div"
            );

        bottom.className =
            "chat-item-bottom";

        bottom.innerHTML = `
            <div class="chat-item-preview">
                ${escapeHtml(
                    chat.chat_type ||
                    ""
                )}
            </div>
        `;

        if (
            Number(
                chat.unread_count || 0
            ) > 0
        ) {
            const badge =
                document.createElement(
                    "div"
                );

            badge.className =
                "unread-badge";

            badge.textContent =
                String(
                    chat.unread_count
                );

            bottom.appendChild(
                badge
            );
        }

        content.appendChild(
            top
        );

        content.appendChild(
            bottom
        );

        element.appendChild(
            avatar
        );

        element.appendChild(
            content
        );

        element.addEventListener(
            "click",
            () => {
                selectedChatId =
                    chat.id;

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

        chatListElement.appendChild(
            element
        );
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

    return chats.filter(
        chat =>
            String(
                chat.title || ""
            )
                .toLowerCase()
                .includes(query) ||
            String(
                chat.username || ""
            )
                .toLowerCase()
                .includes(query)
    );
}

function formatDate(value) {
    if (!value) {
        return "";
    }

    const date =
        new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "";
    }

    return date.toLocaleString(
        [],
        {
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}

function renderSearchResults(
    results
) {
    chatListElement.innerHTML =
        "";

    if (!results.length) {
        chatListElement.innerHTML = `
            <div class="search-empty">
                No messages found.
            </div>
        `;

        return;
    }

    for (const result of results) {
        const element =
            document.createElement(
                "div"
            );

        element.className =
            "search-result-item";

        const preview =
            result.text ||
            "Media message";

        element.innerHTML = `
            <div class="search-result-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M20 11a8 8 0 1 1-2.34-5.66"/>
                    <path d="M20 4v7h-7"/>
                </svg>
            </div>

            <div class="search-result-content">

                <div class="search-result-title">
                    Chat ${escapeHtml(
                        result.chat_id ??
                        ""
                    )}
                </div>

                <div class="search-result-text">
                    ${escapeHtml(
                        preview
                    )}
                </div>

                <div class="search-result-date">
                    ${formatDate(
                        result.date
                    )}
                </div>

            </div>
        `;

        element.addEventListener(
            "click",
            () => {
                const chat =
                    chats.find(
                        item =>
                            String(
                                item.id
                            ) ===
                            String(
                                result.chat_id
                            )
                    );

                if (chat) {
                    selectedChatId =
                        chat.id;

                    window.dispatchEvent(
                        new CustomEvent(
                            "telefarm:chat-selected",
                            {
                                detail:
                                    chat
                            }
                        )
                    );
                }
            }
        );

        chatListElement.appendChild(
            element
        );
    }
}

async function performSearch(
    query
) {
    const trimmed =
        query.trim();

    if (!trimmed) {
        renderChatList(chats);
        return;
    }

    chatListElement.innerHTML = `
        <div class="search-loading">
            Searching...
        </div>
    `;

    try {
        const response =
            await searchMessages(
                trimmed,
                null,
                50
            );

        renderSearchResults(
            response.results || []
        );
    } catch (error) {
        chatListElement.innerHTML = `
            <div class="search-empty">
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;

        console.error(error);
    }
}

searchElement.addEventListener(
    "input",
    () => {
        clearTimeout(
            searchTimer
        );

        const query =
            searchElement.value;

        if (!query.trim()) {
            renderChatList(chats);
            return;
        }

        searchTimer =
            setTimeout(
                () =>
                    performSearch(
                        query
                    ),
                350
            );
    }
);

export async function loadChats() {
    chatListElement.innerHTML = `
        <div class="loading-state">
            Loading chats...
        </div>
    `;

    try {
        const response =
            await getChats(50);

        chats =
            response.chats || [];

        renderChatList(
            chats
        );
    } catch (error) {
        chatListElement.innerHTML = `
            <div class="search-empty">
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;

        console.error(error);
    }
            }
