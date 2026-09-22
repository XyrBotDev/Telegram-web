import {
    getChats,
    searchMessages
} from "./api.js";

let chats = [];
let selectedChatId = null;
let searchTimer = null;
let searchMode = false;

const chatListElement =
    document.getElementById("chat-list");

const searchElement =
    document.getElementById("chat-search");

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getInitial(title) {
    return String(title || "T")
        .trim()
        .charAt(0)
        .toUpperCase() || "T";
}

function renderChatList(items) {
    searchMode = false;
    chatListElement.innerHTML = "";

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
            document.createElement("div");

        element.className = "chat-item";

        if (
            String(chat.id) ===
            String(selectedChatId)
        ) {
            element.classList.add("active");
        }

        element.innerHTML = `
            <div class="chat-item-avatar">
                ${escapeHtml(
                    getInitial(chat.title)
                )}
            </div>

            <div class="chat-item-content">
                <div class="chat-item-top">
                    <div class="chat-item-title">
                        ${escapeHtml(
                            chat.title || "Unknown"
                        )}
                    </div>
                </div>

                <div class="chat-item-bottom">
                    <div class="chat-item-preview">
                        ${escapeHtml(
                            chat.chat_type || ""
                        )}
                    </div>

                    ${
                        Number(
                            chat.unread_count || 0
                        ) > 0
                            ? `
                                <div class="unread-badge">
                                    ${Number(
                                        chat.unread_count
                                    )}
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
            .includes(query) ||
        String(chat.username || "")
            .toLowerCase()
            .includes(query)
    );
}

function renderSearchResults(results) {
    searchMode = true;
    chatListElement.innerHTML = "";

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
            document.createElement("div");

        element.className =
            "search-result-item";

        const preview =
            result.text || "Media message";

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
                        result.chat_id ?? ""
                    )}
                </div>

                <div class="search-result-text">
                    ${escapeHtml(preview)}
                </div>

                <div class="search-result-date">
                    ${formatDate(result.date)}
                </div>

            </div>
        `;

        element.addEventListener(
            "click",
            () => {
                openSearchResult(result);
            }
        );

        chatListElement.appendChild(element);
    }
}

function formatDate(value) {
    if (!value) {
        return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
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

function openSearchResult(result) {
    const chat =
        chats.find(
            item =>
                String(item.id) ===
                String(result.chat_id)
        );

    if (chat) {
        selectedChatId = chat.id;

        window.dispatchEvent(
            new CustomEvent(
                "telefarm:chat-selected",
                {
                    detail: chat
                }
            )
        );

        return;
    }

    window.dispatchEvent(
        new CustomEvent(
            "telefarm:search-result-selected",
            {
                detail: result
            }
        )
    );
}

async function performSearch(query) {
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
                ${escapeHtml(error.message)}
            </div>
        `;

        console.error(error);
    }
}

searchElement.addEventListener(
    "input",
    () => {
        clearTimeout(searchTimer);

        const query =
            searchElement.value;

        if (!query.trim()) {
            renderChatList(chats);
            return;
        }

        searchTimer = setTimeout(
            () => performSearch(query),
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

        renderChatList(chats);
    } catch (error) {
        chatListElement.innerHTML = `
            <div class="search-empty">
                ${escapeHtml(error.message)}
            </div>
        `;

        console.error(error);
    }
}
