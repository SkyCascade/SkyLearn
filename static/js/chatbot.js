/* =========================================================
   SkyLearn AI Chatbot – Client Logic
   ========================================================= */
(function () {
    "use strict";

    // Detect language prefix from current URL (i18n_patterns support)
    var langMatch = window.location.pathname.match(/^\/([a-z]{2}(?:-[a-z]{2})?)\//);
    var langPrefix = langMatch ? "/" + langMatch[1] : "";
    var CHATBOT_API = langPrefix + "/ai/chatbot/";
    const MAX_HISTORY = 20; // keep last N messages for context

    // DOM elements
    const toggleBtn = document.getElementById("chatbot-toggle");
    const chatWindow = document.getElementById("chatbot-window");
    const messagesDiv = document.getElementById("chatbot-messages");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");
    const sendBtn = document.getElementById("chatbot-send");
    const clearBtn = document.getElementById("chatbot-clear");
    const minimizeBtn = document.getElementById("chatbot-minimize");
    const badge = document.getElementById("chatbot-badge");
    const iconOpen = toggleBtn.querySelector(".chatbot-icon-open");
    const iconClose = toggleBtn.querySelector(".chatbot-icon-close");

    let isOpen = false;
    let history = []; // {role, content}

    // ---- Toggle window ----
    function openChat() {
        isOpen = true;
        chatWindow.classList.remove("d-none");
        iconOpen.classList.add("d-none");
        iconClose.classList.remove("d-none");
        badge.classList.add("d-none");
        input.focus();
        scrollToBottom();
    }

    function closeChat() {
        isOpen = false;
        chatWindow.classList.add("d-none");
        iconOpen.classList.remove("d-none");
        iconClose.classList.add("d-none");
    }

    toggleBtn.addEventListener("click", function () {
        isOpen ? closeChat() : openChat();
    });

    minimizeBtn.addEventListener("click", closeChat);

    // ---- Input handling ----
    input.addEventListener("input", function () {
        sendBtn.disabled = !input.value.trim();
    });

    // ---- Send message ----
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        appendMessage("user", text);
        history.push({ role: "user", content: text });
        input.value = "";
        sendBtn.disabled = true;

        showTyping();
        fetchReply(text);
    });

    // ---- API call ----
    function fetchReply(message) {
        const csrfToken = getCookie("csrftoken");
        const payload = {
            message: message,
            history: history.slice(-MAX_HISTORY),
        };

        fetch(CHATBOT_API, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify(payload),
        })
            .then(function (res) {
                if (!res.ok) throw new Error("HTTP " + res.status);
                return res.json();
            })
            .then(function (data) {
                hideTyping();
                if (data.reply) {
                    appendMessage("bot", data.reply);
                    history.push({ role: "assistant", content: data.reply });
                } else if (data.error) {
                    appendMessage("bot", "⚠️ " + data.error);
                }
            })
            .catch(function () {
                hideTyping();
                appendMessage("bot", "⚠️ Unable to connect. Please try again later.");
            });
    }

    // ---- DOM helpers ----
    function appendMessage(role, text) {
        var msgDiv = document.createElement("div");
        msgDiv.className = "chatbot-msg chatbot-msg-" + (role === "user" ? "user" : "bot");

        var avatarDiv = document.createElement("div");
        avatarDiv.className = "chatbot-msg-avatar";
        avatarDiv.innerHTML =
            role === "user"
                ? '<i class="fas fa-user"></i>'
                : '<i class="fas fa-robot"></i>';

        var bubbleDiv = document.createElement("div");
        bubbleDiv.className = "chatbot-msg-bubble";
        bubbleDiv.textContent = text;

        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(bubbleDiv);
        messagesDiv.appendChild(msgDiv);
        scrollToBottom();
    }

    function showTyping() {
        var existing = document.getElementById("chatbot-typing");
        if (existing) return;

        var typingDiv = document.createElement("div");
        typingDiv.id = "chatbot-typing";
        typingDiv.className = "chatbot-msg chatbot-msg-bot";
        typingDiv.innerHTML =
            '<div class="chatbot-msg-avatar"><i class="fas fa-robot"></i></div>' +
            '<div class="chatbot-msg-bubble chatbot-typing">' +
            "<span></span><span></span><span></span>" +
            "</div>";
        messagesDiv.appendChild(typingDiv);
        scrollToBottom();
    }

    function hideTyping() {
        var el = document.getElementById("chatbot-typing");
        if (el) el.remove();
    }

    function scrollToBottom() {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // ---- Clear chat ----
    clearBtn.addEventListener("click", function () {
        // Keep only the initial greeting
        while (messagesDiv.children.length > 1) {
            messagesDiv.removeChild(messagesDiv.lastChild);
        }
        history = [];
    });

    // ---- CSRF helper ----
    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
        return "";
    }
})();
