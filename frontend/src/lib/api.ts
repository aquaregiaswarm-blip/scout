/**
 * Typed API client for Scout backend.
 */

import type {
  StartResearchRequest,
  StartResearchResponse,
  ResearchSession,
  CompanyProfile,
  Initiative,
  PortfolioItem,
  DashboardContent,
  FollowUpRequest,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Unknown error" }));
    throw new ApiError(response.status, error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

// Research API
export const researchApi = {
  start: (data: StartResearchRequest): Promise<StartResearchResponse> =>
    request("/research/start", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  get: (sessionId: string): Promise<ResearchSession> =>
    request(`/research/${sessionId}`),

  stop: (sessionId: string): Promise<void> =>
    request(`/research/${sessionId}/stop`, { method: "POST" }),

  stopPath: (sessionId: string, pathId: string): Promise<void> =>
    request(`/research/${sessionId}/paths/${pathId}/stop`, { method: "POST" }),

  followUp: (sessionId: string, data: FollowUpRequest): Promise<StartResearchResponse> =>
    request(`/research/${sessionId}/follow-up`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getDashboard: (initiativeId: string): Promise<DashboardContent> =>
    request(`/initiatives/${initiativeId}/dashboard`),
};

// Companies API
export const companiesApi = {
  list: (offset = 0, limit = 20): Promise<{ data: CompanyProfile[]; total: number }> =>
    request(`/companies?offset=${offset}&limit=${limit}`),

  get: (id: string): Promise<CompanyProfile> =>
    request(`/companies/${id}`),

  getInitiatives: (companyId: string): Promise<Initiative[]> =>
    request(`/companies/${companyId}/initiatives`),

  delete: (id: string): Promise<void> =>
    request(`/companies/${id}`, { method: "DELETE" }),

  refreshInitiative: (companyId: string, initiativeId: string): Promise<StartResearchResponse> =>
    request(`/companies/${companyId}/initiatives/${initiativeId}/refresh`, { method: "POST" }),
};

// Portfolio API
export const portfolioApi = {
  list: (): Promise<PortfolioItem[]> =>
    request("/portfolio"),

  create: (data: Omit<PortfolioItem, "id" | "team_id" | "created_at" | "updated_at">): Promise<PortfolioItem> =>
    request("/portfolio", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: string, data: Partial<PortfolioItem>): Promise<PortfolioItem> =>
    request(`/portfolio/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: string): Promise<void> =>
    request(`/portfolio/${id}`, { method: "DELETE" }),

  bulkImport: (items: Array<Omit<PortfolioItem, "id" | "team_id" | "created_at" | "updated_at">>): Promise<PortfolioItem[]> =>
    request("/portfolio/bulk", {
      method: "POST",
      body: JSON.stringify(items),
    }),
};

// Auth API (placeholder)
export const authApi = {
  login: (email: string, password: string): Promise<{ token: string; user: { id: string; name: string; email: string } }> =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  register: (data: { name: string; email: string; password: string; team_name: string }): Promise<{ token: string; user: { id: string; name: string; email: string } }> =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  me: (token: string): Promise<{ id: string; name: string; email: string; team_id: string }> =>
    request("/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    }),
};
