import React, { useState } from 'react';

const ProductManager = ({ tgId, bakery, onBack }) => {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        old_price: 0,
        price: 0,
        quantity: 1,
        available_until: new Date(Date.now() + 86400000).toISOString().slice(0, 16)
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        fetch(`/api/products/?tg_id=${tgId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...formData, bakery_id: bakery.id })
        })
            .then(r => r.json())
            .then(() => {
                alert('Товар добавлен!');
                onBack();
            });
    };

    return (
        <div className="section">
            <button className="btn-back" onClick={onBack}>← Назад к пекарням</button>
            <h2 className="section-title">Добавить в {bakery.title}</h2>

            <form className="glass add-form" onSubmit={handleSubmit}>
                <input
                    placeholder="Название блюда"
                    value={formData.title}
                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                    required
                />
                <textarea
                    placeholder="Описание (состав, вес)"
                    value={formData.description}
                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                />
                <div className="form-row">
                    <input
                        type="number"
                        placeholder="Старая цена"
                        value={formData.old_price}
                        onChange={e => setFormData({ ...formData, old_price: parseInt(e.target.value) })}
                    />
                    <input
                        type="number"
                        placeholder="Цена сейчас"
                        value={formData.price}
                        onChange={e => setFormData({ ...formData, price: parseInt(e.target.value) })}
                        required
                    />
                </div>
                <div className="form-row">
                    <input
                        type="number"
                        placeholder="Кол-во"
                        value={formData.quantity}
                        onChange={e => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
                    />
                    <input
                        type="datetime-local"
                        value={formData.available_until}
                        onChange={e => setFormData({ ...formData, available_until: e.target.value })}
                    />
                </div>
                <button type="submit" className="btn-save">Выставить на витрину</button>
            </form>
        </div>
    );
};

export default ProductManager;
