import React, { useState, useEffect } from 'react';

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [hakkimizdaOpen, setHakkimizdaOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', onScroll);
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    return (
        <>
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;700&display=swap');
                
                /* Ana site ile birebir aynı stiller */
                .navbar-dropdown {
                    left: 0;
                    padding: 0;
                    position: fixed;
                    right: 0;
                    top: 0;
                    transition: all 0.45s ease;
                    z-index: 1030;
                    background: #282828;
                }
                .navbar-dropdown .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0.625rem 1.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                .navbar-dropdown .navbar-brand {
                    display: flex;
                    align-items: center;
                    text-decoration: none;
                }
                .navbar-dropdown .navbar-logo img {
                    height: 3rem;
                    transition: all 0.3s ease-in-out;
                }
                .navbar-dropdown .navbar-caption {
                    font-family: 'Golos Text', sans-serif;
                    font-weight: 700;
                    font-size: 1rem;
                    color: #ffffff;
                    margin-left: 0.5rem;
                }
                .navbar-dropdown .navbar-caption span {
                    color: #75E6DA;
                }
                .nav-dropdown {
                    display: flex;
                    align-items: center;
                    gap: 0;
                    list-style: none;
                    margin: 0;
                    padding: 0;
                    font-family: 'Golos Text', sans-serif;
                    font-size: 0.75rem;
                    font-weight: 500;
                }
                .nav-dropdown .nav-item {
                    position: relative;
                }
                .nav-dropdown .nav-link {
                    font-family: 'Golos Text', sans-serif;
                    font-size: 0.95rem;
                    font-weight: 500;
                    color: #ffffff;
                    text-decoration: none;
                    padding: 0.5rem 1rem;
                    transition: color 0.2s ease-in-out;
                    display: block;
                }
                .nav-dropdown .nav-link:hover {
                    color: #75E6DA;
                }
                .nav-dropdown .dropdown-toggle::after {
                    content: '▾';
                    font-size: 0.6rem;
                    margin-left: 0.25rem;
                }
                .nav-dropdown .dropdown-menu {
                    position: absolute;
                    top: 100%;
                    left: 0;
                    background: #1a1a1a;
                    border: 1px solid rgba(117, 230, 218, 0.2);
                    border-radius: 8px;
                    padding: 0.5rem 0;
                    min-width: 180px;
                    display: none;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
                }
                .nav-dropdown .dropdown.open .dropdown-menu {
                    display: block;
                }
                .nav-dropdown .dropdown-item {
                    font-family: 'Golos Text', sans-serif;
                    font-size: 0.9rem;
                    color: #cccccc;
                    text-decoration: none;
                    padding: 0.5rem 1rem;
                    display: block;
                    transition: all 0.15s;
                }
                .nav-dropdown .dropdown-item:hover {
                    color: #75E6DA;
                    background: rgba(117, 230, 218, 0.08);
                }
                .icons-menu {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                .icons-menu .iconfont-wrapper {
                    width: 36px;
                    height: 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 1px solid rgba(117, 230, 218, 0.2);
                    border-radius: 6px;
                    color: #cccccc;
                    text-decoration: none;
                    font-size: 0.9rem;
                    transition: all 0.2s;
                }
                .icons-menu .iconfont-wrapper:hover {
                    border-color: rgba(117, 230, 218, 0.5);
                    color: #75E6DA;
                    background: rgba(117, 230, 218, 0.06);
                }
                .navbar-toggler {
                    display: none;
                    background: transparent;
                    border: 1px solid rgba(117, 230, 218, 0.3);
                    border-radius: 6px;
                    padding: 0.5rem 0.75rem;
                    cursor: pointer;
                    color: #ffffff;
                }
                .hamburger span {
                    display: block;
                    width: 20px;
                    height: 2px;
                    background: #ffffff;
                    margin: 4px 0;
                    transition: 0.3s;
                }
                @media(max-width:991px) {
                    .nav-dropdown, .icons-menu { display: none; }
                    .navbar-toggler { display: block; }
                }
                .mobile-menu {
                    display: none;
                    padding: 1rem 1.5rem;
                    border-top: 1px solid rgba(117, 230, 218, 0.1);
                    background: #282828;
                }
                .mobile-menu.open {
                    display: block;
                }
                .mobile-menu a {
                    display: block;
                    padding: 0.6rem 0;
                    font-family: 'Golos Text', sans-serif;
                    font-size: 0.95rem;
                    color: #cccccc;
                    text-decoration: none;
                    border-bottom: 1px solid rgba(255,255,255,.06);
                    transition: color 0.2s;
                }
                .mobile-menu a:hover {
                    color: #75E6DA;
                }
                
                /* Body padding for fixed navbar */
                body {
                    padding-top: 70px;
                }
            `}</style>
            
            <nav className="navbar-dropdown">
                <div className="container">
                    <div className="navbar-brand">
                        <span className="navbar-logo">
                            <a href="https://zaferkaraca.net/">
                                <img src="/assets/images/zk_logo.webp" alt="Zafer Karaca Logo" />
                            </a>
                        </span>
                        <span className="navbar-caption">Pentest<span>One</span></span>
                    </div>
                    
                    <ul className="nav-dropdown">
                        <li className={`nav-item dropdown ${hakkimizdaOpen ? 'open' : ''}`}>
                            <a className="nav-link dropdown-toggle" href="#" onClick={(e) => { e.preventDefault(); setHakkimizdaOpen(!hakkimizdaOpen); }}>Hakkımızda</a>
                            <div className="dropdown-menu">
                                <a className="dropdown-item" href="https://zaferkaraca.net/#testimonials-8-uSrJKo6yl4">Şirket</a>
                                <a className="dropdown-item" href="https://zaferkaraca.net/hakkimda.html">Zafer Karaca</a>
                            </div>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="https://zaferkaraca.net/posta.html">Posta Hizmetleri</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="https://zaferkaraca.net/referanslar.html">Referanslar</a>
                        </li>
                        <li className={`nav-item dropdown ${dropdownOpen ? 'open' : ''}`}>
                            <a className="nav-link dropdown-toggle" href="#" onClick={(e) => { e.preventDefault(); setDropdownOpen(!dropdownOpen); }}>Araçlar</a>
                            <div className="dropdown-menu">
                                <a className="dropdown-item" href="https://hobby.zaferkaraca.net">Hobby</a>
                                <a className="dropdown-item" href="https://pentestone.zaferkaraca.net/">PentestOne</a>
                                <a className="dropdown-item" href="https://cyber.zaferkaraca.net/">Cyber Security</a>
                                <a className="dropdown-item" href="https://pdfoku.zaferkaraca.net/">PDF OKU</a>
                            </div>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="https://zaferkaraca.net/#contacts-2-uSrJKocEPl">İletişim</a>
                        </li>
                    </ul>
                    
                    <div className="icons-menu">
                        <a className="iconfont-wrapper" href="tel:+905346636464" title="Telefon">📞</a>
                        <a className="iconfont-wrapper" href="mailto:zafer@zaferkaraca.net" title="E-posta">✉️</a>
                        <a className="iconfont-wrapper" href="https://zaferkaraca.net/#contacts-2-uSrJKocEPl" title="Konum">📍</a>
                    </div>
                    
                    <button className="navbar-toggler" onClick={() => setIsOpen(!isOpen)}>
                        <div className="hamburger">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </button>
                </div>
                
                <div className={`mobile-menu ${isOpen ? 'open' : ''}`}>
                    <a href="https://zaferkaraca.net/#testimonials-8-uSrJKo6yl4">Şirket</a>
                    <a href="https://zaferkaraca.net/hakkimda.html">Zafer Karaca</a>
                    <a href="https://zaferkaraca.net/posta.html">Posta Hizmetleri</a>
                    <a href="https://zaferkaraca.net/referanslar.html">Referanslar</a>
                    <a href="https://hobby.zaferkaraca.net">Hobby</a>
                    <a href="https://pentestone.zaferkaraca.net/">PentestOne</a>
                    <a href="https://cyber.zaferkaraca.net/">Cyber Security</a>
                    <a href="https://pdfoku.zaferkaraca.net/">PDF OKU</a>
                    <a href="https://zaferkaraca.net/#contacts-2-uSrJKocEPl">İletişim</a>
                </div>
            </nav>
        </>
    );
};

export default Navbar;
