import React from "react";

import { getStatistics } from "../services/api";

import type { StatsResponse } from "../types/api";

export default function Header() {
  const [stats, setStats] = React.useState<StatsResponse | null>(null);

  const loadStatistics = async () => {
    try {
      const data = await getStatistics();
      setStats(data);
    } catch (err: unknown) {
      console.error("Failed to load statistics:", err);
    }
  };

  React.useEffect(() => {
    loadStatistics();
  }, []);

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 shrink-0">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Coventry Research
              </h1>
              <p className="text-sm text-gray-600">
                Publications Search Engine
              </p>
            </div>
          </div>

          {stats && (
            <div className="hidden md:flex items-center gap-6 text-sm">
              <div className="text-center">
                <div className="font-semibold text-gray-900">
                  {stats.total_publications?.toLocaleString() || 0}
                </div>
                <div className="text-gray-600">Publications</div>
              </div>
              <div className="text-center">
                <div className="font-semibold text-gray-900">
                  {stats.total_authors?.toLocaleString() || 0}
                </div>
                <div className="text-gray-600">Authors</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
