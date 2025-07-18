import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Settings,
  Database,
  Brain,
  Users,
  Globe,
  Palette,
  Plus,
  Edit3,
  Trash2,
  BarChart3,
  Activity,
  Search,
  Save,
  X,
  Check,
  TrendingUp,
  Loader2,
  Play,
  Eye,
  Copy,
  RefreshCw,
  Zap
} from "lucide-react";

const UnifiedAttributeManager = () => {
  const [activeView, setActiveView] = useState("list");
  const [allAttributes, setAllAttributes] = useState([]);
  const [selectedAttributes, setSelectedAttributes] = useState([]);
  const [quickNarrative, setQuickNarrative] = useState("");
  const [isQuickProcessing, setIsQuickProcessing] = useState(false);
  const [systemUsage, setSystemUsage] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [editingAttribute, setEditingAttribute] = useState(null);
  const [extractedAttributes, setExtractedAttributes] = useState(null);
  const [isExtracting, setIsExtracting] = useState(false);

  useEffect(() => {
    loadAllAttributes();
    loadSystemUsage();
  }, []);

  const loadAllAttributes = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/lamish/concepts");
      if (response.ok) {
        const data = await response.json();
        
        // Flatten all attribute types into one list
        const flatAttributes = [
          ...data.personas.map(p => ({ ...p, type: "persona", typeIcon: Users, typeColor: "purple" })),
          ...data.namespaces.map(n => ({ ...n, type: "namespace", typeIcon: Globe, typeColor: "green" })),
          ...data.styles.map(s => ({ ...s, type: "style", typeIcon: Palette, typeColor: "orange" }))
        ];
        
        setAllAttributes(flatAttributes);
      }
    } catch (error) {
      console.error("Failed to load attributes:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSystemUsage = async () => {
    try {
      // This would track where each attribute is used across the system
      // For now, mock data showing integration points
      setSystemUsage({
        "philosopher": ["Transform Tab", "Pipeline Inspector", "Default Config"],
        "lamish-galaxy": ["Transform Tab", "Pipeline Inspector", "Extract Tool"],
        "poetic": ["Transform Tab", "Pipeline Inspector", "Style Templates"],
        // Add more usage tracking
      });
    } catch (error) {
      console.error("Failed to load system usage:", error);
    }
  };

  const syncSystemAttributes = async () => {
    try {
      const response = await fetch("/api/lamish/sync-system", { method: "POST" });
      if (response.ok) {
        await loadAllAttributes();
        alert("System attributes synchronized successfully!");
      }
    } catch (error) {
      console.error("Failed to sync system:", error);
    }
  };

  const handleDeleteAttribute = async (id) => {
    if (confirm("Are you sure? This will affect all parts of the system using this attribute.")) {
      try {
        await fetch(`/api/lamish/concepts/${id}`, { method: "DELETE" });
        await loadAllAttributes();
      } catch (error) {
        console.error("Failed to delete attribute:", error);
      }
    }
  };

  const handleQuickProcess = async () => {
    if (!quickNarrative.trim() || selectedAttributes.length !== 3) return;
    
    setIsQuickProcessing(true);
    try {
      const [persona, namespace, style] = selectedAttributes;
      
      const response = await fetch("/api/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          narrative: quickNarrative,
          target_persona: persona.name,
          target_namespace: namespace.name,
          target_style: style.name,
          show_steps: false
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        alert("Quick processing completed! Check the Transform tab for results.");
      }
    } catch (error) {
      console.error("Quick processing failed:", error);
    } finally {
      setIsQuickProcessing(false);
    }
  };

  const extractNewAttributes = async () => {
    if (!quickNarrative.trim()) return;
    
    setIsExtracting(true);
    try {
      const response = await fetch("/api/lamish/extract-attributes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ narrative: quickNarrative })
      });
      
      if (response.ok) {
        const data = await response.json();
        setExtractedAttributes(data);
        setActiveView("extract");
      }
    } catch (error) {
      console.error("Failed to extract attributes:", error);
    } finally {
      setIsExtracting(false);
    }
  };

  const filteredAttributes = allAttributes.filter(attr => {
    const matchesSearch = attr.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         attr.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === "all" || attr.type === filterType;
    return matchesSearch && matchesType;
  });

  const viewModes = [
    { id: "list", label: "All Attributes", icon: BarChart3 },
    { id: "extract", label: "Extract New", icon: TrendingUp },
    { id: "process", label: "Quick Process", icon: Play }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="w-6 h-6 text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Attribute Management Center
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <Activity className="w-4 h-4" />
              {allAttributes.length} Total Attributes
            </div>
            <button
              onClick={syncSystemAttributes}
              className="inline-flex items-center gap-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg font-medium transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Sync System
            </button>
          </div>
        </div>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Unified management for all personas, namespaces, and styles. Edit, test, and deploy changes across the entire system.
        </p>
      </div>

      {/* View Mode Navigation */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="flex overflow-x-auto">
          {viewModes.map((mode) => {
            const Icon = mode.icon;
            return (
              <button
                key={mode.id}
                onClick={() => setActiveView(mode.id)}
                className={`flex items-center gap-2 px-6 py-4 whitespace-nowrap border-b-2 transition-colors ${
                  activeView === mode.id
                    ? "border-indigo-500 text-indigo-600 dark:text-indigo-400"
                    : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                <Icon className="w-4 h-4" />
                {mode.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeView === "list" && (
          <motion.div
            key="list"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Controls */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search attributes..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white w-64"
                    />
                  </div>
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                    className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="all">All Types</option>
                    <option value="persona">Personas</option>
                    <option value="namespace">Namespaces</option>
                    <option value="style">Styles</option>
                  </select>
                </div>
                <button
                  onClick={() => setEditingAttribute({ type: "persona", name: "", description: "", characteristics: [] })}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Add Attribute
                </button>
              </div>
            </div>

            {/* Master Attribute List */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Attribute
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Usage
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        System Integration
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                    {filteredAttributes.map((attr) => {
                      const Icon = attr.typeIcon;
                      return (
                        <tr key={attr.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                          <td className="px-6 py-4">
                            <div>
                              <div className="text-sm font-medium text-gray-900 dark:text-white">
                                {attr.name}
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">
                                {attr.description}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className={`inline-flex items-center gap-2 px-2 py-1 rounded-full text-xs font-medium bg-${attr.typeColor}-100 dark:bg-${attr.typeColor}-900/30 text-${attr.typeColor}-800 dark:text-${attr.typeColor}-200`}>
                              <Icon className="w-3 h-3" />
                              {attr.type}
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                            {attr.usage_count} times
                            <div className="text-xs">
                              Quality: {(attr.quality_score * 100).toFixed(0)}%
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex flex-wrap gap-1">
                              {(systemUsage[attr.name] || []).map((system, idx) => (
                                <span
                                  key={idx}
                                  className="inline-block px-2 py-1 text-xs bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded"
                                >
                                  {system}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => setEditingAttribute(attr)}
                                className="p-1 text-gray-400 hover:text-indigo-600 transition-colors"
                                title="Edit"
                              >
                                <Edit3 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => navigator.clipboard.writeText(attr.name)}
                                className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                                title="Copy Name"
                              >
                                <Copy className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDeleteAttribute(attr.id)}
                                className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                                title="Delete"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )}

        {activeView === "process" && (
          <motion.div
            key="process"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Quick Processing Widget */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Quick Narrative Processing
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Narrative Text
                  </label>
                  <textarea
                    value={quickNarrative}
                    onChange={(e) => setQuickNarrative(e.target.value)}
                    className="w-full h-32 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                    placeholder="Enter narrative text to process quickly with selected attributes..."
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Select Persona
                    </label>
                    <select
                      onChange={(e) => {
                        const persona = allAttributes.find(a => a.id === e.target.value);
                        setSelectedAttributes(prev => [persona, prev[1], prev[2]].filter(Boolean));
                      }}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Choose persona...</option>
                      {allAttributes.filter(a => a.type === "persona").map(p => (
                        <option key={p.id} value={p.id}>{p.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Select Namespace
                    </label>
                    <select
                      onChange={(e) => {
                        const namespace = allAttributes.find(a => a.id === e.target.value);
                        setSelectedAttributes(prev => [prev[0], namespace, prev[2]].filter(Boolean));
                      }}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Choose namespace...</option>
                      {allAttributes.filter(a => a.type === "namespace").map(n => (
                        <option key={n.id} value={n.id}>{n.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Select Style
                    </label>
                    <select
                      onChange={(e) => {
                        const style = allAttributes.find(a => a.id === e.target.value);
                        setSelectedAttributes(prev => [prev[0], prev[1], style].filter(Boolean));
                      }}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Choose style...</option>
                      {allAttributes.filter(a => a.type === "style").map(s => (
                        <option key={s.id} value={s.id}>{s.name}</option>
                      ))}
                    </select>
                  </div>
                </div>
                
                <div className="flex gap-3">
                  <button
                    onClick={handleQuickProcess}
                    disabled={!quickNarrative.trim() || selectedAttributes.length !== 3 || isQuickProcessing}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
                  >
                    {isQuickProcessing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Quick Process
                      </>
                    )}
                  </button>
                  
                  <button
                    onClick={extractNewAttributes}
                    disabled={!quickNarrative.trim() || isExtracting}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
                  >
                    {isExtracting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Extracting...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4" />
                        Extract New Attributes
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UnifiedAttributeManager;