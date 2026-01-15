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
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsScanning(false);
          setScanResult({
            ip: target,
            mode: mode,
            vulnerabilities: [
              { severity: 'Critical', count: 2 },
              { severity: 'High', count: 5 },
              { severity: 'Medium', count: 12 },
              { severity: 'Low', count: 24 }
            ],
            time: new Date().toLocaleString()
          });
          return 100;
        }
        return prev + 5;
      });
    }, 300);

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

                        <div className="mt-4 pt-3 border-top text-end">
                          <button className="btn btn-outline-dark display-4 me-2" onClick={() => window.print()}>
                            <span className="mobi-mbri mobi-mbri-print mbr-iconfont mbr-iconfont-btn"></span>
                            Print PDF
                          </button>
                          <button className="btn btn-primary display-4" onClick={() => alert('Full report downloading...')}>
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
