import React, { useState, useEffect, useRef } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import History from './components/History'
import { authClient } from './lib/auth'

function App() {
  const [target, setTarget] = useState('');
  const [mode, setMode] = useState('black');
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [scanResult, setScanResult] = useState(null);
  const [toolProgress, setToolProgress] = useState({ completed: [], pending: [] });
  const [activeTab, setActiveTab] = useState('new');
  const [turnstileToken, setTurnstileToken] = useState('');
  const turnstileRef = useRef(null);
  const turnstileWidgetId = useRef(null);
  // Auth session
  const { data: session } = authClient.useSession();

  // Günlük kota bilgisi
  const [quota, setQuota] = useState({ used: 0, limit: 2, remaining: 2 });

  // Session değiştiğinde kotayı sorgula
  useEffect(() => {
    if (session?.user?.id) {
      fetch(`/api/scan-quota?user_id=${session.user.id}`)
        .then(r => r.json())
        .then(data => setQuota(data))
        .catch(() => { });
    }
  }, [session]);

  // Turnstile widget'ını render et
  useEffect(() => {
    const renderTurnstile = () => {
      if (window.turnstile && turnstileRef.current && !turnstileWidgetId.current) {
        turnstileWidgetId.current = window.turnstile.render(turnstileRef.current, {
          sitekey: '0x4AAAAAACgfib7XhvjvFxJX',
          theme: 'dark',
          callback: (token) => setTurnstileToken(token),
          'expired-callback': () => setTurnstileToken(''),
        });
      }
    };

    // Turnstile script yüklenmişse hemen render et
    if (window.turnstile) {
      renderTurnstile();
    } else {
      // Script yüklenmemişse bekle
      const interval = setInterval(() => {
        if (window.turnstile) {
          clearInterval(interval);
          renderTurnstile();
        }
      }, 100);
      return () => clearInterval(interval);
    }
  }, [activeTab]);

  const handleStartScan = async () => {
    // Üyelik kontrolü
    if (!session?.user) {
      alert('Tarama başlatmak için giriş yapmanız gerekiyor.');
      return;
    }
    // Kota kontrolü
    if (quota.remaining <= 0) {
      alert('Günlük tarama limitinize ulaştınız. Yarın tekrar deneyin.');
      return;
    }
    // Turnstile token kontrolü
    if (!turnstileToken) {
      alert('Lütfen "Ben robot değilim" doğrulamasını tamamlayın.');
      return;
    }

    setIsScanning(true);
    setProgress(10);
    setScanResult(null);
    try {
      const response = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ip: target,
          category: mode,
          turnstileToken,
          userId: session.user.id,
          userName: session.user.name || session.user.email,
          userEmail: session.user.email
        })
      });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Scan starting failed');
      }
      const { scan_id } = await response.json();

      // Kotayı güncelle (lokal)
      setQuota(prev => ({ ...prev, used: prev.used + 1, remaining: Math.max(0, prev.remaining - 1) }));

      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`/api/scan/${scan_id}`);
          if (!statusRes.ok) return;
          const statusData = await statusRes.json();
          if (statusData.services) {
            const completed = [], pending = [];
            Object.entries(statusData.services).forEach(([name, info]) => {
              if (info.completed) completed.push(name); else pending.push(name);
            });
            setToolProgress({ completed, pending });
            const total = completed.length + pending.length;
            if (total > 0) setProgress(Math.floor((completed.length / total) * 100));
          }
          fetchResults(scan_id, false);
          if (statusData.status === 'completed') {
            clearInterval(pollInterval);
            fetchResults(scan_id, true);
          }
        } catch (pollErr) { console.error("Polling error:", pollErr); }
      }, 2000);
    } catch (err) {
      console.error("Scan Error:", err);
      alert("Hata: " + err.message);
      setIsScanning(false);
    }
  };

  const fetchResults = async (scanId, isFinal = false) => {
    try {
      const res = await fetch(`/api/scan/${scanId}/results`);
      if (!res.ok) throw new Error('Could not fetch results');
      const data = await res.json();
      if (data.progress) setToolProgress(data.progress);
      const counts = { Critical: 0, High: 0, Medium: 0, Low: 0, Info: 0 };
      data.findings.forEach(f => {
        if (counts[f.severity] !== undefined) counts[f.severity]++;
        else if (f.severity === 'Info' || f.severity === 'Informational') counts.Info++;
      });
      setScanResult({
        ip: target, mode,
        vulnerabilities: [
          { severity: 'Critical', count: counts.Critical },
          { severity: 'High', count: counts.High },
          { severity: 'Medium', count: counts.Medium },
          { severity: 'Low', count: counts.Low },
          { severity: 'Info', count: counts.Info }
        ],
        findings: data.findings,
        time: new Date().toLocaleString()
      });
      if (isFinal) { setProgress(100); setIsScanning(false); }
    } catch (err) {
      console.error("Results Fetch Error:", err);
      if (isFinal) { alert("Sonuçlar alınırken hata oluştu."); setIsScanning(false); }
    }
  };

  const downloadCSV = () => {
    if (!scanResult) { alert("Hata: Tarama sonucu bulunamadı."); return; }
    try {
      const totalVulns = scanResult.vulnerabilities.reduce((sum, v) => sum + v.count, 0);
      let csvRows = [
        "PENTAAS ONECLICK - SCAN REPORT", "",
        "SCAN INFO", `Target,${scanResult.ip}`, `Mode,${scanResult.mode}`,
        `Time,${scanResult.time}`, `Total Findings,${totalVulns}`,
        "", "SUMMARY", "Severity,Count"
      ];
      scanResult.vulnerabilities.forEach(v => csvRows.push(`${v.severity},${v.count}`));
      csvRows.push("", "DETAILED FINDINGS", "ID,Title,Severity,Description");
      scanResult.findings.forEach(f => {
        const descToken = f.description.replace(/(\r\n|\n|\r)/gm, " ").replace(/,/g, ';');
        csvRows.push(`${f.id},${f.title},${f.severity},${descToken}`);
      });
      const blob = new Blob([csvRows.join("\n")], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `pentaas_${scanResult.ip.replace(/[^a-z0-9]/gi, '_')}.csv`;
      document.body.appendChild(link);
      link.click();
      setTimeout(() => { document.body.removeChild(link); window.URL.revokeObjectURL(url); }, 500);
    } catch (err) { alert("Hata oluştu: " + err.message); }
  };

  const sevColor = (s) => ({ Critical: '#ff2d55', High: '#ff6b00', Medium: '#f5c518', Low: '#00c9a7', Info: '#6c757d' }[s] || '#6c757d');
  const sevBg = (s) => ({ Critical: 'rgba(255,45,85,0.1)', High: 'rgba(255,107,0,0.1)', Medium: 'rgba(245,197,24,0.1)', Low: 'rgba(0,201,167,0.1)', Info: 'rgba(108,117,125,0.1)' }[s] || 'rgba(108,117,125,0.1)');
  const tools = ['Nmap', 'Nikto', 'OWASP ZAP', 'Nuclei', 'Dirsearch', 'TestSSL', 'Waf00f', 'Arjun', 'Dalfox', 'DNSRecon'];

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
        :root{--bg:#090b10;--panel:#0d1117;--card:#111827;--border:rgba(0,212,170,0.15);--border-hi:rgba(0,212,170,0.4);--accent:#00d4aa;--accent-g:rgba(0,212,170,0.12);--t1:#e2e8f0;--t2:#94a3b8;--t3:#475569;--mono:'JetBrains Mono',monospace;}
        .sh{background:var(--bg);min-height:calc(100vh - 80px);padding:3rem 0 4rem;position:relative;overflow:hidden;font-family:var(--mono);}
        .sh::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 60% 40% at 70% 10%,rgba(0,212,170,.06) 0%,transparent 70%),radial-gradient(ellipse 50% 50% at 10% 80%,rgba(0,122,255,.04) 0%,transparent 60%);pointer-events:none;}
        .grid-bg{position:absolute;inset:0;background-image:linear-gradient(rgba(0,212,170,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,170,.03) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;}
        .lbl{font-size:.7rem;letter-spacing:.2em;color:var(--accent);text-transform:uppercase;display:inline-flex;align-items:center;gap:.5rem;margin-bottom:1rem;}
        .lbl::before{content:'';width:6px;height:6px;background:var(--accent);border-radius:50%;animation:pd 2s infinite;}
        @keyframes pd{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.8)}}
        h1.ht{font-size:clamp(1.8rem,4vw,3rem);font-weight:700;color:var(--t1);line-height:1.15;margin-bottom:.5rem;letter-spacing:-.02em;}
        h1.ht .acc{color:var(--accent);}
        .sub{color:var(--t2);font-size:1rem;margin-bottom:1.5rem;max-width:600px;}
        .pills{display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:2.5rem;}
        .pill{font-size:.7rem;padding:.25rem .65rem;background:rgba(0,212,170,.07);border:1px solid rgba(0,212,170,.2);border-radius:4px;color:rgba(0,212,170,.7);letter-spacing:.05em;}
        .tabs{display:flex;border:1px solid var(--border);border-radius:8px;overflow:hidden;width:fit-content;margin-bottom:2rem;}
        .tab{padding:.6rem 1.5rem;background:transparent;border:none;color:var(--t3);font-family:var(--mono);font-size:.8rem;letter-spacing:.05em;cursor:pointer;transition:all .2s;}
        .tab.on{background:var(--accent);color:#000;font-weight:700;}
        .tab:not(.on):hover{color:var(--accent);background:var(--accent-g);}
        .panel{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;}
        .ph{padding:1rem 1.5rem;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:.5rem;}
        .pd{width:8px;height:8px;border-radius:50%;}
        .pt{font-size:.75rem;color:var(--t3);letter-spacing:.1em;text-transform:uppercase;margin-left:.25rem;}
        .pb{padding:2rem;}
        .fl{font-size:.7rem;color:var(--t3);text-transform:uppercase;letter-spacing:.15em;display:block;margin-bottom:.6rem;}
        .inp{width:100%;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:.85rem 1rem;color:var(--t1);font-family:var(--mono);font-size:.95rem;outline:none;transition:border-color .2s,box-shadow .2s;}
        .inp::placeholder{color:var(--t3);}
        .inp:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,212,170,.12);}
        .inp:disabled{opacity:.5;cursor:not-allowed;}
        .mgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;}
        @media(max-width:576px){.mgrid{grid-template-columns:1fr}.sgrid{grid-template-columns:repeat(2,1fr)!important;}}
        .mc{padding:1.2rem;border:1px solid var(--border);border-radius:8px;cursor:pointer;transition:all .2s;background:var(--panel);text-align:center;}
        .mc:hover:not(.dis){border-color:var(--border-hi);background:var(--accent-g);}
        .mc.on{border-color:var(--accent);background:rgba(0,212,170,.08);}
        .mc.dis{opacity:.5;cursor:not-allowed;}
        .mi{font-size:1.5rem;margin-bottom:.5rem;display:block;}
        .mn{font-size:.85rem;font-weight:600;color:var(--t1);display:block;margin-bottom:.2rem;}
        .md{font-size:.72rem;color:var(--t3);display:block;}
        .mc.on .mn{color:var(--accent);}
        .btn-s{width:100%;padding:1rem;background:var(--accent);color:#000;border:none;border-radius:8px;font-family:var(--mono);font-size:.95rem;font-weight:700;letter-spacing:.08em;cursor:pointer;transition:all .2s;display:flex;align-items:center;justify-content:center;gap:.5rem;}
        .btn-s:hover:not(:disabled){background:#00f0c0;transform:translateY(-1px);box-shadow:0 8px 24px rgba(0,212,170,.3);}
        .btn-s:disabled{opacity:.7;cursor:not-allowed;transform:none;}
        .psec{margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border);}
        .ph2{display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem;}
        .plbl{font-size:.75rem;color:var(--t2);}
        .ppct{font-size:.75rem;color:var(--accent);font-weight:700;}
        .pwrap{height:4px;background:var(--panel);border-radius:2px;overflow:hidden;margin-bottom:1.2rem;}
        .pfill{height:100%;background:linear-gradient(90deg,var(--accent),#00f0c0);border-radius:2px;transition:width .4s ease;position:relative;overflow:hidden;}
        .pfill::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.3),transparent);animation:sh 1.5s infinite;}
        @keyframes sh{0%{transform:translateX(-100%)}100%{transform:translateX(200%)}}
        .ts{display:flex;flex-wrap:wrap;gap:.4rem;}
        .tb{font-size:.68rem;padding:.3rem .6rem;border-radius:4px;display:flex;align-items:center;gap:.3rem;border:1px solid;}
        .tb.d{color:var(--accent);border-color:rgba(0,212,170,.3);background:rgba(0,212,170,.05);}
        .tb.p{color:var(--t3);border-color:var(--border);background:transparent;}
        .sp{width:8px;height:8px;border:1px solid var(--t3);border-top-color:var(--accent);border-radius:50%;animation:sp 0.8s linear infinite;}
        @keyframes sp{to{transform:rotate(360deg)}}
        .rs{margin-top:2rem;border-top:1px solid var(--border);padding-top:2rem;}
        .rh{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;flex-wrap:wrap;gap:.5rem;}
        .rt{font-size:1.1rem;font-weight:700;color:var(--t1);margin:0;}
        .rm{font-size:.7rem;color:var(--t3);background:var(--panel);padding:.3rem .75rem;border-radius:4px;border:1px solid var(--border);}
        .sgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:.5rem;margin-bottom:2rem;}
        .sc{padding:1rem .5rem;border-radius:8px;text-align:center;border:1px solid;transition:transform .15s;}
        .sc:hover{transform:translateY(-2px);}
        .sl{font-size:.65rem;display:block;margin-bottom:.4rem;text-transform:uppercase;letter-spacing:.08em;}
        .sn{font-size:1.8rem;font-weight:700;display:block;line-height:1;}
        table.ft{width:100%;border-collapse:separate;border-spacing:0 4px;}
        table.ft thead th{font-size:.68rem;text-transform:uppercase;letter-spacing:.12em;color:var(--t3);padding:.5rem 1rem;border-bottom:1px solid var(--border);font-weight:500;}
        table.ft tbody tr{background:var(--panel);transition:background .15s;}
        table.ft tbody tr:hover{background:#161f2e;}
        table.ft tbody td{padding:.75rem 1rem;font-size:.82rem;color:var(--t2);vertical-align:top;}
        table.ft tbody td:first-child{border-radius:6px 0 0 6px;}
        table.ft tbody td:last-child{border-radius:0 6px 6px 0;}
        .sb{font-size:.65rem;padding:.2rem .5rem;border-radius:3px;text-transform:uppercase;letter-spacing:.05em;font-weight:600;}
        .ftt{font-weight:600;color:var(--t1);}
        .ftd{font-size:.75rem;color:var(--t3);line-height:1.5;}
        .ra{display:flex;justify-content:flex-end;gap:.75rem;margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border);flex-wrap:wrap;}
        .ba{padding:.6rem 1.2rem;border-radius:6px;font-family:var(--mono);font-size:.78rem;font-weight:600;cursor:pointer;transition:all .2s;display:flex;align-items:center;gap:.4rem;}
        .bo{background:transparent;border:1px solid var(--border);color:var(--t2);}
        .bo:hover{border-color:var(--border-hi);color:var(--t1);}
        .bp{background:var(--accent);border:none;color:#000;}
        .bp:hover{background:#00f0c0;box-shadow:0 4px 16px rgba(0,212,170,.25);}
      `}</style>

      <Navbar />

      <section className="sh">
        <div className="grid-bg"></div>
        <div className="container" style={{ position: 'relative', zIndex: 2 }}>
          <div className="row justify-content-center">
            <div className="col-12 col-md-10">

              <div className="mb-4">
                <div className="lbl">Pentaas One-Click · Security Scanner</div>
                <h1 className="ht">Hedef Tara,<br /><span className="acc">Zaafiyeti Bul.</span></h1>
                <p className="sub">Sistemlerinizi tek tıkla 10 farklı güvenlik aracıyla kapsamlı biçimde analiz edin.</p>
                <div className="pills">{tools.map(t => <span key={t} className="pill">{t}</span>)}</div>
              </div>

              <div className="tabs">
                <button className={`tab ${activeTab === 'new' ? 'on' : ''}`} onClick={() => setActiveTab('new')}>$ new_scan</button>
                <button className={`tab ${activeTab === 'history' ? 'on' : ''}`} onClick={() => setActiveTab('history')}>$ history</button>
              </div>

              {activeTab === 'new' ? (
                <div className="panel">
                  <div className="ph">
                    <div className="pd" style={{ background: '#ff5f56' }}></div>
                    <div className="pd" style={{ background: '#ffbd2e' }}></div>
                    <div className="pd" style={{ background: '#27c93f' }}></div>
                    <span className="pt">scan_config.sh</span>
                  </div>
                  <div className="pb">
                    <div className="mb-4">
                      <label className="fl">// Hedef IP / Hostname</label>
                      <input type="text" className="inp" placeholder="192.168.1.1 veya example.com" value={target} onChange={(e) => setTarget(e.target.value)} disabled={isScanning} />
                    </div>

                    <div className="mb-4">
                      <label className="fl">// Tarama Modu</label>
                      <div className="mgrid">
                        {[['white', '⬜', 'White Box', 'Tam Erişim / Auth Tarama'], ['gray', '🔲', 'Gray Box', 'Kısmi Erişim'], ['black', '⬛', 'Black Box', 'Erişimsiz / Harici']].map(([m, icon, name, desc]) => (
                          <div key={m} className={`mc ${mode === m ? 'on' : ''} ${isScanning ? 'dis' : ''}`} onClick={() => !isScanning && setMode(m)}>
                            <span className="mi">{icon}</span>
                            <span className="mn">{name}</span>
                            <span className="md">{desc}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* ── Auth & Kota Bilgi Paneli ── */}
                    {!session?.user ? (
                      <div className="mb-4" style={{
                        background: 'rgba(255,107,0,0.08)',
                        border: '1px solid rgba(255,107,0,0.3)',
                        borderRadius: '8px',
                        padding: '1.2rem 1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem'
                      }}>
                        <span style={{ fontSize: '1.5rem' }}>🔒</span>
                        <div>
                          <div style={{ color: '#ff6b00', fontWeight: 700, fontSize: '.9rem', marginBottom: '.2rem' }}>
                            Giriş Gerekli
                          </div>
                          <div style={{ color: 'var(--t2)', fontSize: '.78rem' }}>
                            Tarama başlatmak için üye girişi yapmalısınız. Sağ üstteki <strong style={{ color: '#75E6DA' }}>G Giriş Yap</strong> butonunu kullanın.
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="mb-4" style={{
                        background: quota.remaining > 0 ? 'rgba(0,212,170,0.06)' : 'rgba(255,45,85,0.08)',
                        border: `1px solid ${quota.remaining > 0 ? 'rgba(0,212,170,0.25)' : 'rgba(255,45,85,0.3)'}`,
                        borderRadius: '8px',
                        padding: '1rem 1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        flexWrap: 'wrap',
                        gap: '.5rem'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '.75rem' }}>
                          <span style={{ fontSize: '1.3rem' }}>{quota.remaining > 0 ? '🛡️' : '⛔'}</span>
                          <div>
                            <div style={{ color: 'var(--t1)', fontWeight: 600, fontSize: '.85rem' }}>
                              Hoş geldin, {session.user?.name?.split(' ')[0] || 'Üye'}
                            </div>
                            <div style={{ color: 'var(--t2)', fontSize: '.72rem' }}>
                              {quota.remaining > 0
                                ? `Bugün ${quota.remaining} tarama hakkınız kaldı`
                                : 'Günlük tarama limitinize ulaştınız. Yarın tekrar deneyin.'}
                            </div>
                          </div>
                        </div>
                        <div style={{
                          display: 'flex',
                          gap: '.4rem',
                          alignItems: 'center'
                        }}>
                          {[...Array(quota.limit)].map((_, i) => (
                            <div key={i} style={{
                              width: '28px',
                              height: '28px',
                              borderRadius: '6px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '.75rem',
                              fontWeight: 700,
                              background: i < quota.used
                                ? 'rgba(255,45,85,0.15)'
                                : 'rgba(0,212,170,0.15)',
                              border: `1px solid ${i < quota.used ? 'rgba(255,45,85,0.3)' : 'rgba(0,212,170,0.3)'}`,
                              color: i < quota.used ? '#ff2d55' : 'var(--accent)'
                            }}>
                              {i < quota.used ? '✕' : '✓'}
                            </div>
                          ))}
                          <span style={{ color: 'var(--t3)', fontSize: '.7rem', marginLeft: '.4rem' }}>
                            {quota.used}/{quota.limit}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Cloudflare Turnstile Captcha */}
                    {session?.user && quota.remaining > 0 && (
                      <div className="mb-4" style={{ display: 'flex', justifyContent: 'center' }}>
                        <div ref={turnstileRef}></div>
                      </div>
                    )}

                    <button className="btn-s" onClick={handleStartScan}
                      disabled={!target || isScanning || !session?.user || quota.remaining <= 0 || !turnstileToken}>
                      {isScanning ? (
                        <><div className="sp" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></div>Taranıyor... {progress}%</>
                      ) : !session?.user ? (
                        <>🔒 GİRİŞ YAPARAK TARAMA BAŞLATIN</>
                      ) : quota.remaining <= 0 ? (
                        <>⛔ GÜNLÜK LİMİT DOLDU</>
                      ) : <>▶ TARAMAYI BAŞLAT</>}
                    </button>

                    {isScanning && (
                      <div className="psec">
                        <div className="ph2">
                          <span className="plbl">⬡ {target} taranıyor</span>
                          <span className="ppct">{progress}%</span>
                        </div>
                        <div className="pwrap"><div className="pfill" style={{ width: `${progress}%` }}></div></div>
                        <div className="ts">
                          {toolProgress.completed.map((t, i) => <span key={i} className="tb d">✓ {t}</span>)}
                          {toolProgress.pending.map((t, i) => <span key={i} className="tb p"><div className="sp"></div>{t}</span>)}
                        </div>
                      </div>
                    )}

                    {!isScanning && scanResult && (
                      <div className="rs">
                        <div className="rh">
                          <h3 className="rt">// Tarama Sonuçları</h3>
                          <span className="rm">{scanResult.time} · {scanResult.mode.toUpperCase()}</span>
                        </div>
                        <div className="sgrid">
                          {scanResult.vulnerabilities.map((v, i) => (
                            <div key={i} className="sc" style={{ borderColor: `${sevColor(v.severity)}30`, backgroundColor: sevBg(v.severity) }}>
                              <span className="sl" style={{ color: sevColor(v.severity) }}>{v.severity}</span>
                              <span className="sn" style={{ color: v.count > 0 ? sevColor(v.severity) : 'var(--t3)' }}>{v.count}</span>
                            </div>
                          ))}
                        </div>
                        <div style={{ overflowX: 'auto' }}>
                          <table className="ft">
                            <thead><tr><th>Severity</th><th>Finding</th><th>Description</th></tr></thead>
                            <tbody>
                              {scanResult.findings.map((f) => (
                                <tr key={f.id}>
                                  <td><span className="sb" style={{ color: sevColor(f.severity), background: sevBg(f.severity), border: `1px solid ${sevColor(f.severity)}30` }}>{f.severity}</span></td>
                                  <td className="ftt">{f.title}</td>
                                  <td className="ftd">{f.description}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                        <div className="ra">
                          <button className="ba bo" onClick={() => window.print()}>⎙ PDF Yazdır</button>
                          <button className="ba bp" onClick={downloadCSV}>↓ CSV İndir</button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <History />
              )}
            </div>
          </div>
        </div>
      </section>
      <Footer />
    </>
  );
}

export default App;
