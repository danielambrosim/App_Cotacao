(function () {
    "use strict";

    var updateTimeSpan = document.getElementById("updateTime");
    if (updateTimeSpan) {
        updateTimeSpan.textContent = new Date().toLocaleString("pt-BR", {
            dateStyle: "full",
            timeStyle: "medium",
            hour12: false
        });
    }

    var refreshButton = document.getElementById("refreshButton");
    if (refreshButton) {
        refreshButton.addEventListener("click", function () {
            this.classList.add("is-loading");
            this.disabled = true;
            this.textContent = "Atualizando...";
            setTimeout(function () {
                window.location.reload();
            }, 500);
        });
    }

    var overlay = document.getElementById("subscribeOverlay");
    if (!overlay) {
        return;
    }

    var SUBSCRIBED_COOKIE = "app_cotacao_subscribed=1";

    function getCookie(name) {
        var prefix = name + "=";
        return document.cookie.split("; ").filter(function (item) {
            return item.indexOf(prefix) === 0;
        }).length > 0;
    }

    function setSubscribedCookie() {
        var expires = new Date();
        expires.setFullYear(expires.getFullYear() + 1);
        document.cookie =
            SUBSCRIBED_COOKIE +
            "; path=/; max-age=" + (60 * 60 * 24 * 365) +
            "; expires=" + expires.toUTCString() +
            "; SameSite=Lax";
    }

    if (getCookie("app_cotacao_subscribed")) {
        return;
    }

    var DELAY_MS = 60 * 1000;

    setTimeout(function () {
        overlay.hidden = false;
    }, DELAY_MS);

    var closeButton = document.getElementById("subscribeClose");
    if (closeButton) {
        closeButton.addEventListener("click", function () {
            overlay.hidden = true;
        });
    }

    var form = document.getElementById("subscribeForm");
    var emailInput = document.getElementById("subscribeEmail");
    var submitButton = document.getElementById("subscribeSubmit");
    var messageSpan = document.getElementById("subscribeMsg");

    function showMessage(text, isError) {
        messageSpan.textContent = text;
        messageSpan.classList.toggle("is-error", !!isError);
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        submitButton.disabled = true;
        submitButton.textContent = "Enviando...";
        showMessage("", false);

        fetch("/api/subscribe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: emailInput.value })
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    return { ok: response.ok, data: data };
                });
            })
            .then(function (result) {
                if (result.ok) {
                    setSubscribedCookie();
                    emailInput.value = "";
                    overlay.hidden = true;
                } else if (result.data.error === "invalid_email") {
                    showMessage("Informe um e-mail válido.", true);
                } else {
                    showMessage("Não foi possível cadastrar agora. Tente novamente.", true);
                }
            })
            .catch(function () {
                showMessage("Falha de conexão. Tente novamente.", true);
            })
            .finally(function () {
                submitButton.disabled = false;
                submitButton.textContent = "Cadastrar";
            });
    });
})();
