function AboutPage() {
  return (
    <main className="max-w-7xl mx-auto grow px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          About This Search Engine
        </h1>

        <div className="prose prose-lg max-w-none">
          <p className="text-gray-700 mb-4">
            This is a custom search engine built for Coventry University
            research publications.
          </p>

          <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-3">
            Features
          </h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            <li>Web crawler with robots.txt compliance</li>
            <li>Inverted index with TF weighting</li>
            <li>Cosine similarity ranking</li>
            <li>MongoDB backend storage</li>
            <li>Fast and efficient search results</li>
          </ul>

          <h2 className="text-2xl font-semibold text-gray-900 mt-6 mb-3">
            Technology Stack
          </h2>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            <li>
              <strong>Frontend:</strong> React, TypeScript, Tailwind CSS
            </li>
            <li>
              <strong>Backend:</strong> Python, FastAPI
            </li>
            <li>
              <strong>Database:</strong> MongoDB
            </li>
            <li>
              <strong>Search:</strong> Custom inverted index implementation
            </li>
          </ul>
        </div>
      </div>
    </main>
  );
}

export default AboutPage;
