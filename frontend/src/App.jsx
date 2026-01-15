import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function App() {
  const navigate = useNavigate();
  const [ip, setIp] = useState("");
  const [cat, setCat] = useState("white");
  const [loading, setLoading] = useState(false);

  // Simple route check
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

      const contentType = r.headers.get("content-type");

      if (!r.ok) {
        let errMsg = "Sunucu hatası (" + r.status + ")";
        if (contentType && contentType.includes("application/json")) { // Handle JSON error
          try {
            const err = await r.json();
            errMsg = err.detail || errMsg;
          } catch (ignore) { }
        } else { // Handle HTML/Text error (e.g. Nginx 502)
          const text = await r.text();
          console.error("Non-JSON Error:", text);
          // Show first 100 chars of HTML to hint at the error
          errMsg += ": " + text.substring(0, 100).replace(/<[^>]*>?/gm, "") + "..."; // Strip tags
        }
        throw new Error(errMsg);
      }

      // Success check
      if (!contentType || !contentType.includes("application/json")) {
        const text = await r.text();
        console.error("Non-JSON Success Body:", text);
        throw new Error("Sunucu JSON döndürmedi (" + r.status + "). Beklenmeyen yanıt.");
      }

      const resData = await r.json();
      if (!resData.scan_id) {
        throw new Error("Sunucu scan_id döndürmedi.");
      }

      navigate(`/report/${resData.scan_id}`);
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
