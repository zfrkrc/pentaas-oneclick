function App() {
  const [ip, setIp] = useState("");
  const [cat, setCat] = useState("white");
  const scan = async () => {
    const r = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ip, category: cat })
    });
    const { uid } = await r.json();
    navigate(`/report/${uid}`);
  };
  return (
    <div className="container">
      <h1>Pentest-OneClick</h1>
      <input value={ip} onChange={e => setIp(e.target.value)} placeholder="IP veya domain" />
      <select value={cat} onChange={e => setCat(e.target.value)}>
        <option value="white">White (Pasif)</option>
        <option value="gray">Gray (Aktif)</option>
        <option value="black">Black (Exploit)</option>
      </select>
      <button onClick={scan}>Başlat</button>
    </div>
  );
}
