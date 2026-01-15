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

      {/* Sections removed: Testimonials, Video, Call to Action */}

      {/* Features Slider Section */}
      <section data-bs-version="5.1" className="features017 mbr-embla cid-uSrJKo86Hs" id="features-17-uSrJKo86Hs">
        <div className="position-relative">
          <div className="container-fluid">
            {/* Header removed */}
          </div>

          <div className="embla" data-skip-snaps="true" data-align="center" data-contain-scroll="trimSnaps" data-auto-play-interval="5" data-draggable="true">
            <div className="embla__viewport container-fluid">
              <div className="embla__container">
                <div className="embla__slide slider-image item active" style={{ marginLeft: '4rem', marginRight: '4rem' }}>
                  <div className="slide-content">
                    <div className="item-img">
                      <div className="item-wrapper">
                        <img src="/assets/images/photo-1584169417032-d34e8d805e8b.webp" alt="Scan" title="" data-slide-to="1" data-bs-slide-to="1" />
                      </div>
                    </div>
                    <div className="item-content">
                      <h5 className="item-title mbr-fonts-style display-5">
                        <strong>Network Scan</strong>
                      </h5>
                      <p className="mbr-text mbr-fonts-style mt-3 display-7">Comprehensive port scanning with Nmap.</p>
                    </div>
                  </div>
                </div>
                <div className="embla__slide slider-image item" style={{ marginLeft: '4rem', marginRight: '4rem' }}>
                  <div className="slide-content">
                    <div className="item-img">
                      <div className="item-wrapper">
                        <img src="/assets/images/photo-1683322499436-f4383dd59f5a.webp" alt="Web" title="" data-slide-to="2" data-bs-slide-to="2" />
                      </div>
                    </div>
                    <div className="item-content">
                      <h5 className="item-title mbr-fonts-style display-5">
                        <strong>Web Scan</strong>
                      </h5>
                      <p className="mbr-text mbr-fonts-style mt-3 display-7">Vulnerability scanning for web apps using ZAP.</p>
                    </div>
                  </div>
                </div>
                <div className="embla__slide slider-image item" style={{ marginLeft: '4rem', marginRight: '4rem' }}>
                  <div className="slide-content">
                    <div className="item-img">
                      <div className="item-wrapper">
                        {/* Reusing existing image as placeholder */}
                        <img src="/assets/images/photo-1667372459607-2cfe842fdc4b.webp" alt="CMS" title="" data-slide-to="3" data-bs-slide-to="3" />
                      </div>
                    </div>
                    <div className="item-content">
                      <h5 className="item-title mbr-fonts-style display-5">
                        <strong>CMS Scan</strong>
                      </h5>
                      <p className="mbr-text mbr-fonts-style mt-3 display-7">Specialized WPScan integration for WordPress sites.</p>
                    </div>
                  </div>
                </div>
                <div className="embla__slide slider-image item" style={{ marginLeft: '4rem', marginRight: '4rem' }}>
                  <div className="slide-content">
                    <div className="item-img">
                      <div className="item-wrapper">
                        <img src="/assets/images/photo-1573164713988-8665fc963095.webp" alt="SSL" title="" data-slide-to="4" data-bs-slide-to="4" />
                      </div>
                    </div>
                    <div className="item-content">
                      <h5 className="item-title mbr-fonts-style display-5">
                        <strong>SSL Tests</strong>
                      </h5>
                      <p className="mbr-text mbr-fonts-style mt-3 display-7">Verify SSL/TLS configurations with testssl.sh.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <button className="embla__button embla__button--prev">
              <span className="mobi-mbri mobi-mbri-arrow-prev mbr-iconfont" aria-hidden="true"></span>
              <span className="sr-only visually-hidden visually-hidden">Previous</span>
            </button>
            <button className="embla__button embla__button--next">
              <span className="mobi-mbri mobi-mbri-arrow-next mbr-iconfont" aria-hidden="true"></span>
              <span className="sr-only visually-hidden visually-hidden">Next</span>
            </button>
          </div>
        </div>
      </section>

      {/* Features Grid Section */}
      <section data-bs-version="5.1" className="features5 cid-uSrJKoa50J" id="features-22-uSrJKoa50J">
        <div className="container">
          <div className="row mb-5 justify-content-center">
            {/* Header removed */}
          </div>
          <div className="row">
            <div className="item features-without-image col-12 col-md-6 col-lg-4 item-mb">
              <div className="item-wrapper">
                <div className="card-box align-left">
                  <h5 className="card-title mbr-fonts-style display-5">
                    <strong>Automation</strong>
                  </h5>
                  <p className="card-text mbr-fonts-style display-7">Schedule and automate your security tests with Docker Compose Integration.</p>
                </div>
              </div>
            </div>
            <div className="item features-without-image col-12 col-md-6 col-lg-4 item-mb">
              <div className="item-wrapper">
                <div className="card-box align-left">
                  <h5 className="card-title mbr-fonts-style display-5">
                    <strong>Reporting</strong>
                  </h5>
                  <p className="card-text mbr-fonts-style display-7">Generate detailed reports in multiple formats (HTML, JSON).</p>
                </div>
              </div>
            </div>
            <div className="item features-without-image col-12 col-md-6 col-lg-4 item-mb">
              <div className="item-wrapper">
                <div className="card-box align-left">
                  <h5 className="card-title mbr-fonts-style display-5">
                    <strong>Scalability</strong>
                  </h5>
                  <p className="card-text mbr-fonts-style display-7">Built on modern microservices architecture.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

    </>
  )
}

export default App
