import React, { useState } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'

function App() {
  const [target, setTarget] = useState('');
  const [mode, setMode] = useState('black');
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [scanResult, setScanResult] = useState(null);
  const [toolProgress, setToolProgress] = useState({ completed: [], pending: [] });



  const handleStartScan = async () => {
    setIsScanning(true);
    setProgress(10); // Start with some progress
    setScanResult(null);

    try {
      // 1. Trigger the scan
      const response = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip: target, category: mode })
      });

      if (!response.ok) throw new Error('Scan starting failed');
      const { scan_id } = await response.json();
      console.log("Scan started with ID:", scan_id);

      // 2. Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch(`/api/scan/${scan_id}`);
          if (!statusRes.ok) return;
          const statusData = await statusRes.json();

          // Fetch intermediate results to show progress
          fetchResults(scan_id, false);

          if (statusData.status === 'completed') {
            clearInterval(pollInterval);
            fetchResults(scan_id, true);
          } else if (statusData.status === 'running') {
            setProgress((prev) => (prev < 90 ? prev + 2 : prev)); // Visual progress
          }
        } catch (pollErr) {
          console.error("Polling error:", pollErr);
        }
      }, 4000);


    } catch (err) {
      console.error("Scan Error:", err);
      alert("Hata: Tarama başlatılamadı. Backend servisinin çalıştığından emin olun.");
      setIsScanning(false);
    }
  };

  const fetchResults = async (scanId, isFinal = false) => {
    try {
      const res = await fetch(`/api/scan/${scanId}/results`);
      if (!res.ok) throw new Error('Could not fetch results');
      const data = await res.json();

      // Update tool progress
      if (data.progress) {
        setToolProgress(data.progress);
      }

      // Calculate counts from real findings
      const counts = { Critical: 0, High: 0, Medium: 0, Low: 0, Info: 0 };
      data.findings.forEach(f => {
        if (counts[f.severity] !== undefined) counts[f.severity]++;
        else if (f.severity === 'Info' || f.severity === 'Informational') counts.Info++;
      });

      setScanResult({
        ip: target,
        mode: mode,
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

      if (isFinal) {
        setProgress(100);
        setIsScanning(false);
      }
    } catch (err) {
      console.error("Results Fetch Error:", err);
      if (isFinal) {
        alert("Sonuçlar alınırken hata oluştu.");
        setIsScanning(false);
      }
    }
  };




  const downloadCSV = () => {
    if (!scanResult) {
      alert("Hata: Tarama sonucu bulunamadı.");
      return;
    }

    try {
      console.log("CSV hazırlanalıyor...");
      const totalVulns = scanResult.vulnerabilities.reduce((sum, v) => sum + v.count, 0);

      let csvRows = [
        "PENTAAS ONECLICK - SCAN REPORT",
        "",
        "SCAN INFO",
        `Target,${scanResult.ip}`,
        `Mode,${scanResult.mode}`,
        `Time,${scanResult.time}`,
        `Total Findings,${totalVulns}`,
        "",
        "SUMMARY",
        "Severity,Count"
      ];

      scanResult.vulnerabilities.forEach(v => {
        csvRows.push(`${v.severity},${v.count}`);
      });

      csvRows.push("", "DETAILED FINDINGS", "ID,Title,Severity,Description");

      scanResult.findings.forEach(f => {
        const descToken = f.description.replace(/,/g, ';'); // escape commas for simple CSV
        csvRows.push(`${f.id},${f.title},${f.severity},${descToken}`);
      });

      const csvContent = csvRows.join("\n");
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      const safeIp = scanResult.ip.replace(/[^a-z0-9]/gi, '_');

      link.href = url;
      link.download = `pentaas_${safeIp}.csv`;
      document.body.appendChild(link);
      link.click();

      setTimeout(() => {
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }, 500);

      alert("Rapor indiriliyor: " + link.download + "\nNot: Rapor tarayıcı tarafından oluşturuldu, sunucuya kaydedilmedi.");
    } catch (err) {
      alert("Hata oluştu: " + err.message);
    }
  };



  return (
    <>
      <Navbar />

      {/* Hero Section - Scanner Interface */}
      <section data-bs-version="5.1" className="header18 cid-uSrJKo5xsn mbr-fullscreen mbr-parallax-background" id="hero-16-uSrJKo5xsn">
        <div className="mbr-overlay" style={{ opacity: 0.6, backgroundColor: 'rgb(0, 0, 0)' }}></div>
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-12 col-md-10">
              <h1 className="mbr-section-title mbr-fonts-style mbr-white mb-4 display-2 text-center">
                <strong>Start Security Scan</strong>
              </h1>

              <div className="card p-4" style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderRadius: '1rem' }}>
                <div className="row">
                  {/* Target Input */}
                  <div className="col-12 mb-4">
                    <label className="form-label mbr-fonts-style display-7">Target IP / Hostname</label>
                    <input
                      type="text"
                      className="form-control form-control-lg"
                      placeholder="e.g., 192.168.1.1 or example.com"
                      value={target}
                      onChange={(e) => setTarget(e.target.value)}
                      disabled={isScanning}
                    />

                  </div>

                  {/* Scan Mode Selection */}
                  <div className="col-12 mb-4">
                    <label className="form-label mbr-fonts-style display-7 w-100">Scan Mode</label>
                    <div className="d-flex flex-wrap gap-3 justify-content-center">

                      {/* White Box */}
                      <div
                        className={`p-3 border rounded cursor-pointer ${mode === 'white' ? 'bg-primary text-white' : 'bg-light'} ${isScanning ? 'opacity-50' : ''}`}
                        style={{ cursor: isScanning ? 'not-allowed' : 'pointer', flex: '1 1 200px', textAlign: 'center', transition: 'all 0.3s' }}
                        onClick={() => !isScanning && setMode('white')}
                      >

                        <h4 className="mbr-fonts-style display-7"><strong>White Box</strong></h4>
                        <small>Full Access / Auth Scan</small>
                      </div>

                      {/* Gray Box */}
                      <div
                        className={`p-3 border rounded cursor-pointer ${mode === 'gray' ? 'bg-primary text-white' : 'bg-light'} ${isScanning ? 'opacity-50' : ''}`}
                        style={{ cursor: isScanning ? 'not-allowed' : 'pointer', flex: '1 1 200px', textAlign: 'center', transition: 'all 0.3s' }}
                        onClick={() => !isScanning && setMode('gray')}
                      >

                        <h4 className="mbr-fonts-style display-7"><strong>Gray Box</strong></h4>
                        <small>Partial Access</small>
                      </div>

                      {/* Black Box */}
                      <div
                        className={`p-3 border rounded cursor-pointer ${mode === 'black' ? 'bg-primary text-white' : 'bg-light'} ${isScanning ? 'opacity-50' : ''}`}
                        style={{ cursor: isScanning ? 'not-allowed' : 'pointer', flex: '1 1 200px', textAlign: 'center', transition: 'all 0.3s' }}
                        onClick={() => !isScanning && setMode('black')}
                      >

                        <h4 className="mbr-fonts-style display-7"><strong>Black Box</strong></h4>
                        <small>No Access / External</small>
                      </div>

                    </div>
                  </div>

                  {/* Start Button */}
                  <div className="col-12 text-center">
                    <button
                      className={`btn btn-primary display-4 w-100 ${isScanning ? 'disabled' : ''}`}
                      onClick={handleStartScan}
                      disabled={!target || isScanning}
                    >
                      {isScanning ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Scanning... {progress}%
                        </>
                      ) : (
                        <>
                          <span className="mobi-mbri mobi-mbri-play mbr-iconfont mbr-iconfont-btn"></span>
                          Start Scan
                        </>
                      )}
                    </button>

                    {isScanning && (
                      <div className="mt-4">
                        <div className="progress" style={{ height: '20px', borderRadius: '10px', backgroundColor: '#e9ecef' }}>
                          <div
                            className="progress-bar progress-bar-striped progress-bar-animated"
                            role="progressbar"
                            style={{ width: `${progress}%`, backgroundColor: '#232323' }}
                            aria-valuenow={progress}
                            aria-valuemin="0"
                            aria-valuemax="100"
                          ></div>
                        </div>
                        <p className="text-center mt-2 mbr-fonts-style display-7" style={{ color: '#232323' }}>
                          Scanning <strong>{target}</strong>... {progress}%
                        </p>

                        <div className="mt-3 p-3 bg-white rounded shadow-sm border" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                          <h6 className="mbr-fonts-style display-7 mb-3 text-start"><strong>Tool Status:</strong></h6>
                          <div className="d-flex flex-wrap gap-2">
                            {toolProgress.completed.map((t, idx) => (
                              <span key={idx} className="badge bg-success p-2">
                                <span className="mobi-mbri mobi-mbri-success mbr-iconfont me-1" style={{ fontSize: '1rem' }}></span>
                                {t}
                              </span>
                            ))}
                            {toolProgress.pending.map((t, idx) => (
                              <span key={idx} className="badge bg-light text-dark border p-2">
                                <span className="spinner-border spinner-border-sm me-1" role="status" style={{ width: '0.8rem', height: '0.8rem' }}></span>
                                {t}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}


                    {!isScanning && scanResult && (
                      <div id="scan-results" className="mt-5 p-4 border rounded shadow-sm" style={{ backgroundColor: '#fff', borderLeft: '5px solid #232323' }}>
                        <div className="d-flex justify-content-between align-items-center mb-3">
                          <h3 className="mbr-fonts-style display-5 mb-0"><strong>Scan Results</strong></h3>
                          <span className="badge bg-dark p-2">{scanResult.time}</span>
                        </div>
                        <p className="mbr-fonts-style display-7 mb-4">
                          Target: <strong>{scanResult.ip}</strong> | Mode: <strong>{scanResult.mode.toUpperCase()}</strong>
                        </p>

                        <div className="row g-3">
                          {scanResult.vulnerabilities.map((v, i) => (
                            <div key={i} className="col">
                              <div className="p-3 text-center border rounded bg-light" style={{ minWidth: '100px' }}>
                                <h4 className={`mbr-fonts-style display-7 mb-1 ${v.severity === 'Critical' ? 'text-danger' : v.severity === 'High' ? 'text-warning' : v.severity === 'Medium' ? 'text-primary' : 'text-muted'}`}>
                                  <strong>{v.severity}</strong>
                                </h4>
                                <span className="display-5"><strong>{v.count}</strong></span>
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Detailed Findings Section */}
                        <div className="mt-5">
                          <h4 className="mbr-fonts-style display-6 mb-4"><strong>Detailed Findings</strong></h4>
                          <div className="table-responsive">
                            <table className="table table-hover">
                              <thead className="table-dark">
                                <tr>
                                  <th>Severity</th>
                                  <th>Finding</th>
                                  <th>Description</th>
                                </tr>
                              </thead>
                              <tbody>
                                {scanResult.findings.map((f) => (
                                  <tr key={f.id}>
                                    <td>
                                      <span className={`badge ${f.severity === 'Critical' ? 'bg-danger' : f.severity === 'High' ? 'bg-warning text-dark' : 'bg-info'}`}>
                                        {f.severity}
                                      </span>
                                    </td>
                                    <td><strong>{f.title}</strong></td>
                                    <td><small>{f.description}</small></td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>

                        <div className="mt-4 pt-3 border-top text-end">
                          <button className="btn btn-outline-dark display-4 me-2" onClick={() => window.print()}>
                            <span className="mobi-mbri mobi-mbri-print mbr-iconfont mbr-iconfont-btn"></span>
                            Print PDF
                          </button>
                          <button className="btn btn-primary display-4" onClick={downloadCSV}>
                            <span className="mobi-mbri mobi-mbri-download mbr-iconfont mbr-iconfont-btn"></span>
                            Download CSV
                          </button>
                        </div>
                      </div>
                    )}



                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

      <Footer />
    </>
  )
}

export default App
