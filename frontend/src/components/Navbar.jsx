import React, { useState, useEffect } from 'react';

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', onScroll);
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    return (
        <>
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;700&display=swap');
                .pnav{position:sticky;top:0;z-index:1000;transition:all .3s;font-family:'Golos Text',sans-serif;border-bottom:1px solid transparent;}
                .pnav.s{background:rgba(9,11,16,.95);backdrop-filter:blur(12px);border-bottom:1px solid rgba(0,212,170,.12);}
                .pnav:not(.s){background:rgba(9,11,16,.8);backdrop-filter:blur(8px);}
                .pnav-inner{max-width:1200px;margin:0 auto;padding:.9rem 1.5rem;display:flex;align-items:center;justify-content:space-between;}
                .pnav-brand{display:flex;align-items:center;gap:.75rem;text-decoration:none;}
                .pnav-logo{height:36px;width:36px;border-radius:6px;object-fit:cover;border:1px solid rgba(0,212,170,.25);}
                .pnav-name{font-size:.8rem;font-weight:700;color:#e2e8f0;letter-spacing:.05em;}
                .pnav-name span{color:#00d4aa;}
                .pnav-links{display:flex;align-items:center;gap:1.5rem;list-style:none;margin:0;padding:0;}
                .pnav-links a{font-size:.75rem;color:#94a3b8;text-decoration:none;letter-spacing:.08em;transition:color .2s;text-transform:uppercase;}
                .pnav-links a:hover{color:#00d4aa;}
                .pnav-dd{position:relative;}
                .pnav-dd-btn{font-size:.75rem;color:#94a3b8;background:none;border:none;cursor:pointer;font-family:'JetBrains Mono',monospace;letter-spacing:.08em;text-transform:uppercase;transition:color .2s;padding:0;display:flex;align-items:center;gap:.35rem;}
                .pnav-dd-btn:hover{color:#00d4aa;}
                .pnav-dd-btn::after{content:'▾';font-size:.6rem;}
                .pnav-menu{position:absolute;top:calc(100% + .75rem);right:0;background:#0d1117;border:1px solid rgba(0,212,170,.2);border-radius:8px;padding:.4rem;min-width:180px;display:none;box-shadow:0 16px 40px rgba(0,0,0,.6);}
                .pnav-dd.open .pnav-menu{display:block;}
                .pnav-menu a{display:block;padding:.6rem 1rem;font-size:.72rem;color:#94a3b8;text-decoration:none;border-radius:5px;transition:all .15s;letter-spacing:.06em;}
                .pnav-menu a:hover{color:#00d4aa;background:rgba(0,212,170,.08);}
                .pnav-icons{display:flex;align-items:center;gap:.5rem;}
                .pnav-icon{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(0,212,170,.15);border-radius:6px;color:#94a3b8;text-decoration:none;font-size:.85rem;transition:all .2s;}
                .pnav-icon:hover{border-color:rgba(0,212,170,.4);color:#00d4aa;background:rgba(0,212,170,.06);}
                .pnav-toggle{display:none;background:transparent;border:1px solid rgba(0,212,170,.2);border-radius:6px;padding:.4rem .6rem;cursor:pointer;color:#94a3b8;font-size:1rem;}
                @media(max-width:768px){
                    .pnav-links,.pnav-icons{display:none;}
                    .pnav-toggle{display:block;}
                    .pnav-mobile{display:block;}
                }
                .pnav-mobile{display:none;padding:1rem 1.5rem;border-top:1px solid rgba(0,212,170,.1);}
                .pnav-mobile a{display:block;padding:.6rem 0;font-size:.78rem;color:#94a3b8;text-decoration:none;border-bottom:1px solid rgba(255,255,255,.04);transition:color .2s;}
                .pnav-mobile a:hover{color:#00d4aa;}
            `}</style>
            <nav className={`pnav ${scrolled ? 's' : ''}`}>
                <div className="pnav-inner">
                    <a href="/" className="pnav-brand">
                        <img src="/assets/images/zk_logo.webp" alt="Zafer Karaca Logo" style={{height:'3rem', width:'auto'}} />
                        <span className="pnav-name">Pentest<span>One</span></span>
                    </a>

                    <ul className="pnav-links">
                        <li><a className="nav-link link text-black show text-primary display-4" href="https://zaferkaraca.net/#testimonials-8-uSrJKo6yl4" aria-expanded="false">Hakkımızda</a></li>
                        <li><a className="nav-link link text-black show text-primary display-4" href="https://postaci.zaferkaraca.net">Posta Hizmeti</a></li>
                        <li><a className="nav-link link text-black show text-primary display-4" href="https://hobby.zaferkaraca.net">Hobby</a></li>
                        <li className={`pnav-dd ${isOpen ? 'open' : ''}`}>
                            <button className="pnav-dd-btn" onClick={() => setIsOpen(!isOpen)}>Araçlar</button>
                            <div className="pnav-menu">
                                <a className="text-black dropdown-item text-primary display-4" href="https://pentestone.zaferkaraca.net/">PentestOne</a>
                                <a className="text-black dropdown-item text-primary display-4" href="https://cyber.zaferkaraca.net/">Cyber Security</a>
                                <a className="text-black show dropdown-item text-primary display-4" href="https://pdfoku.zaferkaraca.net/">PDF OKU</a>
                            </div>
                        </li>
                        <li><a className="nav-link link text-black text-primary display-4" href="https://zaferkaraca.net/#contacts-2-uSrJKocEPl">İletişim</a></li>
                    </ul>

                            .pnav-dd-btn{font-size:.75rem;color:#94a3b8;background:none;border:none;cursor:pointer;font-family:'Golos Text',sans-serif;letter-spacing:.08em;text-transform:uppercase;transition:color .2s;padding:0;display:flex;align-items:center;gap:.35rem;}
                        <a href="tel:05346636464" className="pnav-icon" title="Telefon">📞</a>
                        <a href="mailto:zafer@zaferkaraca.net" className="pnav-icon" title="E-posta">✉</a>
                        <a href="https://zaferkaraca.net/#contacts-2-uSrJKocEPl" className="pnav-icon" title="Konum">📍</a>
                    </div>

                    <button className="pnav-toggle" onClick={() => setIsOpen(!isOpen)}>☰</button>
                </div>

                {isOpen && (
                    <div className="pnav-mobile">
                        <a href="https://zaferkaraca.net/#testimonials-8-uSrJKo6yl4">Hakkımızda</a>
                        <a href="https://postaci.zaferkaraca.net">Posta Hizmeti</a>
                        <a href="https://hobby.zaferkaraca.net">Hobby</a>
                        <a href="https://pentestone.zaferkaraca.net/">PentestOne</a>
                        <a href="https://cyber.zaferkaraca.net/">Cyber Security</a>
                        <a href="https://pdfoku.zaferkaraca.net/">PDF OKU</a>
                        <a href="https://zaferkaraca.net/#contacts-2-uSrJKocEPl">İletişim</a>
                    </div>
                )}
            </nav>
        </>
    );
                                    <img src="/assets/images/zk_logo.webp" alt="Logo" className="pnav-logo" />

export default Navbar;
