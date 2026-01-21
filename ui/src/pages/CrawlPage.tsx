import CrawlManager from "../components/CrawlManager";

function CrawlPage() {
  return (
    <main className="max-w-7xl mx-auto grow px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Crawl Management
        </h1>
        <p className="text-gray-600">
          Trigger and monitor crawl jobs to update the publication database
        </p>
      </div>

      <CrawlManager />
    </main>
  );
}

export default CrawlPage;
