import React from 'react';

const Navbar = () => {
    return (
        <section data-bs-version="5.1" className="menu menu6 cid-uV07AC1aCa" once="menu" id="menu06-a">
            <nav className="navbar navbar-dropdown opacityScrollOff navbar-fixed-top navbar-expand-lg">
                <div className="container">
                    <div className="navbar-brand">
                        <span className="navbar-logo">
                            <a href="/">
                                <img src="/assets/images/capture-206x207.jpg" alt="Pentaas" style={{ height: '3rem' }} />
                            </a>
                        </span>
                        <span className="navbar-caption-wrap">
                            <a className="navbar-caption text-black display-7" href="/">Pentaas OneClick</a>
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
                                <a className="nav-link link text-black show text-primary display-4" href="/dashboard">Dashboard</a>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link link text-black show text-primary display-4" href="/scans">Scans</a>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link link text-black show text-primary display-4" href="/reports">Reports</a>
                            </li>
                            <li className="nav-item">
                                <a className="nav-link link text-black text-primary display-4" href="/settings">Settings</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
        </section>
    );
};

export default Navbar;
