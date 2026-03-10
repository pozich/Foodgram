import { useEffect, useState } from 'react'
import './App.css'
import BakeryManager from './components/BakeryManager'
import ProductManager from './components/ProductManager'
import ProductFeed from './components/ProductFeed'
import OrderHistory from './components/OrderHistory'

const SellerManagement = ({ adminTgId }) => {
  const [sellers, setSellers] = useState([]);
  const [newSeller, setNewSeller] = useState('');
  const [search, setSearch] = useState('');

  const fetchSellers = () => {
    fetch(`/api/admin/sellers?tg_id=${adminTgId}`)
      .then(r => r.json())
      .then(setSellers);
  };

  useEffect(() => {
    fetchSellers();
  }, [adminTgId]);

  const addSeller = () => {
    fetch(`/api/admin/sellers?tg_id=${adminTgId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: newSeller })
    }).then(() => {
      setNewSeller('');
      fetchSellers();
    });
  };

  const filteredSellers = sellers.filter(s =>
    s.user.username.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="view-container">
      <h3>Управление продавцами</h3>
      <div className="search-container">
        <span className="search-icon">🔍</span>
        <input
          className="search-input"
          placeholder="Поиск по username"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <div className="seller-list">
        {filteredSellers.map(s => (
          <div key={s.user.id} className="glass seller-card">
            <div className="seller-info">
              <p className="seller-name">{s.user.username}</p>
              <p className="seller-username">@{s.user.username}</p>
            </div>
            <div className="seller-badge">{s.tier?.name || 'Seller'}</div>
          </div>
        ))}
      </div>
      <div className="glass add-box" style={{ marginTop: '20px', padding: '16px' }}>
        <input
          placeholder="New seller username"
          value={newSeller}
          onChange={(e) => setNewSeller(e.target.value)}
        />
        <button className="btn-buy" onClick={addSeller} style={{ marginTop: '10px' }}>Добавить продавца</button>
      </div>
    </div>
  );
};

function App() {
  const [user, setUser] = useState(null);
  const [isOwner, setIsOwner] = useState(false);
  const [isSuperuser, setIsSuperuser] = useState(false);
  const [activeTab, setActiveTab] = useState('feed');
  const [isManagementMode, setIsManagementMode] = useState(false);
  const [selectedBakery, setSelectedBakery] = useState(null);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.expand();
      const tgUser = tg.initDataUnsafe?.user;
      if (tgUser) {
        setUser(tgUser);
        fetch(`/api/owner/profile?tg_id=${tgUser.id}`)
          .then(r => r.json())
          .then(data => {
            if (data.is_superuser) setIsSuperuser(true);
            if (data.is_owner) setIsOwner(true);
          });
      }
    }
  }, []);

  const toggleMode = () => {
    setIsManagementMode(!isManagementMode);
    // Reset secondary states when toggling
    setSelectedBakery(null);
  };

  const renderContent = () => {
    if (isManagementMode) {
      if (isSuperuser) return <SellerManagement adminTgId={user?.id} />;
      if (isOwner) {
        if (selectedBakery) {
          return <ProductManager tgId={user?.id} bakery={selectedBakery} onBack={() => setSelectedBakery(null)} />;
        }
        return <BakeryManager tgId={user?.id} onSelectBakery={setSelectedBakery} />;
      }
    }

    if (activeTab === 'feed') return <ProductFeed tgId={user?.id} />;
    if (activeTab === 'orders') return <OrderHistory tgId={user?.id} />;

    return <ProductFeed tgId={user?.id} />;
  };

  return (
    <div className="app">
      {renderContent()}

      <div className="bottom-nav">
        <div
          className={`nav-item ${activeTab === 'feed' && !isManagementMode ? 'active' : ''}`}
          onClick={() => { setActiveTab('feed'); setIsManagementMode(false); }}
        >
          <span className="nav-icon">🛒</span>
          <span>Магазин</span>
        </div>

        <div
          className={`nav-item ${activeTab === 'orders' && !isManagementMode ? 'active' : ''}`}
          onClick={() => { setActiveTab('orders'); setIsManagementMode(false); }}
        >
          <span className="nav-icon">📦</span>
          <span>Заказы</span>
        </div>

        {(isOwner || isSuperuser) && (
          <div
            className={`nav-item ${isManagementMode ? 'active' : ''}`}
            onClick={toggleMode}
          >
            <div className={`mode-toggle-btn ${isSuperuser ? 'admin' : ''}`}>
              <span className="icon">⚙️</span>
              <span>{isSuperuser ? 'Админ' : 'Продавец'}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
