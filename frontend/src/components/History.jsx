import React, { useState, useEffect } from 'react';

function History() {
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchScans();
    }, []);

    const fetchScans = async () => {
        try {
            const res = await fetch('/api/scans');
            const data = await res.json();
            setScans(data.scans || []);
        } catch (err) {
            console.error("Failed to fetch scans", err);
        } finally {
            setLoading(false);
        }
    };

    const downloadReport = async (scanId, target) => {
        try {
            const res = await fetch(`/api/scan/${scanId}/results`);
            const data = await res.json();

            // Simple CSV generation (reused from App.jsx logic)
            const csvRows = [
                "PENTAAS ONECLICK - SCAN REPORT",
                "",
                "SCAN INFO",
                `Target,${data.target}`,
                `Mode,${data.scan_type}`,
                `Time,${new Date(data.timestamp).toLocaleString()}`,
                `Total Findings,${data.findings.length}`,
                "",
                "DETAILED FINDINGS",
                "ID,Title,Severity,Description"
            ];

            data.findings.forEach(f => {
                const desc = f.description ? f.description.replace(/(\r\n|\n|\r)/gm, " ").replace(/,/g, ";") : "";
                csvRows.push(`${f.id},${f.title},${f.severity},${desc}`);
            });

            const blob = new Blob([csvRows.join("\n")], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report_${target}_${scanId}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch (err) {
            alert("Rapor indirilemedi: " + err.message);
        }
    };

    return (
                                </div >
                            </div >

                        </div >
                    </div >
                </div >
            </section >
        <Footer />
        </>
    );
}

export default History;
