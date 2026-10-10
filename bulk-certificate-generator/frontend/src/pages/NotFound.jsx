import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="d-flex flex-column align-items-center justify-content-center h-100 py-5">
      <h1 className="display-1 fw-bold text-primary mb-3">404</h1>
      <h3 className="fw-bold mb-2">Page Not Found</h3>
      <p className="text-muted mb-4">The page you're looking for doesn't exist.</p>
      <Link to="/" className="btn btn-primary-custom">Go to Dashboard</Link>
    </div>
  );
}