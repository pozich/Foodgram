document.addEventListener('DOMContentLoaded', () => {
    const dbSection = document.getElementById('db-section');
    if (dbSection && dbSection.style.display !== 'none') {
        loadSellers();
    }
});

async function manageSeller(action) {
    const btn = event.target;
    const targetInput = document.getElementById('target_id');
    const targetValue = targetInput.value.trim();

    if (!targetValue) {
        tg.showAlert("Введите ID или Username!");
        return;
    }

    btn.disabled = true;
    tg.MainButton.showProgress();

    try {
        const result = await apiRequest('/api/admin', {
            action: action,
            target: targetValue
        });

        if (result.status === 'success') {
            tg.HapticFeedback.notificationOccurred('success');
            targetInput.value = '';
            if (document.getElementById('db-section').style.display !== 'none') {
                await loadSellers();
            }
            tg.showScanQrPopup({ text: "Готово!" });
            setTimeout(() => tg.closeScanQrPopup(), 1000);
        } else {
            tg.showAlert("Ошибка: " + (result.message || "пользователь не найден"));
        }
    } finally {
        btn.disabled = false;
        tg.MainButton.hideProgress();
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
        loadSellers();
    } else {
        dbSection.style.display = 'none';
        settingsSection.style.display = 'block';
        btnDb.classList.remove('active');
        btnSettings.classList.add('active');
    }
}
