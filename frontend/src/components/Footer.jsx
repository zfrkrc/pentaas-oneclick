import React from 'react';

const Footer = () => {
    return (
        <>
            <section data-bs-version="5.1" className="contacts02 map1 cid-uSrJKocEPl" id="contacts-2-uSrJKocEPl">
                <div className="container">
                    <div className="row justify-content-center">
                        <div className="col-12 content-head">
                            <div className="mbr-section-head mb-5">
                                <h3 className="mbr-section-title mbr-fonts-style align-center mb-0 display-2">
                                    <strong>Contact Information</strong>
                                </h3>
                            </div>
                        </div>
                    </div>
                    <div className="row justify-content-center">
                        <div className="card col-12 col-md-12 col-lg-6">
                            <div className="card-wrapper">
                                <div className="text-wrapper">
                                    <ul className="list mbr-fonts-style display-7">
                                        <li className="mbr-text item-wrap">
                                            Support: <a href="mailto:support@pentaas.com" className="text-black">support@pentaas.com</a>
                                        </li>
                                        <li className="mbr-text item-wrap">
                                            System Status: <span style={{ color: 'green' }}>Operational</span>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div className="col-md-12 col-lg-6">
                            <div className="text-wrapper">
                                <p className="mbr-text display-7">
                                    <strong>Pentaas OneClick</strong> is a comprehensive security tool designed for ease of use and automated pentesting.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section className="display-7" style={{ padding: '1rem', alignItems: 'center', justifyContent: 'center', display: 'flex', backgroundColor: '#f0f0f0' }}>
                <p style={{ margin: 0, textAlign: 'center' }} className="display-7">
                    © 2026 Pentaas Security. All Rights Reserved.
                </p>
            </section>
        </>
    );
};

export default Footer;
