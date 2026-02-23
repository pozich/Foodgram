// Сообщаем Telegram, что приложение готово
window.Telegram.WebApp.ready();

// Расширяем Mini App на всю высоту
window.Telegram.WebApp.expand();

// По желанию: подстраиваем цвета под тему пользователя
/*
if (window.Telegram.WebApp.themeParams) {
    document.body.style.backgroundColor = window.Telegram.WebApp.themeParams.bg_color || '#2c3e50';
    document.body.style.color = window.Telegram.WebApp.themeParams.text_color || '#ecf0f1';
}
*/
