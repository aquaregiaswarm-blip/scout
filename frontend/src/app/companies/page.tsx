"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { CompanyProfile } from "@/lib/types";
import { companiesApi } from "@/lib/api";

export default function CompaniesPage() {
  const router = useRouter();
  const [companies, setCompanies] = useState<CompanyProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const response = await companiesApi.list();
        setCompanies(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load companies");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCompanies();
  }, []);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this company and all its research data?")) return;

    try {
      await companiesApi.delete(id);
      setCompanies((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete company");
    }
  };

  const filteredCompanies = companies.filter((c) =>
    c.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.industry?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="glass rounded-xl p-8 text-center">
          <div className="animate-pulse text-gray-400">Loading companies...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Companies</h1>
          <p className="text-gray-400 mt-1">
            {companies.length} {companies.length === 1 ? "company" : "companies"} researched
          </p>
        </div>
        <a
          href="/"
          className="px-4 py-2 rounded-lg bg-scout-primary text-white font-medium hover:opacity-90 transition-opacity"
        >
          + New Research
        </a>
      </div>

      {/* Search */}
      <div className="mb-6">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search companies..."
          className="w-full px-4 py-3 rounded-lg bg-void-800 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-scout-primary"
        />
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-500/20 text-red-400">
          {error}
        </div>
      )}

      {/* Companies List */}
      {filteredCompanies.length === 0 ? (
        <div className="glass rounded-xl p-12 text-center">
          <div className="text-6xl mb-4">🏢</div>
          <h2 className="text-xl font-semibold text-white mb-2">No companies yet</h2>
          <p className="text-gray-400 mb-6">Start researching a company to see it here</p>
          <a
            href="/"
            className="inline-block px-6 py-3 rounded-lg bg-scout-primary text-white font-medium hover:opacity-90 transition-opacity"
          >
            Start Research
          </a>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredCompanies.map((company) => (
            <div
              key={company.id}
              onClick={() => router.push(`/companies/${company.id}`)}
              className="glass rounded-xl p-6 hover:border-scout-primary/50 transition-colors cursor-pointer group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white group-hover:text-scout-primary transition-colors">
                    {company.company_name}
                  </h3>
                  {company.industry && (
                    <p className="text-gray-400 text-sm mt-1">{company.industry}</p>
                  )}
                </div>
                <div className="flex items-center gap-4">
                  {company.initiatives && company.initiatives.length > 0 && (
                    <span className="px-3 py-1 rounded-full bg-scout-primary/20 text-scout-primary text-sm">
                      {company.initiatives.length} {company.initiatives.length === 1 ? "initiative" : "initiatives"}
                    </span>
                  )}
                  <button
                    onClick={(e) => handleDelete(company.id, e)}
                    className="p-2 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
              
              {/* Initiatives preview */}
              {company.initiatives && company.initiatives.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="flex flex-wrap gap-2">
                    {company.initiatives.slice(0, 3).map((initiative) => (
                      <span
                        key={initiative.id}
                        className="px-3 py-1 rounded-full bg-white/5 text-gray-300 text-sm flex items-center gap-1"
                      >
                        {initiative.discovered_by_agent && (
                          <span className="text-scout-secondary">🤖</span>
                        )}
                        {initiative.name}
                      </span>
                    ))}
                    {company.initiatives.length > 3 && (
                      <span className="px-3 py-1 text-gray-500 text-sm">
                        +{company.initiatives.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              <p className="text-xs text-gray-500 mt-4">
                Last updated: {new Date(company.updated_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
