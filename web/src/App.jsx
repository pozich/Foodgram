import { useEffect, useState } from 'react'
import './App.css'

const AdminDashboard = ({ data }) => (
  <div className="admin-panel" style={{ background: '#222', padding: '20px', borderRadius: '15px', marginTop: '20px' }}>
    <h2>🏢 Панель Владельца</h2>
    <div style={{ background: '#333', padding: '10px', borderRadius: '10px' }}>
      <p>Тариф: <b>{data.tier?.name || "SuperUser"}</b></p>
    </div>
    <h3>Мои пекарни:</h3>
    {data.bakeries?.length > 0 ? (
      data.bakeries.map(b => <div key={b.id}>🥐 {b.title}</div>)
    ) : (
      <p>У вас пока нет пекарен</p>
    )}
    <button style={{ background: '#28a745', color: 'white', marginTop: '10px' }}>+ Создать пекарню</button>
  </div>
);

function App() {
  const [user, setUser] = useState(null);
  const [adminData, setAdminData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const tg = window.Telegram.WebApp;
    tg.ready();
    
    if (tg.initDataUnsafe?.user) {
      const tgUser = tg.initDataUnsafe.user;
      setUser(tgUser);

      // СТУЧИМСЯ В БЭКЕНД
      fetch(`/api/owner/profile?tg_id=${tgUser.id}`)
        .then(res => {
          if (!res.ok) throw new Error("Not Admin");
          return res.json();
        })
        .then(data => setAdminData(data)) // Если API сказал "ОК", записываем данные
        .catch(() => setAdminData(null))   // Если 403, оставляем null
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  if (loading) return <div style={{color: 'white'}}>Загрузка...</div>;

  return (
    <div style={{ padding: '20px', color: 'white', textAlign: 'center' }}>
      <h1>🍞 Foodgram</h1>
      
      {adminData ? (
        <AdminDashboard data={adminData} />
      ) : (
        <div>
          {user && <p>Привет, <b>{user.first_name}</b>! (Клиент)</p>}
          <p>Тут скоро будет меню еды.</p>
        </div>
      )}

      <button onClick={() => window.Telegram.WebApp.close()} style={{ marginTop: '20px' }}>
        Закрыть
      </button>
    </div>
  );
}

export default App;
