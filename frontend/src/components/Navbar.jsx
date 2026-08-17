import React, { useState } from 'react';
import { authClient } from '../lib/auth';

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [dropdownOpen, setDropdownOpen] = useState(false);

    // Fetch session on load
    const { data: session } = authClient.useSession();

    const signInWithGoogle = async () => {
        await authClient.signIn.social({
            provider: "google",
            callbackURL: window.location.origin,  // pentestone.zaferkaraca.net'e geri dön
        });
    };

    const signOut = async () => {
        await authClient.signOut({
            fetchOptions: {
                credentials: "include",
            },
        });
        window.location.reload();
    };

    return (
        <>
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                
                /* Ana site ile birebir aynı stiller */
                .navbar-dropdown {
                    left: 0;
                    padding: 0;
                    position: fixed;
                    right: 0;
                    top: 0;
                    transition: all 0.45s ease;
                    z-index: 1030;
                    background: rgba(15, 34, 56, 0.92);
                    backdrop-filter: blur(12px);
                    -webkit-backdrop-filter: blur(12px);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
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
                    font-family: 'Inter', sans-serif;
                    font-weight: 700;
                    font-size: 1rem;
                    color: #ffffff;
                    margin-left: 0.5rem;
                }
                .navbar-dropdown .navbar-caption span {
                    color: #00D4FF;
                }
                .navbar-dropdown .product-label {
                    margin-left: 0.75rem;
                    padding-left: 0.75rem;
                    border-left: 1px solid rgba(255, 255, 255, 0.14);
                    color: #00D4FF;
                    font: 600 0.72rem/1 'Inter', sans-serif;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                }
                .nav-dropdown {
                    display: flex;
                    align-items: center;
                    gap: 0;
                    list-style: none;
                    margin: 0;
                    padding: 0;
                    font-family: 'Inter', sans-serif;
                    font-size: 0.75rem;
                    font-weight: 500;
                }
                .nav-dropdown .nav-item {
                    position: relative;
                }
                .nav-dropdown .nav-link {
                    font-family: 'Inter', sans-serif;
                    font-size: 0.85rem;
                    font-weight: 500;
                    color: #ffffff;
                    text-decoration: none;
                    padding: 0.5rem 1rem;
                    transition: color 0.2s ease-in-out;
                    display: block;
                }
                .nav-dropdown .nav-link:hover {
                    color: #00D4FF;
                }
                .nav-dropdown .nav-link.active-product {
                    color: #00D4FF;
                    background: rgba(0, 212, 255, 0.08);
                    border-radius: 5px;
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
                    border: 1px solid rgba(0, 212, 255, 0.2);
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
                    font-family: 'Inter', sans-serif;
                    font-size: 0.9rem;
                    color: #cccccc;
                    text-decoration: none;
                    padding: 0.5rem 1rem;
                    display: block;
                    transition: all 0.15s;
                }
                .nav-dropdown .dropdown-item:hover {
                    color: #00D4FF;
                    background: rgba(0, 212, 255, 0.08);
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
                    border: 1px solid rgba(0, 212, 255, 0.2);
                    border-radius: 6px;
                    color: #cccccc;
                    text-decoration: none;
                    font-size: 0.9rem;
                    transition: all 0.2s;
                }
                .icons-menu .iconfont-wrapper:hover {
                    border-color: rgba(0, 212, 255, 0.5);
                    color: #00D4FF;
                    background: rgba(0, 212, 255, 0.06);
                }
                .navbar-toggler {
                    display: none;
                    background: transparent;
                    border: 1px solid rgba(0, 212, 255, 0.3);
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
                    border-top: 1px solid rgba(255, 255, 255, 0.07);
                    background: rgba(15, 34, 56, 0.95);
                }
                .mobile-menu.open {
                    display: block;
                }
                .mobile-menu a {
                    display: block;
                    padding: 0.6rem 0;
                    font-family: 'Inter', sans-serif;
                    font-size: 0.85rem;
                    color: #cccccc;
                    text-decoration: none;
                    border-bottom: 1px solid rgba(255,255,255,.06);
                    transition: color 0.2s;
                }
                .mobile-menu a:hover {
                    color: #00D4FF;
                }
                
                /* Main content padding is handled by the component wrapper */
            `}</style>

            <nav className="navbar-dropdown">
                <div className="container">
                    <div className="navbar-brand">
                        <span className="navbar-logo">
                            <a href="https://zaferkaraca.net/">
                                <img src="https://zaferkaraca.net/assets/images/zk_logo-white.webp" alt="Zafer Karaca Logo" />
                            </a>
                        </span>
                        <a href="https://zaferkaraca.net/" className="navbar-caption">Zafer Karaca</a>
                        <span className="product-label">PENTAAS</span>
                    </div>

                    <ul className="nav-dropdown">
                        <li className="nav-item">
                            <a href="https://zaferkaraca.net/hakkimda" className="nav-link">Hakkımda</a>
                        </li>
                        <li className={`nav-item dropdown ${dropdownOpen ? 'open' : ''}`}>
                            <a className="nav-link dropdown-toggle" href="#" onClick={(e) => { e.preventDefault(); setDropdownOpen(!dropdownOpen); }}>Hizmetler</a>
                            <div className="dropdown-menu">
                                <a className="dropdown-item" href="https://zaferkaraca.net/insightmap">InsightMap AI</a>
                                <a className="dropdown-item" href="https://zaferkaraca.net/veri-merkezi-dr">Veri Merkezi &amp; DR</a>
                                <a className="dropdown-item" href="https://zaferkaraca.net/altyapi-sanallastirma">Altyapı &amp; Sanallaştırma</a>
                                <a className="dropdown-item active-product" href="https://zaferkaraca.net/pentaas" aria-current="page">Siber Güvenlik</a>
                                <a className="dropdown-item" href="https://zaferkaraca.net/posta">Kurumsal E-Posta</a>
                            </div>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="https://zaferkaraca.net/referanslar">Referanslar</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link" href="https://zaferkaraca.net/teklif-sihirbazi">Teklif Al</a>
                        </li>
                    </ul>

                    <div className="icons-menu" style={{ display: 'flex', alignItems: 'center' }}>
                        {session ? (
                            <div className="user-profile" title="Çıkış Yap" onClick={signOut} style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', marginLeft: '16px' }}>
                                <img src={session.user?.image || 'https://ui-avatars.com/api/?name=' + session.user?.name} style={{ width: 32, height: 32, borderRadius: '50%' }} />
                                <span style={{ color: '#00D4FF', fontSize: '0.85rem', fontFamily: 'Inter' }}>{session.user?.name?.split(' ')[0] || 'Hesabım'}</span>
                            </div>
                        ) : (
                            <button onClick={signInWithGoogle} className="btn-login" style={{ marginLeft: '16px', background: 'transparent', color: '#00D4FF', border: '1px solid rgba(0,212,255,.3)', borderRadius: '6px', padding: '6px 14px', fontSize: '0.85rem', cursor: 'pointer', fontFamily: 'Inter', display: 'flex', alignItems: 'center', gap: '6px', transition: 'all 0.3s' }}>
                                <span style={{ fontSize: '1rem' }}>G</span> Giriş Yap
                            </button>
                        )}
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
                    <a href="https://zaferkaraca.net/hakkimda">Hakkımda</a>
                    <a href="https://zaferkaraca.net/insightmap">InsightMap AI</a>
                    <a href="https://zaferkaraca.net/veri-merkezi-dr">Veri Merkezi &amp; DR</a>
                    <a href="https://zaferkaraca.net/altyapi-sanallastirma">Altyapı &amp; Sanallaştırma</a>
                    <a href="https://zaferkaraca.net/pentaas">Siber Güvenlik</a>
                    <a href="https://zaferkaraca.net/posta">Kurumsal E-Posta</a>
                    <a href="https://zaferkaraca.net/referanslar">Referanslar</a>
                    <a href="https://zaferkaraca.net/teklif-sihirbazi">Teklif Al</a>
                </div>
            </nav>
        </>
    );
};

export default Navbar;
