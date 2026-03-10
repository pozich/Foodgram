import React, { useState, useEffect } from 'react';

const OrderHistory = ({ tgId }) => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch(`/api/orders/me?tg_id=${tgId}`)
            .then(r => r.json())
            .then(setOrders)
            .finally(() => setLoading(false));
    }, [tgId]);

    if (loading) return <p className="loading">Загружаем ваши заказы...</p>;

    return (
        <div className="order-history">
            <h2 className="section-title">Мои заказы</h2>
            {orders.length === 0 ? (
                <p className="empty-text">Вы еще ничего не забронировали. Пора это исправить! 🥐</p>
            ) : (
                orders.map(o => (
                    <div key={o.id} className="glass order-card">
                        <div className="order-main">
                            <h3>{o.product.title}</h3>
                            <div className={`status status-${o.status}`}>
                                {o.status === 'pending' ? 'Ожидает получения' : o.status}
                            </div>
                        </div>
                        <div className="order-details">
                            <p>Количество: {o.quantity} шт.</p>
                            <p>Сумма: <b>{o.total_price} ₽</b></p>
                        </div>
                        <div className="pickup-box">
                            <span className="pickup-label">Код выдачи:</span>
                            <span className="pickup-code">{o.pickup_code}</span>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
};

export default OrderHistory;
