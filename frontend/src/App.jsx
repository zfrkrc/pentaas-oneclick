import React from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'

function App() {
  return (
    <>
      <Navbar />

      {/* Hero Section */}
      <section data-bs-version="5.1" className="header18 cid-uSrJKo5xsn mbr-fullscreen mbr-parallax-background" id="hero-16-uSrJKo5xsn">
        <div className="mbr-overlay" style={{ opacity: 0.5, backgroundColor: 'rgb(0, 0, 0)' }}></div>
        <div className="container-fluid">
          <div className="row">
            <div className="content-wrap col-12 col-md-12">
              <h1 className="mbr-section-title mbr-fonts-style mbr-white mb-4 display-1">
                <strong>Pentest One-Click</strong></h1>
              <p className="mbr-fonts-style mbr-text mbr-white mb-4 display-7">Comprehensive Security Testing Suite: Nmap, WPScan, ZAP, and more.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Intro / Testimonials Section (Repurpose for Quick Intro) */}
      <section data-bs-version="5.1" className="people07 cid-uSrJKo6yl4" id="testimonials-8-uSrJKo6yl4">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-md-12 col-lg-8">
              <p className="card-text mbr-fonts-style display-5">Identify vulnerabilities before they are exploited. Automated scanning for web and network assets.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Video Section (Placeholder as in source) */}
      <section data-bs-version="5.1" className="header18 cid-uSrJKo73AL mbr-fullscreen" id="video-5-uSrJKo73AL">
        <div className="mbr-overlay" style={{ opacity: 0, backgroundColor: 'rgb(0, 0, 0)' }}></div>
        <div className="container">
          <div className="row">
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section data-bs-version="5.1" className="header14 cid-uSrJKo7xHR mbr-fullscreen" id="call-to-action-9-uSrJKo7xHR">
        <div className="container">
          <div className="row justify-content-center">
            <div className="card col-12 col-md-12 col-lg-12">
              <div className="card-wrapper">
                <div className="card-box align-center">
                  <h1 className="card-title mbr-fonts-style mb-4 display-1"><strong>Start Scanning Now</strong></h1>
                  <p className="mbr-text mbr-fonts-style mb-4 display-7">Secure your infrastructure with our one-click solutions.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Slider Section */}
      <section data-bs-version="5.1" className="features017 mbr-embla cid-uSrJKo86Hs" id="features-17-uSrJKo86Hs">
        <div className="position-relative">
          <div className="container-fluid">
            <div className="row justify-content-center">
              <div className="col-12 content-head">
                <div className="mbr-section-head mb-5">
                  <h4 className="mbr-section-title mbr-fonts-style align-center mb-0 display-2">
                    <strong>Core Features</strong>
                  </h4>
                  <h5 className="mbr-section-subtitle mbr-fonts-style align-center mb-0 mt-4 display-7">Security at your fingertips</h5>
                </div>
              </div>
            </div>
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
            <div className="col-12 content-head">
              <h3 className="mbr-section-title mbr-fonts-style align-center mb-0 display-2">
                <strong>Security Solutions</strong>
              </h3>
            </div>
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

      <Footer />
    </>
  )
}

export default App
