export default function Placeholder() {
  return (
    <div className="text-center py-16">
      <svg
        className="w-24 h-24 text-gray-300 mx-auto mb-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <h2 className="text-2xl font-semibold text-gray-900 mb-2">
        Search Coventry Research Publications
      </h2>
      <p className="text-gray-600 mb-6">
        Find publications, authors, and research topics from Coventry.
      </p>
      <div className="max-w-md mx-auto text-left bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-3">Search Tips:</h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="text-primary-600 mt-0.5">•</span>
            <span>Use specific keywords related to your research interest</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-600 mt-0.5">•</span>
            <span>Search by author name, publication title, or topic</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-600 mt-0.5">•</span>
            <span>Results are ranked by relevance using TF-IDF scoring</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
