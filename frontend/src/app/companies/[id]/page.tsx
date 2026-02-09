"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import type { CompanyProfile, Initiative, DashboardContent } from "@/lib/types";
import { companiesApi, researchApi } from "@/lib/api";

export default function CompanyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const companyId = params.id as string;

  const [company, setCompany] = useState<CompanyProfile | null>(null);
  const [initiatives, setInitiatives] = useState<Initiative[]>([]);
  const [selectedInitiative, setSelectedInitiative] = useState<Initiative | null>(null);
  const [dashboard, setDashboard] = useState<DashboardContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCompany = async () => {
      try {
        const [companyData, initiativesData] = await Promise.all([
          companiesApi.get(companyId),
          companiesApi.getInitiatives(companyId),
        ]);
        setCompany(companyData);
        setInitiatives(initiativesData);

        // Auto-select first initiative
        if (initiativesData.length > 0) {
          setSelectedInitiative(initiativesData[0]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load company");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCompany();
  }, [companyId]);

  // Fetch dashboard when initiative changes
  useEffect(() => {
    if (!selectedInitiative) {
      setDashboard(null);
      return;
    }

    const fetchDashboard = async () => {
      try {
        const dashboardData = await researchApi.getDashboard(selectedInitiative.id);
        setDashboard(dashboardData);
      } catch (err) {
        console.error("Failed to load dashboard:", err);
        setDashboard(null);
      }
    };

    fetchDashboard();
  }, [selectedInitiative?.id]);

  const handleRefreshInitiative = async () => {
    if (!company || !selectedInitiative) return;

    setIsRefreshing(true);
    try {
      const response = await companiesApi.refreshInitiative(company.id, selectedInitiative.id);
      router.push(`/research/${response.session_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start refresh");
    } finally {
      setIsRefreshing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="glass rounded-xl p-8 text-center">
          <div className="animate-pulse text-gray-400">Loading company...</div>
        </div>
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="glass rounded-xl p-8 text-center">
          <p className="text-red-400">{error || "Company not found"}</p>
          <a href="/companies" className="mt-4 inline-block text-scout-primary hover:underline">
            ← Back to companies
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <a href="/companies" className="text-gray-400 hover:text-white text-sm mb-2 inline-block">
            ← Back to companies
          </a>
          <h1 className="text-3xl font-bold text-white">{company.company_name}</h1>
          {company.industry && (
            <p className="text-gray-400 mt-1">{company.industry}</p>
          )}
        </div>
        <div className="flex items-center gap-3">
          {selectedInitiative && (
            <button
              onClick={handleRefreshInitiative}
              disabled={isRefreshing}
              className="px-4 py-2 rounded-lg bg-scout-primary/20 text-scout-primary hover:bg-scout-primary/30 transition-colors disabled:opacity-50"
            >
              {isRefreshing ? "Starting..." : "🔄 Refresh Research"}
            </button>
          )}
          <a
            href={`/?company=${encodeURIComponent(company.company_name)}`}
            className="px-4 py-2 rounded-lg bg-scout-primary text-white font-medium hover:opacity-90 transition-opacity"
          >
            + New Initiative
          </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Initiatives sidebar */}
        <div className="lg:col-span-1">
          <div className="glass rounded-xl p-4">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
              Initiatives
            </h2>
            {initiatives.length === 0 ? (
              <p className="text-gray-500 text-sm">No initiatives yet</p>
            ) : (
              <div className="space-y-2">
                {initiatives.map((initiative) => (
                  <button
                    key={initiative.id}
                    onClick={() => setSelectedInitiative(initiative)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedInitiative?.id === initiative.id
                        ? "bg-scout-primary/20 text-scout-primary"
                        : "hover:bg-white/5 text-gray-300"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {initiative.discovered_by_agent && (
                        <span className="text-scout-secondary text-xs">🤖</span>
                      )}
                      <span className="font-medium truncate">{initiative.name}</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(initiative.updated_at).toLocaleDateString()}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Dashboard content */}
        <div className="lg:col-span-3">
          {selectedInitiative ? (
            <div className="space-y-6">
              {/* Initiative header */}
              <div className="glass rounded-xl p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                      {selectedInitiative.discovered_by_agent && (
                        <span className="text-scout-secondary" title="Discovered by AI">🤖</span>
                      )}
                      {selectedInitiative.name}
                    </h2>
                    {selectedInitiative.description && (
                      <p className="text-gray-400 mt-2">{selectedInitiative.description}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Dashboard categories */}
              {dashboard?.content ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(dashboard.content).map(([category, content]) => {
                    if (!content) return null;
                    
                    const icons: Record<string, string> = {
                      people: "👥",
                      initiative: "🎯",
                      technology: "⚙️",
                      competitive: "⚔️",
                      financial: "💰",
                      market: "📊",
                    };

                    return (
                      <div key={category} className="glass rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-3">
                          <span>{icons[category] || "📋"}</span>
                          {category.charAt(0).toUpperCase() + category.slice(1)}
                        </h3>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {content.summary || "No data available"}
                        </p>
                        {content.insights && content.insights.length > 0 && (
                          <ul className="mt-3 space-y-1">
                            {content.insights.slice(0, 3).map((insight, i) => (
                              <li key={i} className="text-xs text-gray-400 flex items-start gap-1">
                                <span className="text-scout-primary">•</span>
                                {insight}
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="glass rounded-xl p-12 text-center">
                  <p className="text-gray-400">No research data available for this initiative</p>
                  <button
                    onClick={handleRefreshInitiative}
                    disabled={isRefreshing}
                    className="mt-4 px-6 py-3 rounded-lg bg-scout-primary text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                  >
                    {isRefreshing ? "Starting..." : "Start Research"}
                  </button>
                </div>
              )}

              {/* Portfolio recommendations */}
              {dashboard?.portfolio_recommendations && dashboard.portfolio_recommendations.length > 0 && (
                <div className="glass rounded-xl p-6 glow-indigo">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                    <span>💼</span> Portfolio Recommendations
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {dashboard.portfolio_recommendations.map((rec, i) => (
                      <div key={i} className="p-4 rounded-lg bg-white/5">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-scout-primary">{rec.vendor}</span>
                          <span className="text-xs text-gray-400">{rec.capability}</span>
                        </div>
                        <p className="text-gray-300 text-sm">{rec.relevance}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="glass rounded-xl p-12 text-center">
              <p className="text-gray-400">Select an initiative to view its research</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
