const tg = window.Telegram.WebApp;

tg.ready();
tg.expand();

document.documentElement.style.setProperty('--tg-bg-color', tg.backgroundColor);

function notify(message) {
    tg.showAlert(message);
}

async function apiRequest(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-Telegram-Init-Data': tg.initData 
        },
        body: JSON.stringify(data)
    });
    return await response.json();
}
