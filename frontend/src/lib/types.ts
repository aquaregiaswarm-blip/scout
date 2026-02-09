/**
 * Shared TypeScript types for Scout.
 * Keep in sync with backend Pydantic models.
 */

// Enums
export type ResearchStatus = 
  | "pending"
  | "running" 
  | "completed"
  | "stopped"
  | "failed";

export type PathStatus =
  | "active"
  | "completed"
  | "stopped"
  | "exhausted"
  | "error";

export type FindingCategory =
  | "people"
  | "initiative"
  | "technology"
  | "competitive"
  | "financial"
  | "market";

export type ConfidenceLevel =
  | "none"
  | "low"
  | "medium"
  | "high"
  | "sufficient";

// Core entities
export interface Team {
  id: string;
  name: string;
  created_at: string;
}

export interface User {
  id: string;
  team_id: string;
  name: string;
  email: string;
  created_at: string;
}

export interface CompanyProfile {
  id: string;
  team_id: string;
  company_name: string;
  industry?: string;
  created_at: string;
  updated_at: string;
  initiatives?: Initiative[];
}

export interface Initiative {
  id: string;
  company_profile_id: string;
  name: string;
  description?: string;
  discovered_by_agent: boolean;
  created_at: string;
  updated_at: string;
}

export interface ResearchSession {
  id: string;
  initiative_id: string;
  triggered_by: string;
  status: ResearchStatus;
  follow_up_question?: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface ResearchCycle {
  id: string;
  research_session_id: string;
  cycle_number: number;
  prime_agent_plan?: Record<string, unknown>;
  confidence_assessment?: ConfidenceAssessment;
  started_at: string;
  completed_at?: string;
}

export interface ResearchPath {
  id: string;
  research_cycle_id: string;
  assignment_id: string;
  topic: string;
  instructions?: string;
  status: PathStatus;
  reasoning?: string;
  tools_used: number;
  started_at: string;
  completed_at?: string;
}

export interface ResearchFinding {
  id: string;
  research_path_id: string;
  initiative_id: string;
  category: FindingCategory;
  content: Record<string, unknown>;
  source_url?: string;
  source_type?: string;
  confidence_score: number;
  created_at: string;
}

export interface ConfidenceAssessment {
  people: ConfidenceLevel;
  initiative: ConfidenceLevel;
  technology: ConfidenceLevel;
  competitive: ConfidenceLevel;
  financial: ConfidenceLevel;
  market: ConfidenceLevel;
}

export interface DashboardContent {
  id: string;
  initiative_id: string;
  content: {
    people?: CategoryContent;
    initiative?: CategoryContent;
    technology?: CategoryContent;
    competitive?: CategoryContent;
    financial?: CategoryContent;
    market?: CategoryContent;
  };
  portfolio_recommendations?: PortfolioRecommendation[];
  created_at: string;
  updated_at: string;
}

export interface CategoryContent {
  summary: string;
  findings: ResearchFinding[];
  insights?: string[];
  confidence: ConfidenceLevel;
}

export interface PortfolioItem {
  id: string;
  team_id: string;
  vendor_name: string;
  partnership_level?: string;
  capabilities?: string[];
  created_at: string;
  updated_at: string;
}

export interface PortfolioRecommendation {
  vendor: string;
  capability: string;
  relevance: string;
  supporting_findings: string[];
}

// API Request/Response types
export interface StartResearchRequest {
  company_name: string;
  industry?: string;
  initiative_description: string;
}

export interface StartResearchResponse {
  session_id: string;
  status: ResearchStatus;
  initiative_id: string;
}

export interface FollowUpRequest {
  question: string;
}

// SSE Event types
export type SSEEventType =
  | "cycle_started"
  | "subagent_started"
  | "subagent_completed"
  | "subagent_stopped"
  | "synthesis_complete"
  | "findings_updated"
  | "initiative_discovered"
  | "research_complete"
  | "error";

export interface SSEEvent {
  type: SSEEventType;
  timestamp: string;
  session_id: string;
  data: Record<string, unknown>;
}

export interface CycleStartedEvent extends SSEEvent {
  type: "cycle_started";
  data: {
    cycle_number: number;
    plan_summary: string;
  };
}

export interface SubagentStartedEvent extends SSEEvent {
  type: "subagent_started";
  data: {
    path_id: string;
    topic: string;
    priority: string;
  };
}

export interface SubagentCompletedEvent extends SSEEvent {
  type: "subagent_completed";
  data: {
    path_id: string;
    topic: string;
    findings_count: number;
    tangential_signals?: string[];
  };
}

export interface FindingsUpdatedEvent extends SSEEvent {
  type: "findings_updated";
  data: {
    dashboard_content: DashboardContent;
  };
}

export interface ResearchCompleteEvent extends SSEEvent {
  type: "research_complete";
  data: {
    total_cycles: number;
    total_findings: number;
    final_confidence: ConfidenceAssessment;
  };
}

export interface InitiativeDiscoveredEvent extends SSEEvent {
  type: "initiative_discovered";
  data: {
    initiative_name: string;
    description: string;
    evidence: string[];
  };
}
