import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function App() {
  const navigate = useNavigate();
  const [ip, setIp] = useState("");
  const [cat, setCat] = useState("white");
  const [loading, setLoading] = useState(false);

  // Simple route check (since we are in strict mode and explicit routes weren't defined)
  const isReport = window.location.pathname.startsWith("/report/");
  const reportId = isReport ? window.location.pathname.split("/")[2] : null;

  const scan = async () => {
    if (!ip) {
      alert("Lütfen bir IP adresi girin.");
      return;
    }

    setLoading(true);
    try {
      const r = await fetch("/api/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip, category: cat })
      });

      if (!r.ok) {
        const err = await r.json();
        throw new Error(err.detail || "Sunucu hatası");
      }

      // FIX: Backend returns 'scan_id', not 'uid'
      const { scan_id } = await r.json();
      navigate(`/report/${scan_id}`);
    } catch (e) {
      console.error(e);
      alert("Hata: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  if (isReport) {
    return (
      <div className="container">
        <h1>Rapor Hazırlanıyor</h1>
        <p>Tarama başlatıldı/tamamlandı.</p>
        <p>ID: {reportId}</p>
        <a href={`/reports/${reportId}/`} target="_blank" rel="noreferrer">
          <button>Dosyaları Görüntüle</button>
        </a>
        <br /><br />
        <button onClick={() => navigate("/")} style={{ backgroundColor: '#64748b' }}>Yeni Tarama</button>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Pentest-OneClick</h1>
      <input value={ip} onChange={e => setIp(e.target.value)} placeholder="IP veya domain" />
      <select value={cat} onChange={e => setCat(e.target.value)}>
        <option value="white">White (Pasif)</option>
        <option value="gray">Gray (Aktif)</option>
        <option value="black">Black (Exploit)</option>
      </select>
      <button onClick={scan} disabled={loading}>
        {loading ? "Başlatılıyor..." : "Başlat"}
      </button>
    </div>
  );
}
