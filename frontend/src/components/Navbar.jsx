import React from 'react';

const Navbar = ({ onNavigate, currentView }) => {
    return (
        <section data-bs-version="5.1" className="menu menu6 cid-uV07AC1aCa" once="menu" id="menu06-a">
            <nav className="navbar navbar-dropdown opacityScrollOff navbar-fixed-top navbar-expand-lg">
                <div className="container">
                    <div className="navbar-brand" style={{ cursor: 'pointer' }} onClick={() => onNavigate('home')}>
                        <span className="navbar-logo">
                            <a>
                                <img src="/assets/images/capture-206x207.jpg" alt="Logo" style={{ height: '3rem' }} />
                            </a>
                        </span>
                    </div>
                    <button
                        className="navbar-toggler"
                        type="button"
                        data-toggle="collapse"
                        data-bs-toggle="collapse"
                        data-target="#navbarSupportedContent"
                        data-bs-target="#navbarSupportedContent"
                        aria-controls="navbarNavAltMarkup"
                        aria-expanded="false"
                        aria-label="Toggle navigation"
                    >
                        <div className="hamburger">
                            <span></span>
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </button>
                    <div className="collapse navbar-collapse opacityScrollOff" id="navbarSupportedContent">
                        <ul className="navbar-nav nav-dropdown nav-right" data-app-modern-menu="true">
                            <li className="nav-item">
                                <span className={`nav-link link text-black show display-4 ${currentView === 'home' ? 'text-primary' : ''}`} style={{ cursor: 'pointer' }} onClick={() => onNavigate('home')}>Dashboard</span>
                            </li>
                            <li className="nav-item">
                                <span className={`nav-link link text-black show display-4 ${currentView === 'history' ? 'text-primary' : ''}`} style={{ cursor: 'pointer' }} onClick={() => onNavigate('history')}>Scan History</span>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link link text-black show text-primary display-4" href="https://zaferkaraca.net/#testimonials-8-uSrJKo6yl4">Hakkımızda</a>
                            </li>

                            <li className="nav-item">
                                <a className="nav-link link text-black show text-primary display-4" href="https://postaci.zaferkaraca.net">Posta Hizmeti</a>
                            </li>
                            <li className="nav-item dropdown">
                                <a
                                    className="nav-link link text-black dropdown-toggle display-4"
                                    href="https://zaferkaraca.net"
                                    aria-expanded="false"
                                    data-toggle="dropdown-submenu"
                                    data-bs-toggle="dropdown"
                                    data-bs-auto-close="outside"
                                >
                                    Araçlar
                                </a>
                                <div className="dropdown-menu" aria-labelledby="dropdown-288">
                                    <a className="text-black show dropdown-item text-primary display-4" href="dashboard.html">Dashboard</a>
                                    <a className="text-black dropdown-item text-primary display-4" href="page1.html">Posta Araçları</a>
                                    <a className="text-black dropdown-item text-primary display-4" href="https://pentest.zaferkaraca.net/">Pentest</a>
                                    <a className="text-black show dropdown-item text-primary display-4" href="https://pdfoku.zaferkaraca.net/">PDF OKU</a>
                                </div>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link link text-black text-primary display-4" href="https://zaferkaraca.net/#contacts-2-uSrJKocEPl">İletişim</a>
                            </li>
                        </ul>
                        <div className="icons-menu">
                            <a className="iconfont-wrapper" href="tel:05346636464">
                                <span className="p-2 mbr-iconfont mobi-mbri-phone mobi-mbri"></span>
                            </a>
                            <a className="iconfont-wrapper" href="mailto:zafer@zaferkaraca.net">
                                <span className="p-2 mbr-iconfont mobi-mbri-letter mobi-mbri"></span>
                            </a>
                            <a className="iconfont-wrapper" href="https://zaferkaraca.net/#contacts-2-uSrJKocEPl">
                                <span className="p-2 mbr-iconfont mobi-mbri-map-pin mobi-mbri"></span>
                            </a>
                        </div>
                    </div>
                </div>
            </nav>
        </section>
    );
};

export default Navbar;
