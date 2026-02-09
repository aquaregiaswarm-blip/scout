"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    companyName: "",
    industry: "",
    initiative: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/research/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: formData.companyName,
          industry: formData.industry,
          initiative_description: formData.initiative,
        }),
      });

      if (!response.ok) throw new Error("Failed to start research");

      const data = await response.json();
      router.push(`/research/${data.session_id}`);
    } catch (error) {
      console.error("Error starting research:", error);
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          <span className="text-scout-primary">New</span>{" "}
          <span className="text-white">Research</span>
        </h1>
        <p className="text-gray-400">
          Enter a company and initiative to start AI-powered research
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Company Name */}
        <div>
          <label htmlFor="companyName" className="block text-sm font-medium text-gray-300 mb-2">
            Company Name <span className="text-red-400">*</span>
          </label>
          <input
            id="companyName"
            type="text"
            required
            value={formData.companyName}
            onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
            placeholder="e.g., Acme Corporation"
            className="w-full px-4 py-3 rounded-lg bg-void-800 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-scout-primary focus:border-transparent"
          />
        </div>

        {/* Industry */}
        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-gray-300 mb-2">
            Industry
          </label>
          <input
            id="industry"
            type="text"
            value={formData.industry}
            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            placeholder="e.g., Manufacturing, Healthcare, Financial Services"
            className="w-full px-4 py-3 rounded-lg bg-void-800 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-scout-primary focus:border-transparent"
          />
        </div>

        {/* Initiative */}
        <div>
          <label htmlFor="initiative" className="block text-sm font-medium text-gray-300 mb-2">
            Project or Initiative <span className="text-red-400">*</span>
          </label>
          <textarea
            id="initiative"
            required
            rows={4}
            value={formData.initiative}
            onChange={(e) => setFormData({ ...formData, initiative: e.target.value })}
            placeholder="What are you trying to learn about? Can be vague — e.g., 'I heard they're doing something with cloud' or 'data modernization efforts'"
            className="w-full px-4 py-3 rounded-lg bg-void-800 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-scout-primary focus:border-transparent resize-none"
          />
          <p className="mt-2 text-sm text-gray-500">
            Scout will research this topic and discover related initiatives
          </p>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-4 rounded-lg bg-gradient-to-r from-scout-primary to-scout-secondary text-white font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Starting Research...
            </span>
          ) : (
            "Start Research"
          )}
        </button>
      </form>

      {/* Recent companies placeholder */}
      <div className="mt-16">
        <h2 className="text-lg font-semibold text-gray-300 mb-4">Recent Companies</h2>
        <div className="glass rounded-xl p-8 text-center text-gray-500">
          <p>No research history yet</p>
          <p className="text-sm mt-1">Your recent company profiles will appear here</p>
        </div>
      </div>
    </div>
  );
}
