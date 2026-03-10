import React, { useState, useEffect } from 'react';

const ProductFeed = ({ tgId }) => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/products/feed')
            .then(r => r.json())
            .then(setProducts)
            .finally(() => setLoading(false));
    }, []);

    const handleBook = (productId) => {
        if (!tgId) return alert('Ошибка: зайдите через бота');

        fetch(`/api/orders/?tg_id=${tgId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        })
            .then(r => {
                if (!r.ok) return r.json().then(e => { throw e });
                return r.json();
            })
            .then(() => {
                alert('Успешно забронировано! Проверьте вкладку "Заказы"');
                fetch('/api/products/feed').then(r => r.json()).then(setProducts);
            })
            .catch(err => alert(err.detail || 'Ошибка бронирования'));
    };

    if (loading) return <p className="loading">Ищем вкусняшки...</p>;

    return (
        <div className="product-feed">
            {products.length === 0 ? (
                <p className="empty-text">Пока ничего не выложили. Заходи позже! 🥐</p>
            ) : (
                products.map(p => (
                    <div key={p.id} className="glass product-card">
                        <div className="product-badges">
                            <span className="badge-discount">
                                -{Math.round((1 - p.price / p.old_price) * 100)}%
                            </span>
                        </div>
                        <div className="product-info">
                            <h3>{p.title} <span className="badge-qty">(осталось: {p.quantity})</span></h3>
                            <p className="product-bakery">📍 {p.bakery.title}</p>
                            <p className="product-desc">{p.description}</p>
                            <div className="product-price-row">
                                <span className="price-old">{p.old_price} ₽</span>
                                <span className="price-current">{p.price} ₽</span>
                            </div>
                            <button className="btn-buy" onClick={() => handleBook(p.id)}>Забронировать</button>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
};

export default ProductFeed;
