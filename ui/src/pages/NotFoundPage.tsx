import { Link } from "react-router-dom";

function NotFoundPage() {
  return (
    <main className="max-w-7xl mx-auto grow px-4 sm:px-6 lg:px-8 py-8 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
        <p className="text-2xl text-gray-600 mb-8">Page Not Found</p>
        <p className="text-gray-500 mb-8">
          The page you're looking for doesn't exist.
        </p>
        <Link
          to="/"
          className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Go Home
        </Link>
      </div>
    </main>
  );
}

export default NotFoundPage;
