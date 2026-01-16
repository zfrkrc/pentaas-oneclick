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
            if (!res.ok) throw new Error("API call failed");
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
            if (!res.ok) throw new Error("API call failed");
            const data = await res.json();

            // Simple CSV generation
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

            if (data.findings) {
                data.findings.forEach(f => {
                    const desc = f.description ? f.description.replace(/(\r\n|\n|\r)/gm, " ").replace(/,/g, ";") : "";
                    csvRows.push(`${f.id},${f.title},${f.severity},${desc}`);
                });
            }

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
        <div className="card shadow-sm">
            <div className="card-body p-0">
                <h4 className="p-3 mb-0 bg-light border-bottom">Scan History</h4>
                <div className="table-responsive">
                    <table className="table table-hover mb-0">
                        <thead className="bg-light">
                            <tr>
                                <th className="p-3">Date</th>
                                <th className="p-3">Target</th>
                                <th className="p-3">Type</th>
                                <th className="p-3">Status</th>
                                <th className="p-3 text-end">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan="5" className="text-center p-4">Loading...</td></tr>
                            ) : scans.length === 0 ? (
                                <tr><td colSpan="5" className="text-center p-4">No scans found.</td></tr>
                            ) : (
                                scans.map(scan => (
                                    <tr key={scan.scan_id}>
                                        <td className="p-3">{new Date(scan.timestamp).toLocaleString()}</td>
                                        <td className="p-3 fw-bold">{scan.target}</td>
                                        <td className="p-3">
                                            <span className={`badge ${scan.scan_type === 'white' ? 'bg-info' : scan.scan_type === 'gray' ? 'bg-secondary' : 'bg-dark'}`}>
                                                {scan.scan_type.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="p-3">
                                            <span className={`badge ${scan.status === 'completed' ? 'bg-success' : scan.status === 'running' ? 'bg-warning' : 'bg-danger'}`}>
                                                {scan.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="p-3 text-end">
                                            <button
                                                className="btn btn-sm btn-primary"
                                                onClick={() => downloadReport(scan.scan_id, scan.target)}
                                            >
                                                Download CSV
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default History;
