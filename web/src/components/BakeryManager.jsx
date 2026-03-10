import React, { useState, useEffect } from 'react';

const BakeryManager = ({ tgId, onSelectBakery }) => {
    const [bakeries, setBakeries] = useState([]);
    const [workers, setWorkers] = useState([]);
    const [activeSubTab, setActiveSubTab] = useState('bakeries'); // 'bakeries' or 'staff'
    const [showAdd, setShowAdd] = useState(false);
    const [editingBakery, setEditingBakery] = useState(null);
    const [newWorkerUsername, setNewWorkerUsername] = useState('');

    const [formData, setFormData] = useState({ title: '', description: '', latitude: 0, longitude: 0 });

    const fetchBakeries = () => {
        fetch(`/api/bakeries/?tg_id=${tgId}`)
            .then(r => r.json())
            .then(setBakeries);
    };

    const fetchWorkers = () => {
        // We'll need an endpoint for this, assuming it exists based on models or mocking it
        fetch(`/api/owner/staff?tg_id=${tgId}`)
            .then(r => r.json())
            .then(setWorkers)
            .catch(() => setWorkers([])); // Fallback if endpoint not ready
    };

    useEffect(() => {
        fetchBakeries();
        fetchWorkers();
    }, []);

    const handleSave = (e) => {
        e.preventDefault();
        const method = editingBakery ? 'PUT' : 'POST';
        const url = editingBakery
            ? `/api/bakeries/${editingBakery.id}?tg_id=${tgId}`
            : `/api/bakeries/?tg_id=${tgId}`;

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
            .then(() => {
                setShowAdd(false);
                setEditingBakery(null);
                setFormData({ title: '', description: '', latitude: 0, longitude: 0 });
                fetchBakeries();
            });
    };

    const handleAddWorker = () => {
        if (!newWorkerUsername) return;
        fetch(`/api/owner/staff/add?owner_tg_id=${tgId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: newWorkerUsername })
        }).then(() => {
            setNewWorkerUsername('');
            fetchWorkers();
        });
    };

    const handleGetLocation = () => {
        if (!navigator.geolocation) {
            alert("Ваш браузер не поддерживает GPS");
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                setFormData({
                    ...formData,
                    latitude: pos.coords.latitude,
                    longitude: pos.coords.longitude
                });
            },
            (err) => {
                alert("Не удалось получить местоположение. Проверьте разрешения.");
            },
            { enableHighAccuracy: true }
        );
    };

    return (
        <div className="view-container">
            <div className="sub-tabs glass" style={{ display: 'flex', marginBottom: '16px', padding: '4px', borderRadius: '12px' }}>
                <div
                    className={`nav-item ${activeSubTab === 'bakeries' ? 'active' : ''}`}
                    style={{ padding: '8px', cursor: 'pointer', borderRadius: '10px', flex: 1, textAlign: 'center' }}
                    onClick={() => setActiveSubTab('bakeries')}
                >
                    Заведения
                </div>
                <div
                    className={`nav-item ${activeSubTab === 'staff' ? 'active' : ''}`}
                    style={{ padding: '8px', cursor: 'pointer', borderRadius: '10px', flex: 1, textAlign: 'center' }}
                    onClick={() => setActiveSubTab('staff')}
                >
                    Работники
                </div>
            </div>

            {activeSubTab === 'bakeries' ? (
                <div className="bakeries-view">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <h3 style={{ margin: 0 }}>Ваши пекарни</h3>
                        <button className="mode-toggle-btn" onClick={() => { setShowAdd(true); setEditingBakery(null); setFormData({ title: '', description: '', latitude: 0, longitude: 0 }); }}>+ Добавить</button>
                    </div>

                    {(showAdd || editingBakery) && (
                        <form className="glass add-form" onSubmit={handleSave} style={{ padding: '16px', marginBottom: '20px' }}>
                            <h4 style={{ marginBottom: '12px' }}>{editingBakery ? 'Редактировать' : 'Новое заведение'}</h4>
                            <input
                                placeholder="Название"
                                value={formData.title}
                                onChange={e => setFormData({ ...formData, title: e.target.value })}
                                required
                                style={{ marginBottom: '10px' }}
                            />
                            <textarea
                                placeholder="Описание"
                                value={formData.description}
                                onChange={e => setFormData({ ...formData, description: e.target.value })}
                                style={{ marginBottom: '10px', height: '80px' }}
                            />

                            <div className="location-picker" style={{ marginBottom: '15px' }}>
                                <button
                                    type="button"
                                    className="btn-buy"
                                    style={{ background: '#34c759', margin: '0 0 10px 0', fontSize: '0.9rem' }}
                                    onClick={handleGetLocation}
                                >
                                    📍 Указать моё местоположение
                                </button>
                                <div style={{ display: 'flex', gap: '8px', fontSize: '0.8rem', opacity: 0.7 }}>
                                    <span>Lat: {formData.latitude.toFixed(4)}</span>
                                    <span>Lon: {formData.longitude.toFixed(4)}</span>
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '8px' }}>
                                <button type="submit" className="btn-buy">Сохранить</button>
                                <button type="button" className="btn-buy" style={{ background: '#ff3b30' }} onClick={() => { setShowAdd(false); setEditingBakery(null); }}>Отмена</button>
                            </div>
                        </form>
                    )}

                    <div className="bakery-list">
                        {bakeries.map(b => (
                            <div key={b.id} className="glass bakery-card" style={{ padding: '12px', marginBottom: '8px', position: 'relative' }}>
                                <div onClick={() => onSelectBakery(b)}>
                                    <p className="seller-name">{b.title}</p>
                                    <p className="seller-username">{b.description}</p>
                                </div>
                                <button
                                    style={{ position: 'absolute', top: '12px', right: '12px', background: 'none', color: "var(--tg-theme-link-color, '#2481cc')" }}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setEditingBakery(b);
                                        setFormData({ title: b.title, description: b.description, latitude: b.latitude, longitude: b.longitude });
                                    }}
                                >
                                    Изм.
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="staff-view">
                    <h3>Работники</h3>
                    <div className="glass add-box" style={{ padding: '16px', marginBottom: '16px' }}>
                        <input
                            placeholder="Username работника"
                            value={newWorkerUsername}
                            onChange={(e) => setNewWorkerUsername(e.target.value)}
                        />
                        <button className="btn-buy" onClick={handleAddWorker} style={{ marginTop: '10px' }}>Добавить работника</button>
                    </div>
                    <div className="seller-list">
                        {workers.map(w => (
                            <div key={w.id} className="glass seller-card" style={{ padding: '12px', marginBottom: '8px' }}>
                                <div>
                                    <p className="seller-name">{w.user.username}</p>
                                    <p className="seller-username">@{w.user.username}</p>
                                </div>
                                <div className="seller-badge">Staff</div>
                            </div>
                        ))}
                        {workers.length === 0 && <p style={{ textAlign: 'center', opacity: 0.5 }}>Работников пока нет</p>}
                    </div>
                </div>
            )
            }
        </div >
    );
};

export default BakeryManager;
