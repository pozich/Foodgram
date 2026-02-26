const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Настройка темы
document.documentElement.style.setProperty('--tg-bg-color', tg.backgroundColor);

// Загружаем данные сразу при старте, если вдруг открыта вкладка БД
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('db-section').style.display !== 'none') {
        loadSellers();
    }
});

async function manageSeller(action) {
    const targetInput = document.getElementById('target_id');
    const targetValue = targetInput.value.trim();

    if (!targetValue) {
        tg.showAlert("Введите ID или Username!");
        return;
    }
    
    const payload = {
        scope: 'admin',
        action: action,
        target: targetValue,
    };

    tg.HapticFeedback.impactOccurred('medium');

    try {
        const response = await fetch('/api/admin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        
        if (result.status === 'success') {
            tg.showPopup({
                title: 'Успешно',
                message: `Операция выполнена для: ${targetValue}`,
                buttons: [{type: 'ok'}]
            });
            targetInput.value = '';
            // Если мы в разделе БД, обновляем список после добавления
            if (document.getElementById('db-section').style.display !== 'none') {
                loadSellers();
            }
        } else {
            tg.showAlert("Ошибка: " + (result.message || "что-то пошло не так"));
        }
    } catch (e) {
        tg.showAlert("Сервер не отвечает. Проверь туннель!");
    }
}

async function loadSellers() {
    try {
        const response = await fetch('/api/admin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                scope: 'admin', 
                action: 'get_sellers' 
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            const container = document.getElementById('sellers-list');
            if (!container) return;

            if (!result.sellers || result.sellers.length === 0) {
                container.innerHTML = '<tr><td colspan="2" style="text-align:center; padding:20px; color:var(--text-hint);">Продавцов пока нет</td></tr>';
                return;
            }

            container.innerHTML = result.sellers.map(s => {
                const isPending = s.tg_id === null || s.tg_id === 0;
                const displayName = s.username ? `@${s.username}` : `ID: ${s.tg_id}`;
                const link = s.username ? `https://t.me/${s.username}` : `#`;
                
                return `
                <tr>
                    <td>
                        <a href="${link}" class="seller-link ${isPending ? 'pending' : ''}" target="_blank">
                            ${displayName} ${isPending ? '<span style="font-size:10px; opacity:0.6;">(ожидает)</span>' : ''}
                        </a>
                    </td>
                    <td style="text-align: right; color: var(--text-hint);">${s.bakery_name || '-'}</td>
                </tr>`;
            }).join('');
        }
    } catch (e) {
        console.error("Ошибка API:", e);
        tg.showAlert("Не удалось загрузить список");
    }
}

function showTab(tabId) {
    tg.HapticFeedback.selectionChanged();
    
    const dbSection = document.getElementById('db-section');
    const settingsSection = document.getElementById('settings-section');
    const btnDb = document.getElementById('btn-db');
    const btnSettings = document.getElementById('btn-settings');

    if (tabId === 'db') {
        dbSection.style.display = 'block';
        settingsSection.style.display = 'none';
        btnDb.classList.add('active');
        btnSettings.classList.remove('active');
        loadSellers(); // Теперь загрузка вызывается правильно
    } else {
        dbSection.style.display = 'none';
        settingsSection.style.display = 'block';
        btnDb.classList.remove('active');
        btnSettings.classList.add('active');
    }
}
