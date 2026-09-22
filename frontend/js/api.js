const API_BASE = "";


function getSessionId() {
    return sessionStorage.getItem(
        "telefarm_session_id"
    );
}


async function request(
    path,
    options = {}
) {
    const response = await fetch(
        `${API_BASE}${path}`,
        {
            ...options,

            headers: {
                "Content-Type":
                    "application/json",

                ...(options.headers || {})
            }
        }
    );


    const data =
        await response
            .json()
            .catch(() => ({}));


    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Request failed."
        );
    }


    return data;
}


export async function getChats(
    limit = 50
) {
    const sessionId =
        getSessionId();


    if (!sessionId) {
        window.location.replace(
            "/login.html"
        );

        throw new Error(
            "Authentication required."
        );
    }


    return request(
        `/api/chats?session_id=${encodeURIComponent(sessionId)}&limit=${limit}`
    );
}


export async function getChat(
    chatId
) {
    const sessionId =
        getSessionId();


    if (!sessionId) {
        window.location.replace(
            "/login.html"
        );

        throw new Error(
            "Authentication required."
        );
    }


    return request(
        `/api/chats/${encodeURIComponent(chatId)}?session_id=${encodeURIComponent(sessionId)}`
    );
}


export async function getMessages(
    chatId,
    limit = 50
) {
    const sessionId =
        getSessionId();


    if (!sessionId) {
        window.location.replace(
            "/login.html"
        );

        throw new Error(
            "Authentication required."
        );
    }


    return request(
        `/api/messages/${encodeURIComponent(chatId)}?session_id=${encodeURIComponent(sessionId)}&limit=${limit}`
    );
}


export async function searchMessages(
    query,
    chatId = null,
    limit = 50
) {
    const sessionId =
        getSessionId();


    if (!sessionId) {
        window.location.replace(
            "/login.html"
        );

        throw new Error(
            "Authentication required."
        );
    }


    const params =
        new URLSearchParams();


    params.set(
        "session_id",
        sessionId
    );


    params.set(
        "query",
        query
    );


    params.set(
        "limit",
        String(limit)
    );


    if (chatId !== null) {
        params.set(
            "chat_id",
            String(chatId)
        );
    }


    return request(
        `/api/search/messages?${params.toString()}`
    );
            }
