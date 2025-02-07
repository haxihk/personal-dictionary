document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-switch");

    // بررسی تم ذخیره‌شده در Local Storage
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        document.body.className = savedTheme;
        themeToggle.checked = savedTheme === "dark-mode";
    }

    // تغییر تم با کلیک روی سوئیچ
    themeToggle.addEventListener("change", () => {
        if (themeToggle.checked) {
            document.body.className = "dark-mode";
            localStorage.setItem("theme", "dark-mode");
        } else {
            document.body.className = "light-mode";
            localStorage.setItem("theme", "light-mode");
        }
    });
});
