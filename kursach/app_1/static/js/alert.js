document.addEventListener("DOMContentLoaded", function () {
        const errorAlert = document.getElementById("error-alert");
        if (errorAlert) {
            // Скрыть через 5 секунд
            setTimeout(() => {
                errorAlert.style.transition = "opacity 0.5s ease-out";
                errorAlert.style.opacity = "0";
                setTimeout(() => errorAlert.remove(), 500); // Полностью удалить из DOM
            }, 5000); // 5000 мс = 5 секунд
        }
    });