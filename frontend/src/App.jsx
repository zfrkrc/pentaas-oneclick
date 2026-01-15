import React, { useState } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'

function App() {
  const [target, setTarget] = useState('');
  const [mode, setMode] = useState('black');

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
                    />
                  </div>

                  {/* Scan Mode Selection */}
                  <div className="col-12 mb-4">
                    <label className="form-label mbr-fonts-style display-7 w-100">Scan Mode</label>
                    <div className="d-flex flex-wrap gap-3 justify-content-center">

                      {/* White Box */}
                      <div
                        className={`p-3 border rounded cursor-pointer ${mode === 'white' ? 'bg-primary text-white' : 'bg-light'}`}
                        style={{ cursor: 'pointer', flex: '1 1 200px', textAlign: 'center', transition: 'all 0.3s' }}
                        onClick={() => setMode('white')}
                      >
                        <h4 className="mbr-fonts-style display-7"><strong>White Box</strong></h4>
                        <small>Full Access / Auth Scan</small>
                      </div>

                      {/* Gray Box */}
                      <div
                        className={`p-3 border rounded cursor-pointer ${mode === 'gray' ? 'bg-primary text-white' : 'bg-light'}`}
                        style={{ cursor: 'pointer', flex: '1 1 200px', textAlign: 'center', transition: 'all 0.3s' }}
                        onClick={() => setMode('gray')}
                      >
                        <h4 className="mbr-fonts-style display-7"><strong>Gray Box</strong></h4>
                        <small>Partial Access</small>
                      </div>

                      {/* Black Box */}
                      <div
                        className={`p-3 border rounded cursor-pointer ${mode === 'black' ? 'bg-primary text-white' : 'bg-light'}`}
                        style={{ cursor: 'pointer', flex: '1 1 200px', textAlign: 'center', transition: 'all 0.3s' }}
                        onClick={() => setMode('black')}
                      >
                        <h4 className="mbr-fonts-style display-7"><strong>Black Box</strong></h4>
                        <small>No Access / External</small>
                      </div>

                    </div>
                  </div>

                  {/* Start Button */}
                  <div className="col-12 text-center">
                    <button
                      className="btn btn-primary display-4 w-100"
                      onClick={() => alert(`Starting ${mode} scan on ${target}`)}
                      disabled={!target}
                    >
                      <span className="mobi-mbri mobi-mbri-play mbr-iconfont mbr-iconfont-btn"></span>
                      Start Scan
                    </button>
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
