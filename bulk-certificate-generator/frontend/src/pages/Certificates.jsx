import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Search, Download, Eye, X } from 'lucide-react';
import { certificatesApi } from '../api/certificates';
import toast from 'react-hot-toast';

export default function Certificates() {
  const [certs, setCerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    const fetchCerts = async () => {
      try {
        const res = await certificatesApi.getCertificates(1, 100);
        setCerts(res.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchCerts();
  }, []);

  const handlePreview = (certId) => {
    setPreviewUrl(`${import.meta.env.VITE_API_BASE_URL}/api/v1/certificates/${certId}/download`);
  };

  const filtered = certs.filter(c => 
    c.recipient_name.toLowerCase().includes(search.toLowerCase()) || 
    c.recipient_email.toLowerCase().includes(search.toLowerCase()) ||
    c.certificate_code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="container-fluid py-2">
      <div className="mb-4">
        <h2 className="fw-bold mb-1">Certificates Library</h2>
        <p className="text-muted-custom mb-0">Search and view all generated certificates.</p>
      </div>

      <div className="surface overflow-hidden mb-5">
        <div className="p-4 border-bottom" style={{ borderColor: 'var(--border)' }}>
          <div className="position-relative" style={{ width: '100%', maxWidth: 400 }}>
            <Search size={18} className="position-absolute text-muted-custom" style={{ top: 11, left: 12 }} />
            <input type="text" className="form-control-custom ps-5" placeholder="Search by name, email, or code..."
                   value={search} onChange={e => setSearch(e.target.value)} />
          </div>
        </div>

        <div className="table-container">
          <table className="table-custom">
            <thead>
              <tr>
                <th>Code</th>
                <th>Recipient Name</th>
                <th>Email Address</th>
                <th>Status</th>
                <th className="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" className="text-center py-5">
                    <span className="spinner-border text-primary opacity-50" />
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center py-5 text-muted-custom">
                     <FileText size={48} className="mb-3 opacity-50 mx-auto" />
                     <p className="mb-0">No certificates found.</p>
                  </td>
                </tr>
              ) : (
                filtered.map(c => (
                  <tr key={c.id}>
                    <td className="font-monospace text-muted-custom small">{c.certificate_code}</td>
                    <td className="fw-medium">{c.recipient_name}</td>
                    <td className="text-muted-custom">{c.recipient_email}</td>
                    <td>
                      {c.status === 'COMPLETED' ? <span className="badge-custom badge-success">Generated</span> :
                       <span className="badge-custom badge-danger">Failed</span>}
                    </td>
                    <td className="text-end">
                      {c.status === 'COMPLETED' && (
                        <div className="d-flex justify-content-end gap-2">
                          <button onClick={() => handlePreview(c.id)} className="btn btn-sm btn-secondary-custom p-2" title="Preview PDF">
                            <Eye size={16} />
                          </button>
                          <a href={`${import.meta.env.VITE_API_BASE_URL}/api/v1/certificates/${c.id}/download`} 
                             target="_blank" rel="noreferrer"
                             className="btn btn-sm btn-primary-custom p-2" title="Download PDF">
                            <Download size={16} />
                          </a>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <AnimatePresence>
        {previewUrl && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center"
            style={{ backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1050, padding: 20 }}>
            
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="surface overflow-hidden d-flex flex-column"
              style={{ width: '100%', maxWidth: 900, height: '90vh' }}>
              
              <div className="p-3 border-bottom d-flex justify-content-between align-items-center bg-light" style={{ borderColor: 'var(--border)' }}>
                <h5 className="mb-0 fw-bold d-flex align-items-center"><FileText size={20} className="me-2 text-primary"/> Certificate Preview</h5>
                <button className="btn btn-link text-muted-custom p-0" onClick={() => setPreviewUrl(null)}>
                  <X size={24} />
                </button>
              </div>
              
              <div className="flex-grow-1 bg-secondary bg-opacity-10">
                <iframe src={previewUrl} className="w-100 h-100 border-0" title="PDF Preview"></iframe>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}