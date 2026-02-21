import React, { useState, useEffect } from 'react';

function History() {
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => { fetchScans(); }, []);

    const fetchScans = async () => {
        try {
            const res = await fetch('/api/scans');
            if (!res.ok) throw new Error("API call failed");
            const data = await res.json();
            setScans(data.scans || []);
        } catch (err) {
            console.error("Failed to fetch scans", err);
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = async (scanId, target) => {
        try {
            const res = await fetch(`/api/scan/${scanId}/results`);
            if (!res.ok) throw new Error("API call failed");
            const data = await res.json();
            const csvRows = [
                "PENTAAS ONECLICK - SCAN REPORT", "",
                "SCAN INFO",
                `Target,${data.target}`, `Mode,${data.scan_type}`,
                `Time,${new Date(data.timestamp).toLocaleString()}`,
                `Total Findings,${data.findings.length}`,
                "", "DETAILED FINDINGS", "ID,Title,Severity,Description"
            ];
            if (data.findings) {
                data.findings.forEach(f => {
                    const desc = f.description ? f.description.replace(/(\r\n|\n|\r)/gm, " ").replace(/,/g, ";") : "";
                    csvRows.push(`${f.id},${f.title},${f.severity},${desc}`);
                });
            }
            const blob = new Blob([csvRows.join("\n")], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = `report_${target}_${scanId}.csv`;
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
        } catch (err) { alert("Rapor indirilemedi: " + err.message); }
    };

    const typeColor = (t) => ({ white: '#00d4aa', gray: '#94a3b8', black: '#e2e8f0' }[t] || '#94a3b8');
    const statusColor = (s) => ({ completed: '#00d4aa', running: '#f5c518', failed: '#ff2d55' }[s] || '#94a3b8');
    const statusBg = (s) => ({ completed: 'rgba(0,212,170,.1)', running: 'rgba(245,197,24,.1)', failed: 'rgba(255,45,85,.1)' }[s] || 'rgba(148,163,184,.1)');

    return (
        <>
            <style>{`
                .hist-panel{background:#111827;border:1px solid rgba(0,212,170,.15);border-radius:12px;overflow:hidden;font-family:'JetBrains Mono',monospace;}
                .hist-head{padding:1rem 1.5rem;border-bottom:1px solid rgba(0,212,170,.15);display:flex;align-items:center;justify-content:space-between;}
                .hist-title{font-size:.75rem;color:#475569;letter-spacing:.1em;text-transform:uppercase;}
                .hist-refresh{background:transparent;border:1px solid rgba(0,212,170,.2);border-radius:4px;padding:.3rem .7rem;font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#00d4aa;cursor:pointer;transition:all .2s;}
                .hist-refresh:hover{background:rgba(0,212,170,.1);border-color:rgba(0,212,170,.4);}
                .htable{width:100%;border-collapse:separate;border-spacing:0 3px;}
                .htable thead th{font-size:.65rem;text-transform:uppercase;letter-spacing:.12em;color:#475569;padding:.75rem 1.25rem;border-bottom:1px solid rgba(0,212,170,.1);font-weight:500;}
                .htable tbody tr{background:#0d1117;transition:background .15s;}
                .htable tbody tr:hover{background:#161f2e;}
                .htable tbody td{padding:.85rem 1.25rem;font-size:.8rem;color:#94a3b8;vertical-align:middle;}
                .htable tbody td:first-child{border-radius:6px 0 0 6px;}
                .htable tbody td:last-child{border-radius:0 6px 6px 0;}
                .hbadge{font-size:.62rem;padding:.2rem .5rem;border-radius:3px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;}
                .hbtn{background:transparent;border:1px solid rgba(0,212,170,.2);border-radius:4px;padding:.3rem .75rem;font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#00d4aa;cursor:pointer;transition:all .2s;}
                .hbtn:hover{background:rgba(0,212,170,.1);border-color:rgba(0,212,170,.4);}
                .hempty{text-align:center;padding:3rem;color:#475569;font-size:.8rem;}
            `}</style>
            <div className="hist-panel">
                <div className="hist-head">
                    <span className="hist-title">// Tarama Geçmişi</span>
                    <button className="hist-refresh" onClick={fetchScans}>↻ Yenile</button>
                </div>
                <div style={{ overflowX: 'auto' }}>
                    <table className="htable">
                        <thead>
                            <tr>
                                <th>Tarih</th>
                                <th>Hedef</th>
                                <th>Tip</th>
                                <th>Durum</th>
                                <th style={{ textAlign: 'right' }}>Eylem</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan="5" className="hempty">Yükleniyor...</td></tr>
                            ) : scans.length === 0 ? (
                                <tr><td colSpan="5" className="hempty">Henüz tarama yapılmadı.</td></tr>
                            ) : (
                                scans.map(scan => (
                                    <tr key={scan.scan_id}>
                                        <td>{new Date(scan.timestamp).toLocaleString()}</td>
                                        <td style={{ color: '#e2e8f0', fontWeight: 600 }}>{scan.target}</td>
                                        <td>
                                            <span className="hbadge" style={{ color: typeColor(scan.scan_type), background: `${typeColor(scan.scan_type)}15`, border: `1px solid ${typeColor(scan.scan_type)}30` }}>
                                                {scan.scan_type.toUpperCase()}
                                            </span>
                                        </td>
                                        <td>
                                            <span className="hbadge" style={{ color: statusColor(scan.status), background: statusBg(scan.status), border: `1px solid ${statusColor(scan.status)}30` }}>
                                                {scan.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td style={{ textAlign: 'right' }}>
                                            <button className="hbtn" onClick={() => window.open(`/api/report/${scan.scan_id}`, '_blank')}>
                                                ↗ Rapor
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </>
    );
}

export default History;
