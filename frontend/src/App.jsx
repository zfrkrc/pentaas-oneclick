import React, { useState } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'

function App() {
  const [target, setTarget] = useState('');
  const [mode, setMode] = useState('black');
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [scanResult, setScanResult] = useState(null);


  const handleStartScan = () => {
    setIsScanning(true);
    setProgress(0);
    setScanResult(null);

    // Mode-specific templates
    const templates = {
      black: {
        findings: [
          { id: 1, title: 'Unencrypted HTTP Communication', severity: 'High', description: 'Sensitive data transmitted over plain text.' },
          { id: 2, title: 'Insecure SSL Cipher Suite', severity: 'Medium', description: 'Server supports deprecated TLS 1.0/1.1.' },
          { id: 3, title: 'Missing Security Headers', severity: 'Medium', description: 'HSTS and CSP headers are not present.' },
          { id: 4, title: 'Exposed Server Signature', severity: 'Low', description: 'Server version (Nginx/1.18.0) is visible in headers.' },
          { id: 5, title: 'Open Port 8080', severity: 'Low', description: 'Non-standard HTTP port is accessible externally.' },
          { id: 6, title: 'Directory Browsing Enabled', severity: 'Low', description: '/backup directory allows file listing.' }
        ]
      },
      gray: {
        findings: [
          { id: 1, title: 'Session Hijacking via Lack of CSRF', severity: 'Critical', description: 'Forms lack anti-CSRF tokens.' },
          { id: 2, title: 'Insecure Direct Object Reference (IDOR)', severity: 'High', description: 'User data accessible by changing ID in URL.' },
          { id: 3, title: 'Privilege Escalation', severity: 'High', description: 'Regular users can access admin endpoints.' },
          { id: 4, title: 'Weak Password Policy', severity: 'Medium', description: 'Passwords lack complexity requirements.' },
          { id: 5, title: 'Session Timeout Not Configured', severity: 'Medium', description: 'Sessions remain active indefinitely.' },
          { id: 6, title: 'Improper Error Handling', severity: 'Low', description: 'Stack traces visible on 500 errors.' }
        ]
      },
      white: {
        findings: [
          { id: 1, title: 'Blind SQL Injection on /api/v1/search', severity: 'Critical', description: 'Database exfiltration possible via time-based injection.' },
          { id: 2, title: 'Remote Code Execution (RCE)', severity: 'Critical', description: 'Unsafe deserialization detected in file upload.' },
          { id: 3, title: 'Hardcoded API Credentials', severity: 'High', description: 'AWS Secret keys found in frontend build artifacts.' },
          { id: 4, title: 'Insecure Cryptographic Storage', severity: 'High', description: 'User passwords stored using MD5 instead of Argon2/BCrypt.' },
          { id: 5, title: 'XML External Entity (XXE) Injection', severity: 'High', description: 'XML parser allows external entity references.' },
          { id: 6, title: 'Command Injection in Log Parser', severity: 'High', description: 'User input passed directly to shell commands.' },
          { id: 7, title: 'Path Traversal Vulnerability', severity: 'Medium', description: 'File download endpoint allows ../../../etc/passwd access.' },
          { id: 8, title: 'Insecure Deserialization', severity: 'Medium', description: 'Pickle files accepted without validation.' }
        ]
      }
    };

    const selected = templates[mode] || templates.black;

    // Calculate counts dynamically from findings
    const calculateCounts = (findings) => {
      const counts = { Critical: 0, High: 0, Medium: 0, Low: 0 };
      findings.forEach(f => {
        if (counts[f.severity] !== undefined) {
          counts[f.severity]++;
        }
      });
      return [counts.Critical, counts.High, counts.Medium, counts.Low];
    };

    const counts = calculateCounts(selected.findings);

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsScanning(false);
          setScanResult({
            ip: target,
            mode: mode,
            vulnerabilities: [
              { severity: 'Critical', count: counts[0] },
              { severity: 'High', count: counts[1] },
              { severity: 'Medium', count: counts[2] },
              { severity: 'Low', count: counts[3] }
            ],
            findings: selected.findings,
            time: new Date().toLocaleString()
          });
          return 100;
        }
        return prev + 5;
      });
    }, 300);
  };



  const downloadCSV = () => {
    console.log("Download CSV triggered. ScanResult:", scanResult);
    if (!scanResult) {
      console.error("No scan result found to download.");
      return;
    }

    try {
      // Calculate total vulnerabilities
      const totalVulns = scanResult.vulnerabilities.reduce((sum, v) => sum + v.count, 0);

      // Create comprehensive CSV with metadata
      const rows = [
        ["PENTAAS ONECLICK - SECURITY SCAN REPORT"],
        [""],
        ["SCAN INFORMATION"],
        ["Target", scanResult.ip],
        ["Scan Mode", scanResult.mode.toUpperCase() + " BOX"],
        ["Scan Time", scanResult.time],
        ["Total Vulnerabilities", totalVulns],
        [""],
        ["VULNERABILITY SUMMARY"]
      ];

      scanResult.vulnerabilities.forEach(v => {
        rows.push([v.severity, v.count]);
      });

      rows.push([""]);
      rows.push(["DETAILED FINDINGS"]);
      rows.push(["ID", "Title", "Severity", "Description"]);

      scanResult.findings.forEach(f => {
        rows.push([f.id, f.title, f.severity, f.description]);
      });

      const csvContent = rows.map(e => e.map(val => `"${val}"`).join(",")).join("\n");
      console.log("CSV Content generated, size:", csvContent.length);

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');

      const safeIp = scanResult.ip.replace(/[^a-z0-9]/gi, '_');
      const filename = "pentaas_report_" + safeIp + "_" + scanResult.mode + ".csv";

      console.log("Attempting download with filename:", filename);

      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();

      setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        console.log("Download cleanup complete.");
      }, 100);
    } catch (err) {
      console.error("Error during CSV generation/download:", err);
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
                      </div>
                    )}

                    {!isScanning && scanResult && (
                      <div className="mt-5 p-4 border rounded shadow-sm" style={{ backgroundColor: '#fff', borderLeft: '5px solid #232323' }}>
                        <div className="d-flex justify-content-between align-items-center mb-3">
                          <h3 className="mbr-fonts-style display-5 mb-0"><strong>Scan Results</strong></h3>
                          <span className="badge bg-dark p-2">{scanResult.time}</span>
                        </div>
                        <p className="mbr-fonts-style display-7 mb-4">
                          Target: <strong>{scanResult.ip}</strong> | Mode: <strong>{scanResult.mode.toUpperCase()}</strong>
                        </p>

                        <div className="row g-3">
                          {scanResult.vulnerabilities.map((v, i) => (
                            <div key={i} className="col-6 col-md-3">
                              <div className="p-3 text-center border rounded bg-light">
                                <h4 className={`mbr-fonts-style display-7 mb-1 ${v.severity === 'Critical' ? 'text-danger' : v.severity === 'High' ? 'text-warning' : 'text-primary'}`}>
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
