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
            var original = this.textContent;
            this.textContent = "Atualizando...";
            setTimeout(function () {
                window.location.reload();
            }, 500);
        });
    }
})();
