import React from 'react';

const Footer = () => {
    return (
        <>
            <style>{`
                .pfooter{background:#050508;border-top:1px solid rgba(0,212,255,.1);padding:1.5rem;display:flex;align-items:center;justify-content:center;font-family:'Inter',sans-serif;}
                .pfooter p{margin:0;font-size:.7rem;color:#475569;letter-spacing:.08em;}
                .pfooter span{color:#00D4FF;}
            `}</style>
            <footer className="pfooter">
                <p>© 2026 <span>Zafer Karaca</span> — All Rights Reserved</p>
            </footer>
        </>
    );
};

export default Footer;
