const phoneForm =
    document.getElementById("phone-form");

const codeForm =
    document.getElementById("code-form");

const passwordForm =
    document.getElementById("password-form");

const phoneInput =
    document.getElementById("phone-number");

const codeInput =
    document.getElementById("verification-code");

const passwordInput =
    document.getElementById(
        "two-factor-password"
    );

const phoneButton =
    document.getElementById("phone-button");

const codeButton =
    document.getElementById("code-button");

const passwordButton =
    document.getElementById(
        "password-button"
    );

const messageElement =
    document.getElementById(
        "login-message"
    );

const loadingElement =
    document.getElementById(
        "login-loading"
    );

let sessionId = null;

function showMessage(
    message,
    type = ""
) {
    messageElement.textContent =
        message;

    messageElement.className =
        "login-message";

    if (type) {
        messageElement.classList.add(
            type
        );
    }
}

function clearMessage() {
    messageElement.textContent = "";

    messageElement.className =
        "login-message hidden";
}

function setLoading(
    loading,
    button = null
) {
    loadingElement.classList.toggle(
        "hidden",
        !loading
    );

    if (button) {
        button.disabled = loading;
    }
}

async function apiRequest(
    path,
    options = {}
) {
    const response =
        await fetch(path, {
            ...options,
            headers: {
                "Content-Type":
                    "application/json",
                ...(options.headers || {})
            }
        });

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

function saveSession(id) {
    /*
     * This is the temporary Telefarm
     * session identifier.
     *
     * It is not the Telegram session
     * string.
     */
    sessionStorage.setItem(
        "telefarm_session_id",
        id
    );
}

function getSavedSession() {
    return sessionStorage.getItem(
        "telefarm_session_id"
    );
}

function openApplication() {
    window.location.replace("/");
}

async function finishLogin(id) {
    sessionId = id;

    saveSession(sessionId);

    try {
        const result =
            await apiRequest(
                `/api/auth/me?session_id=${encodeURIComponent(sessionId)}`
            );

        if (!result.authenticated) {
            throw new Error(
                "Authentication could not be confirmed."
            );
        }

        showMessage(
            "Signed in successfully.",
            "success"
        );

        setTimeout(
            openApplication,
            300
        );

    } catch (error) {
        sessionStorage.removeItem(
            "telefarm_session_id"
        );

        throw error;
    }
}

phoneForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        clearMessage();

        const phoneNumber =
            phoneInput.value.trim();

        if (!phoneNumber) {
            showMessage(
                "Enter your phone number."
            );
            return;
        }

        setLoading(
            true,
            phoneButton
        );

        try {
            const result =
                await apiRequest(
                    "/api/auth/phone",
                    {
                        method: "POST",
                        body: JSON.stringify({
                            phone_number:
                                phoneNumber
                        })
                    }
                );

            if (!result.session_id) {
                throw new Error(
                    "Login session was not created."
                );
            }

            sessionId =
                result.session_id;

            if (result.requires_code) {
                phoneForm.classList.add(
                    "hidden"
                );

                codeForm.classList.remove(
                    "hidden"
                );

                codeInput.focus();

                showMessage(
                    "A verification code was requested. Enter the code sent by Telegram."
                );
            } else if (
                result.success
            ) {
                await finishLogin(
                    sessionId
                );
            } else {
                showMessage(
                    result.message ||
                    "Unable to continue."
                );
            }

        } catch (error) {
            showMessage(
                error.message,
                "error"
            );
        } finally {
            setLoading(
                false,
                phoneButton
            );
        }
    }
);

codeForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        clearMessage();

        const code =
            codeInput.value.trim();

        if (!code) {
            showMessage(
                "Enter the verification code."
            );
            return;
        }

        if (!sessionId) {
            showMessage(
                "Login session is missing."
            );
            return;
        }

        setLoading(
            true,
            codeButton
        );

        try {
            const result =
                await apiRequest(
                    "/api/auth/verify-code",
                    {
                        method: "POST",
                        body: JSON.stringify({
                            session_id:
                                sessionId,
                            code
                        })
                    }
                );

            if (
                result.requires_password
            ) {
                codeForm.classList.add(
                    "hidden"
                );

                passwordForm.classList.remove(
                    "hidden"
                );

                passwordInput.focus();

                showMessage(
                    "Two-factor authentication is enabled. Enter your password."
                );

                return;
            }

            if (result.success) {
                await finishLogin(
                    sessionId
                );
                return;
            }

            showMessage(
                result.message ||
                "Verification failed."
            );

        } catch (error) {
            showMessage(
                error.message,
                "error"
            );
        } finally {
            setLoading(
                false,
                codeButton
            );
        }
    }
);

passwordForm.addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        clearMessage();

        const password =
            passwordInput.value;

        if (!password) {
            showMessage(
                "Enter your two-factor password."
            );
            return;
        }

        if (!sessionId) {
            showMessage(
                "Login session is missing."
            );
            return;
        }

        setLoading(
            true,
            passwordButton
        );

        try {
            const result =
                await apiRequest(
                    "/api/auth/verify-password",
                    {
                        method: "POST",
                        body: JSON.stringify({
                            session_id:
                                sessionId,
                            password
                        })
                    }
                );

            if (result.success) {
                await finishLogin(
                    sessionId
                );
                return;
            }

            showMessage(
                result.message ||
                "Authentication failed."
            );

        } catch (error) {
            showMessage(
                error.message,
                "error"
            );
        } finally {
            setLoading(
                false,
                passwordButton
            );
        }
    }
);

async function checkExistingSession() {
    const savedSession =
        getSavedSession();

    if (!savedSession) {
        return;
    }

    try {
        const result =
            await apiRequest(
                `/api/auth/me?session_id=${encodeURIComponent(savedSession)}`
            );

        if (result.authenticated) {
            window.location.replace("/");
        } else {
            sessionStorage.removeItem(
                "telefarm_session_id"
            );
        }

    } catch {
        sessionStorage.removeItem(
            "telefarm_session_id"
        );
    }
}

checkExistingSession();
