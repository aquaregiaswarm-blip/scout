"use client";

import { useEffect, useState } from "react";
import type { PortfolioItem } from "@/lib/types";
import { portfolioApi } from "@/lib/api";

interface NewVendorForm {
  vendor_name: string;
  partnership_level: string;
  capabilities: string;
}

export default function PortfolioPage() {
  const [items, setItems] = useState<PortfolioItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<NewVendorForm>({
    vendor_name: "",
    partnership_level: "",
    capabilities: "",
  });

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const fetchPortfolio = async () => {
    try {
      const data = await portfolioApi.list();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load portfolio");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const payload = {
      vendor_name: formData.vendor_name,
      partnership_level: formData.partnership_level || undefined,
      capabilities: formData.capabilities
        ? formData.capabilities.split(",").map((c) => c.trim()).filter(Boolean)
        : undefined,
    };

    try {
      if (editingId) {
        const updated = await portfolioApi.update(editingId, payload);
        setItems((prev) => prev.map((item) => (item.id === editingId ? updated : item)));
        setEditingId(null);
      } else {
        const created = await portfolioApi.create(payload);
        setItems((prev) => [...prev, created]);
      }
      setShowAddForm(false);
      setFormData({ vendor_name: "", partnership_level: "", capabilities: "" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save vendor");
    }
  };

  const handleEdit = (item: PortfolioItem) => {
    setFormData({
      vendor_name: item.vendor_name,
      partnership_level: item.partnership_level || "",
      capabilities: item.capabilities?.join(", ") || "",
    });
    setEditingId(item.id);
    setShowAddForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this vendor from your portfolio?")) return;

    try {
      await portfolioApi.delete(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete vendor");
    }
  };

  const handleCancel = () => {
    setShowAddForm(false);
    setEditingId(null);
    setFormData({ vendor_name: "", partnership_level: "", capabilities: "" });
  };

  // Group items by partnership level
  const groupedItems = items.reduce((acc, item) => {
    const level = item.partnership_level || "Other";
    if (!acc[level]) acc[level] = [];
    acc[level].push(item);
    return acc;
  }, {} as Record<string, PortfolioItem[]>);

  const levelOrder = ["Elite", "Premier", "Partner", "Authorized", "Other"];
  const sortedLevels = Object.keys(groupedItems).sort(
    (a, b) => levelOrder.indexOf(a) - levelOrder.indexOf(b)
  );

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="glass rounded-xl p-8 text-center">
          <div className="animate-pulse text-gray-400">Loading portfolio...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">Partner Portfolio</h1>
          <p className="text-gray-400 mt-1">
            {items.length} {items.length === 1 ? "vendor" : "vendors"} in your portfolio
          </p>
        </div>
        <button
          onClick={() => setShowAddForm(true)}
          className="px-4 py-2 rounded-lg bg-scout-primary text-white font-medium hover:opacity-90 transition-opacity"
        >
          + Add Vendor
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-500/20 text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-2 text-red-300">×</button>
        </div>
      )}

      {/* Add/Edit Form */}
      {showAddForm && (
        <div className="glass rounded-xl p-6 mb-8">
          <h2 className="text-lg font-semibold text-white mb-4">
            {editingId ? "Edit Vendor" : "Add New Vendor"}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Vendor Name <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.vendor_name}
                onChange={(e) => setFormData({ ...formData, vendor_name: e.target.value })}
                placeholder="e.g., Dell, IBM, VMware"
                className="w-full px-4 py-3 rounded-lg bg-void-800 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-scout-primary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Partnership Level
              </label>
              <select
                value={formData.partnership_level}
                onChange={(e) => setFormData({ ...formData, partnership_level: e.target.value })}
                className="w-full px-4 py-3 rounded-lg bg-void-800 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-scout-primary"
              >
                <option value="">Select level...</option>
                <option value="Elite">Elite</option>
                <option value="Premier">Premier</option>
                <option value="Partner">Partner</option>
                <option value="Authorized">Authorized</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Capabilities
              </label>
              <input
                type="text"
                value={formData.capabilities}
                onChange={(e) => setFormData({ ...formData, capabilities: e.target.value })}
                placeholder="e.g., Cloud, Storage, Security (comma-separated)"
                className="w-full px-4 py-3 rounded-lg bg-void-800 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-scout-primary"
              />
              <p className="text-xs text-gray-500 mt-1">Separate capabilities with commas</p>
            </div>

            <div className="flex gap-4">
              <button
                type="submit"
                className="px-6 py-3 rounded-lg bg-scout-primary text-white font-medium hover:opacity-90 transition-opacity"
              >
                {editingId ? "Save Changes" : "Add Vendor"}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="px-6 py-3 rounded-lg bg-white/10 text-gray-300 hover:bg-white/20 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Portfolio List */}
      {items.length === 0 ? (
        <div className="glass rounded-xl p-12 text-center">
          <div className="text-6xl mb-4">💼</div>
          <h2 className="text-xl font-semibold text-white mb-2">No vendors yet</h2>
          <p className="text-gray-400 mb-6">
            Add your partner vendors to get portfolio-matched recommendations
          </p>
          <button
            onClick={() => setShowAddForm(true)}
            className="inline-block px-6 py-3 rounded-lg bg-scout-primary text-white font-medium hover:opacity-90 transition-opacity"
          >
            Add Your First Vendor
          </button>
        </div>
      ) : (
        <div className="space-y-8">
          {sortedLevels.map((level) => (
            <div key={level}>
              <h2 className="text-lg font-semibold text-gray-400 mb-4 flex items-center gap-2">
                <LevelBadge level={level} />
                {level}
                <span className="text-sm font-normal">({groupedItems[level].length})</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {groupedItems[level].map((item) => (
                  <div key={item.id} className="glass rounded-xl p-6 group">
                    <div className="flex items-start justify-between">
                      <h3 className="text-lg font-semibold text-white">{item.vendor_name}</h3>
                      <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => handleEdit(item)}
                          className="p-2 rounded-lg text-gray-500 hover:text-scout-primary hover:bg-scout-primary/10 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="p-2 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    
                    {item.capabilities && item.capabilities.length > 0 && (
                      <div className="mt-4 flex flex-wrap gap-2">
                        {item.capabilities.map((cap, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 rounded-full bg-white/5 text-gray-400 text-xs"
                          >
                            {cap}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Bulk import hint */}
      {items.length > 0 && items.length < 5 && (
        <div className="mt-8 glass rounded-xl p-6 text-center">
          <p className="text-gray-400 text-sm">
            💡 <strong>Tip:</strong> The more vendors you add, the better portfolio recommendations you&apos;ll get.
          </p>
        </div>
      )}
    </div>
  );
}

function LevelBadge({ level }: { level: string }) {
  const config: Record<string, string> = {
    Elite: "🥇",
    Premier: "🥈",
    Partner: "🥉",
    Authorized: "✓",
    Other: "•",
  };
  return <span>{config[level] || "•"}</span>;
}
