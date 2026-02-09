"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import type {
  ResearchSession,
  DashboardContent,
  SSEEvent,
  ConfidenceLevel,
  FindingCategory,
} from "@/lib/types";
import { researchApi } from "@/lib/api";

// Confidence level to color/width mapping
const confidenceConfig: Record<ConfidenceLevel, { color: string; width: string; label: string }> = {
  none: { color: "bg-gray-600", width: "w-0", label: "None" },
  low: { color: "bg-red-500", width: "w-1/4", label: "Low" },
  medium: { color: "bg-yellow-500", width: "w-1/2", label: "Medium" },
  high: { color: "bg-green-400", width: "w-3/4", label: "High" },
  sufficient: { color: "bg-scout-primary", width: "w-full", label: "Sufficient" },
};

// Category display config
const categoryConfig: Record<FindingCategory, { icon: string; label: string }> = {
  people: { icon: "👥", label: "Key People" },
  initiative: { icon: "🎯", label: "Initiative Details" },
  technology: { icon: "⚙️", label: "Technology Stack" },
  competitive: { icon: "⚔️", label: "Competitive Intel" },
  financial: { icon: "💰", label: "Financial Signals" },
  market: { icon: "📊", label: "Market Context" },
};

interface ActivityLogEntry {
  id: string;
  type: string;
  message: string;
  timestamp: Date;
}

export default function ResearchSessionPage() {
  const params = useParams();
  const sessionId = params.id as string;

  const [session, setSession] = useState<ResearchSession | null>(null);
  const [dashboard, setDashboard] = useState<DashboardContent | null>(null);
  const [activityLog, setActivityLog] = useState<ActivityLogEntry[]>([]);
  const [activePaths, setActivePaths] = useState<Map<string, { topic: string; startedAt: Date }>>(new Map());
  const [error, setError] = useState<string | null>(null);
  const [followUpQuestion, setFollowUpQuestion] = useState("");
  const [isSubmittingFollowUp, setIsSubmittingFollowUp] = useState(false);

  const eventSourceRef = useRef<EventSource | null>(null);
  const activityLogRef = useRef<HTMLDivElement>(null);

  // Auto-scroll activity log
  useEffect(() => {
    if (activityLogRef.current) {
      activityLogRef.current.scrollTop = activityLogRef.current.scrollHeight;
    }
  }, [activityLog]);

  // Fetch initial session data
  useEffect(() => {
    const fetchSession = async () => {
      try {
        const data = await researchApi.get(sessionId);
        setSession(data);

        if (data.status === "completed" || data.status === "stopped") {
          // Fetch final dashboard
          const dashboardData = await researchApi.getDashboard(data.initiative_id);
          setDashboard(dashboardData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load session");
      }
    };

    fetchSession();
  }, [sessionId]);

  // Set up SSE connection for live updates
  useEffect(() => {
    if (!session || session.status === "completed" || session.status === "stopped" || session.status === "failed") {
      return;
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    const eventSource = new EventSource(`${apiUrl}/research/${sessionId}/stream`);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const sseEvent: SSEEvent = JSON.parse(event.data);
        handleSSEEvent(sseEvent);
      } catch (err) {
        console.error("Failed to parse SSE event:", err);
      }
    };

    eventSource.onerror = () => {
      console.error("SSE connection error");
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [session?.status, sessionId]);

  const handleSSEEvent = (event: SSEEvent) => {
    const logEntry: ActivityLogEntry = {
      id: `${event.type}-${Date.now()}`,
      type: event.type,
      message: formatEventMessage(event),
      timestamp: new Date(event.timestamp),
    };
    setActivityLog((prev) => [...prev, logEntry]);

    switch (event.type) {
      case "cycle_started":
        // Nothing special, just log
        break;

      case "subagent_started":
        const startData = event.data as { path_id: string; topic: string };
        setActivePaths((prev) => {
          const next = new Map(prev);
          next.set(startData.path_id, { topic: startData.topic, startedAt: new Date() });
          return next;
        });
        break;

      case "subagent_completed":
      case "subagent_stopped":
        const endData = event.data as { path_id: string };
        setActivePaths((prev) => {
          const next = new Map(prev);
          next.delete(endData.path_id);
          return next;
        });
        break;

      case "findings_updated":
        const findingsData = event.data as { dashboard_content: DashboardContent };
        setDashboard(findingsData.dashboard_content);
        break;

      case "research_complete":
        setSession((prev) => prev ? { ...prev, status: "completed" } : prev);
        break;

      case "error":
        const errorData = event.data as { message: string };
        setError(errorData.message);
        break;

      case "initiative_discovered":
        // Could show a notification
        break;
    }
  };

  const formatEventMessage = (event: SSEEvent): string => {
    switch (event.type) {
      case "cycle_started":
        return `🔄 Starting cycle ${(event.data as { cycle_number: number }).cycle_number}`;
      case "subagent_started":
        return `🔍 Researching: ${(event.data as { topic: string }).topic}`;
      case "subagent_completed":
        return `✅ Completed: ${(event.data as { topic: string; findings_count: number }).topic} (${(event.data as { findings_count: number }).findings_count} findings)`;
      case "subagent_stopped":
        return `⏹️ Stopped: ${(event.data as { topic: string }).topic}`;
      case "synthesis_complete":
        return "🧪 Synthesis complete - dashboard updated";
      case "findings_updated":
        return "📊 Dashboard updated with new findings";
      case "initiative_discovered":
        return `💡 Discovered initiative: ${(event.data as { initiative_name: string }).initiative_name}`;
      case "research_complete":
        return "🎉 Research complete!";
      case "error":
        return `❌ Error: ${(event.data as { message: string }).message}`;
      default:
        return event.type;
    }
  };

  const handleStopResearch = async () => {
    try {
      await researchApi.stop(sessionId);
      setSession((prev) => prev ? { ...prev, status: "stopped" } : prev);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to stop research");
    }
  };

  const handleFollowUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!followUpQuestion.trim() || !session) return;

    setIsSubmittingFollowUp(true);
    try {
      await researchApi.followUp(sessionId, { question: followUpQuestion });
      setFollowUpQuestion("");
      setSession((prev) => prev ? { ...prev, status: "running" } : prev);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit follow-up");
    } finally {
      setIsSubmittingFollowUp(false);
    }
  };

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="glass rounded-xl p-8 text-center">
          <p className="text-red-400 text-lg">Error: {error}</p>
          <a href="/" className="mt-4 inline-block text-scout-primary hover:underline">
            ← Start new research
          </a>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="glass rounded-xl p-8 text-center">
          <div className="animate-pulse text-gray-400">Loading session...</div>
        </div>
      </div>
    );
  }

  const isActive = session.status === "running" || session.status === "pending";

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Research Session</h1>
          <p className="text-gray-400 text-sm mt-1">
            Session ID: {sessionId.slice(0, 8)}...
          </p>
        </div>
        <div className="flex items-center gap-4">
          <StatusBadge status={session.status} />
          {isActive && (
            <button
              onClick={handleStopResearch}
              className="px-4 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
            >
              Stop Research
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Dashboard - 2 columns */}
        <div className="lg:col-span-2 space-y-6">
          {/* Active Paths */}
          {activePaths.size > 0 && (
            <div className="glass rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="animate-pulse">🔍</span> Active Research
              </h2>
              <div className="space-y-3">
                {Array.from(activePaths.entries()).map(([pathId, { topic }]) => (
                  <div key={pathId} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                    <span className="text-gray-300">{topic}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-scout-primary animate-pulse" />
                      <button
                        onClick={() => researchApi.stopPath(sessionId, pathId)}
                        className="text-xs text-gray-500 hover:text-red-400 transition-colors"
                      >
                        Stop
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dashboard Categories */}
          {dashboard ? (
            <div className="space-y-4">
              {(Object.keys(categoryConfig) as FindingCategory[]).map((category) => {
                const content = dashboard.content[category];
                const config = categoryConfig[category];
                const confidence = content?.confidence || "none";
                const confConfig = confidenceConfig[confidence];

                return (
                  <div key={category} className="glass rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                        <span>{config.icon}</span>
                        {config.label}
                      </h3>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-500">{confConfig.label}</span>
                        <div className="w-20 h-2 rounded-full bg-white/10 overflow-hidden">
                          <div className={`h-full ${confConfig.color} ${confConfig.width} transition-all duration-500`} />
                        </div>
                      </div>
                    </div>

                    {content?.summary ? (
                      <p className="text-gray-300 leading-relaxed">{content.summary}</p>
                    ) : (
                      <p className="text-gray-500 italic">No findings yet...</p>
                    )}

                    {content?.insights && content.insights.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-white/10">
                        <p className="text-sm text-gray-400 mb-2">Key Insights:</p>
                        <ul className="space-y-1">
                          {content.insights.map((insight, i) => (
                            <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                              <span className="text-scout-primary">•</span>
                              {insight}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Portfolio Recommendations */}
              {dashboard.portfolio_recommendations && dashboard.portfolio_recommendations.length > 0 && (
                <div className="glass rounded-xl p-6 glow-indigo">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                    <span>💼</span> Portfolio Recommendations
                  </h3>
                  <div className="space-y-4">
                    {dashboard.portfolio_recommendations.map((rec, i) => (
                      <div key={i} className="p-4 rounded-lg bg-white/5">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-scout-primary">{rec.vendor}</span>
                          <span className="text-sm text-gray-400">{rec.capability}</span>
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
              <div className="animate-pulse text-gray-400">
                {isActive ? "Waiting for research findings..." : "No dashboard data available"}
              </div>
            </div>
          )}

          {/* Follow-up Question (when research complete) */}
          {session.status === "completed" && (
            <form onSubmit={handleFollowUp} className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Ask a Follow-up Question</h3>
              <div className="flex gap-4">
                <input
                  type="text"
                  value={followUpQuestion}
                  onChange={(e) => setFollowUpQuestion(e.target.value)}
                  placeholder="What else would you like to know?"
                  className="flex-1 px-4 py-3 rounded-lg bg-void-800 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-scout-primary"
                />
                <button
                  type="submit"
                  disabled={isSubmittingFollowUp || !followUpQuestion.trim()}
                  className="px-6 py-3 rounded-lg bg-scout-primary text-white font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                >
                  {isSubmittingFollowUp ? "..." : "Ask"}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Activity Log - 1 column */}
        <div className="lg:col-span-1">
          <div className="glass rounded-xl p-6 sticky top-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <span>📋</span> Activity Log
            </h2>
            <div
              ref={activityLogRef}
              className="h-[500px] overflow-y-auto space-y-2 text-sm"
            >
              {activityLog.length === 0 ? (
                <p className="text-gray-500 italic">Waiting for events...</p>
              ) : (
                activityLog.map((entry) => (
                  <div key={entry.id} className="p-2 rounded-lg bg-white/5">
                    <p className="text-gray-300">{entry.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {entry.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    pending: { bg: "bg-yellow-500/20", text: "text-yellow-400", label: "Pending" },
    running: { bg: "bg-blue-500/20", text: "text-blue-400", label: "Running" },
    completed: { bg: "bg-green-500/20", text: "text-green-400", label: "Completed" },
    stopped: { bg: "bg-gray-500/20", text: "text-gray-400", label: "Stopped" },
    failed: { bg: "bg-red-500/20", text: "text-red-400", label: "Failed" },
  };

  const c = config[status] || config.pending;

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${c.bg} ${c.text}`}>
      {c.label}
    </span>
  );
}
