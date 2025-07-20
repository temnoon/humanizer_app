import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Settings,
  Cpu,
  Zap,
  Brain,
  Globe,
  Users,
  Palette,
  Eye,
  MessageSquare,
  Languages,
  TrendingUp,
  Plus,
  Edit3,
  Trash2,
  Save,
  RotateCcw,
  Download,
  Upload,
  AlertTriangle,
  Check,
  Activity,
  Server,
  Database,
  Loader2,
  Key,
  Shield,
  TestTube,
  X
} from "lucide-react";

const LLMConfigManager = () => {
  const [configs, setConfigs] = useState({});
  const [availableProviders, setAvailableProviders] = useState([]);
  const [availableModels, setAvailableModels] = useState({});
  const [selectedTask, setSelectedTask] = useState("deconstruct");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [systemStatus, setSystemStatus] = useState({});
  const [showKeyManager, setShowKeyManager] = useState(false);
  const [keyManagerProvider, setKeyManagerProvider] = useState("");
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [isTestingKey, setIsTestingKey] = useState(false);
  const [ollamaModels, setOllamaModels] = useState([]);
  const [ollamaStatus, setOllamaStatus] = useState(null);
  const [showOllamaManager, setShowOllamaManager] = useState(false);
  const [newModelName, setNewModelName] = useState("");
  const [isPullingModel, setIsPullingModel] = useState(false);
  const [isRefreshingModels, setIsRefreshingModels] = useState(false);
  const [lastRefreshTime, setLastRefreshTime] = useState(null);

  const agentTasks = [
    {
      id: "deconstruct",
      name: "Deconstruct",
      description: "Extract core narrative elements (WHO/WHAT/WHY/HOW/OUTCOME)",
      icon: Zap,
      category: "Pipeline",
      complexity: "Medium",
      typicalTokens: 800
    },
    {
      id: "map", 
      name: "Map to Namespace",
      description: "Translate elements to target universe",
      icon: Globe,
      category: "Pipeline", 
      complexity: "High",
      typicalTokens: 1200
    },
    {
      id: "reconstruct",
      name: "Reconstruct Allegory", 
      description: "Rebuild narrative from persona perspective",
      icon: Users,
      category: "Pipeline",
      complexity: "High", 
      typicalTokens: 1500
    },
    {
      id: "stylize",
      name: "Apply Style",
      description: "Adjust tone and linguistic expression", 
      icon: Palette,
      category: "Pipeline",
      complexity: "Medium",
      typicalTokens: 1000
    },
    {
      id: "reflect",
      name: "Generate Reflection",
      description: "Create meta-commentary on transformation",
      icon: Brain,
      category: "Pipeline", 
      complexity: "High",
      typicalTokens: 1200
    },
    {
      id: "maieutic",
      name: "Maieutic Dialogue",
      description: "Socratic questioning and dialogue generation",
      icon: MessageSquare,
      category: "Analysis",
      complexity: "High",
      typicalTokens: 1000
    },
    {
      id: "translation",
      name: "Translation Analysis", 
      description: "Multi-language semantic analysis",
      icon: Languages,
      category: "Analysis",
      complexity: "Medium",
      typicalTokens: 800
    },
    {
      id: "vision",
      name: "Vision Analysis",
      description: "Image analysis and transcription",
      icon: Eye,
      category: "Multimodal",
      complexity: "High", 
      typicalTokens: 1500
    },
    {
      id: "extract_attributes",
      name: "Extract Attributes",
      description: "Derive persona/namespace/style from text",
      icon: TrendingUp,
      category: "Analysis",
      complexity: "Medium",
      typicalTokens: 1000
    }
  ];

  const providerProfiles = {
    "ollama": {
      name: "Ollama",
      description: "Local LLM hosting with privacy",
      capabilities: ["text", "embedding", "vision"],
      strengths: ["Privacy", "Cost-effective", "Local control", "No API limits"],
      limitations: ["Speed varies", "Hardware dependent", "Model availability"],
      costLevel: "free"
    },
    "openai": {
      name: "OpenAI",
      description: "GPT models with high quality and reliability",
      capabilities: ["text", "vision", "embedding", "function-calling"], 
      strengths: ["High quality", "Fast", "Reliable", "Well-documented"],
      limitations: ["Cost", "Privacy", "Rate limits", "Usage tracking"],
      costLevel: "high"
    },
    "anthropic": {
      name: "Anthropic",
      description: "Claude models with safety focus and reasoning",
      capabilities: ["text", "vision", "analysis"],
      strengths: ["Safety", "Reasoning", "Long context", "Helpful responses"], 
      limitations: ["Cost", "Limited availability", "No embedding"],
      costLevel: "high"
    },
    "google": {
      name: "Google Gemini",
      description: "Google's multimodal AI with large context",
      capabilities: ["text", "vision", "embedding", "multimodal"],
      strengths: ["Multimodal", "Fast", "Large context", "Free tier"],
      limitations: ["Privacy", "Regional availability", "Rate limits"],
      costLevel: "medium"
    },
    "huggingface": {
      name: "Hugging Face",
      description: "Open source models via inference API",
      capabilities: ["text", "embedding", "specialized"],
      strengths: ["Open source", "Model variety", "Community", "Transparency"],
      limitations: ["Speed varies", "Rate limits", "Model consistency"],
      costLevel: "low"
    },
    "groq": {
      name: "Groq",
      description: "Ultra-fast inference with custom hardware",
      capabilities: ["text", "fast-inference"],
      strengths: ["Extremely fast", "Low latency", "Good pricing", "Reliable"],
      limitations: ["Limited models", "No vision", "Hardware dependency"],
      costLevel: "low"
    },
    "together": {
      name: "Together AI",
      description: "Open source models with competitive pricing",
      capabilities: ["text", "fine-tuning", "open-source"],
      strengths: ["Open models", "Good pricing", "Fine-tuning", "Variety"],
      limitations: ["Quality varies", "Less mainstream", "Documentation"],
      costLevel: "medium"
    },
    "replicate": {
      name: "Replicate",
      description: "Run models in the cloud with pay-per-use",
      capabilities: ["text", "vision", "specialized", "custom"],
      strengths: ["Pay per use", "Model variety", "Easy deployment", "No setup"],
      limitations: ["Cost per call", "Cold starts", "Dependency"],
      costLevel: "medium"
    },
    "cohere": {
      name: "Cohere",
      description: "Enterprise-focused language models",
      capabilities: ["text", "embedding", "classification", "enterprise"],
      strengths: ["Enterprise features", "Multilingual", "Embedding", "RAG"],
      limitations: ["Limited availability", "Cost", "Less known"],
      costLevel: "medium"
    },
    "mistral": {
      name: "Mistral AI",
      description: "European AI with strong performance",
      capabilities: ["text", "multilingual", "code"],
      strengths: ["European", "Good performance", "Multilingual", "Open models"],
      limitations: ["Newer provider", "Limited availability", "Ecosystem"],
      costLevel: "medium"
    },
    "mock": {
      name: "Mock Provider",
      description: "Testing provider with predictable responses",
      capabilities: ["text", "embedding", "testing"],
      strengths: ["Testing", "Predictable", "No cost", "Offline"],
      limitations: ["Not for production", "Static responses", "No real AI"],
      costLevel: "free"
    }
  };

  useEffect(() => {
    loadConfigurations();
    loadSystemStatus();
    loadOllamaData();
  }, []);

  const loadConfigurations = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/llm/configurations");
      if (response.ok) {
        const data = await response.json();
        setConfigs(data.task_configs || {});
        setAvailableProviders(data.available_providers || []);
        setAvailableModels(data.available_models || {});
      }
    } catch (error) {
      console.error("Failed to load LLM configurations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSystemStatus = async () => {
    try {
      const response = await fetch("/api/llm/status");
      if (response.ok) {
        const data = await response.json();
        setSystemStatus(data || {});
      } else {
        console.error("Failed to load system status:", response.status);
        setSystemStatus({});
      }
    } catch (error) {
      console.error("Failed to load system status:", error);
      setSystemStatus({});
    }
  };

  const saveConfiguration = async () => {
    setIsSaving(true);
    try {
      const response = await fetch("/api/llm/configurations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task_configs: configs })
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Show success message with details
        const taskCount = Object.keys(configs).length;
        const modelInfo = Object.entries(configs).map(([task, config]) => 
          `${task}: ${config.provider}/${config.model}`
        ).join('\n');
        
        alert(`✅ Successfully saved configurations for ${taskCount} tasks:\n\n${modelInfo}\n\nConfigurations will persist between sessions.`);
        await loadSystemStatus(); // Refresh status
        await loadConfigurations(); // Reload to confirm persistence
      } else {
        const errorData = await response.json();
        alert(`❌ Failed to save configurations: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Failed to save configurations:", error);
      alert(`❌ Error saving configurations: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const resetToDefaults = async () => {
    if (confirm("Reset all configurations to defaults? This cannot be undone.")) {
      try {
        const response = await fetch("/api/llm/configurations/reset", { method: "POST" });
        if (response.ok) {
          await loadConfigurations();
          alert("Configurations reset to defaults");
        }
      } catch (error) {
        console.error("Failed to reset configurations:", error);
      }
    }
  };

  const updateTaskConfig = (taskId, field, value) => {
    setConfigs(prev => ({
      ...prev,
      [taskId]: {
        ...prev[taskId],
        [field]: value
      }
    }));
  };

  const openKeyManager = (provider) => {
    setKeyManagerProvider(provider);
    setApiKeyInput("");
    setShowKeyManager(true);
  };

  const closeKeyManager = () => {
    setShowKeyManager(false);
    setKeyManagerProvider("");
    setApiKeyInput("");
  };

  const storeApiKey = async () => {
    if (!apiKeyInput.trim()) return;
    
    setIsTestingKey(true);
    try {
      const response = await fetch(`/api/llm/keys/${keyManagerProvider}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKeyInput })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`API key stored successfully! ${data.key_valid ? "✅ Key is valid" : "⚠️ Key validation failed"}`);
        await loadSystemStatus(); // Refresh status
        closeKeyManager();
      } else {
        const error = await response.json();
        alert(`Failed to store API key: ${error.detail}`);
      }
    } catch (error) {
      alert(`Error storing API key: ${error.message}`);
    } finally {
      setIsTestingKey(false);
    }
  };

  const deleteApiKey = async (provider) => {
    if (!confirm(`Delete API key for ${provider}? This cannot be undone.`)) return;
    
    try {
      const response = await fetch(`/api/llm/keys/${provider}`, {
        method: "DELETE"
      });
      
      if (response.ok) {
        alert(`API key deleted for ${provider}`);
        await loadSystemStatus(); // Refresh status
      } else {
        const error = await response.json();
        alert(`Failed to delete API key: ${error.detail}`);
      }
    } catch (error) {
      alert(`Error deleting API key: ${error.message}`);
    }
  };

  const testApiKey = async (provider) => {
    setIsTestingKey(true);
    try {
      const response = await fetch(`/api/llm/test/${provider}`, {
        method: "POST"
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`${provider} test result: ${data.success ? "✅ Success" : "❌ Failed"}\n${data.message}`);
      } else {
        alert(`Failed to test ${provider} API key`);
      }
    } catch (error) {
      alert(`Error testing API key: ${error.message}`);
    } finally {
      setIsTestingKey(false);
    }
  };

  const loadOllamaData = async () => {
    try {
      // Load Ollama status
      const statusResponse = await fetch("/api/ollama/status");
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setOllamaStatus(statusData);
        
        // If running, load models
        if (statusData.running) {
          const modelsResponse = await fetch("/api/ollama/models");
          if (modelsResponse.ok) {
            const modelsData = await modelsResponse.json();
            setOllamaModels(modelsData.models || []);
          }
        }
      }
    } catch (error) {
      console.error("Failed to load Ollama data:", error);
      setOllamaStatus({ running: false, error: error.message });
    }
  };

  const pullOllamaModel = async () => {
    if (!newModelName.trim()) return;
    
    setIsPullingModel(true);
    try {
      const response = await fetch("/api/ollama/pull", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: newModelName.trim() })
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`✅ Successfully pulled model: ${newModelName}`);
        setNewModelName("");
        await loadOllamaData(); // Refresh models list
        await loadSystemStatus(); // Refresh provider status
      } else {
        const error = await response.json();
        alert(`❌ Failed to pull model: ${error.detail}`);
      }
    } catch (error) {
      alert(`❌ Error pulling model: ${error.message}`);
    } finally {
      setIsPullingModel(false);
    }
  };

  const deleteOllamaModel = async (modelName) => {
    if (!confirm(`Delete model "${modelName}"? This cannot be undone.`)) return;
    
    try {
      const response = await fetch(`/api/ollama/models/${encodeURIComponent(modelName)}`, {
        method: "DELETE"
      });
      
      if (response.ok) {
        alert(`✅ Successfully deleted model: ${modelName}`);
        await loadOllamaData(); // Refresh models list
      } else {
        const error = await response.json();
        alert(`❌ Failed to delete model: ${error.detail}`);
      }
    } catch (error) {
      alert(`❌ Error deleting model: ${error.message}`);
    }
  };

  const refreshModelLists = async () => {
    setIsRefreshingModels(true);
    try {
      const response = await fetch("/api/llm/refresh-models", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      
      if (response.ok) {
        const data = await response.json();
        setLastRefreshTime(new Date().toLocaleString());
        
        // Update available models
        setAvailableModels(data.available_models || {});
        
        // Refresh system status and Ollama data
        await loadSystemStatus();
        await loadOllamaData();
        
        alert(`✅ Model lists refreshed! Updated ${Object.keys(data.available_models || {}).length} providers`);
      } else {
        const error = await response.json();
        alert(`❌ Failed to refresh models: ${error.detail}`);
      }
    } catch (error) {
      alert(`❌ Error refreshing models: ${error.message}`);
    } finally {
      setIsRefreshingModels(false);
    }
  };

  const currentConfig = configs[selectedTask] || {};
  const selectedTaskInfo = agentTasks.find(t => t.id === selectedTask);

  // Safety check to prevent crashes
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2">Loading LLM configurations...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Cpu className="w-6 h-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              LLM Configuration Center
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <Activity className="w-4 h-4" />
              {Object.keys(configs).length} Configured Tasks
            </div>
            <button
              onClick={refreshModelLists}
              disabled={isRefreshingModels}
              className="inline-flex items-center gap-2 px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white text-sm rounded-lg font-medium transition-colors"
              title="Refresh model lists from live APIs"
            >
              {isRefreshingModels ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Refreshing...
                </>
              ) : (
                <>
                  <RotateCcw className="w-4 h-4" />
                  Refresh Models
                </>
              )}
            </button>
            <button
              onClick={resetToDefaults}
              className="inline-flex items-center gap-2 px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded-lg font-medium transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
            <button
              onClick={saveConfiguration}
              disabled={isSaving}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save All
                </>
              )}
            </button>
          </div>
        </div>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Configure specific LLM providers, models, and parameters for each agent task
        </p>
      </div>

      {/* System Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(systemStatus || {}).map(([provider, status]) => (
          <div key={provider} className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                    {(providerProfiles && providerProfiles[provider]?.name) || provider}
                  </h3>
                  <div className={`w-2 h-2 rounded-full ${
                    status?.available ? "bg-green-500" : "bg-red-500"
                  }`} title={status?.available ? "Available" : "Unavailable"} />
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {status?.status_message || status?.model || "No model"}
                </p>
              </div>
            </div>
            
            {/* Key Management Controls */}
            {provider !== "ollama" && provider !== "mock" && (
              <div className="flex items-center gap-2 mt-3">
                {status?.has_key ? (
                  <>
                    <button
                      onClick={() => testApiKey(provider)}
                      disabled={isTestingKey}
                      className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-800/40 text-blue-700 dark:text-blue-300 rounded transition-colors"
                      title="Test API key"
                    >
                      {isTestingKey ? <Loader2 className="w-3 h-3 animate-spin" /> : "🧪"}
                      Test
                    </button>
                    <button
                      onClick={() => deleteApiKey(provider)}
                      className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 hover:bg-red-200 dark:bg-red-900/30 dark:hover:bg-red-800/40 text-red-700 dark:text-red-300 rounded transition-colors"
                      title="Delete API key"
                    >
                      🗑️ Remove
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => openKeyManager(provider)}
                    className="flex items-center gap-1 px-2 py-1 text-xs bg-green-100 hover:bg-green-200 dark:bg-green-900/30 dark:hover:bg-green-800/40 text-green-700 dark:text-green-300 rounded transition-colors"
                    title="Add API key"
                  >
                    🔑 Add Key
                  </button>
                )}
              </div>
            )}
            
            {/* Provider info */}
            {provider === "ollama" && (
              <div className="mt-3">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  Local provider - no API key needed
                </div>
                <button
                  onClick={() => setShowOllamaManager(true)}
                  className="flex items-center gap-1 px-2 py-1 text-xs bg-purple-100 hover:bg-purple-200 dark:bg-purple-900/30 dark:hover:bg-purple-800/40 text-purple-700 dark:text-purple-300 rounded transition-colors"
                  title="Manage Ollama models"
                >
                  🔧 Manage Models
                </button>
              </div>
            )}
            {provider === "mock" && (
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Testing provider - always available
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Task Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Agent Tasks
            </h3>
            
            <div className="space-y-2">
              {agentTasks.map((task) => {
                const Icon = task.icon;
                return (
                  <button
                    key={task.id}
                    onClick={() => setSelectedTask(task.id)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      selectedTask === task.id
                        ? "bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-700"
                        : "bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon className={`w-5 h-5 ${
                        selectedTask === task.id ? "text-blue-600" : "text-gray-500"
                      }`} />
                      <div className="flex-1">
                        <div className="font-medium text-gray-900 dark:text-white">
                          {task.name}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {task.category} • {task.complexity}
                        </div>
                      </div>
                      {configs[task.id] && (
                        <div className="w-2 h-2 bg-green-500 rounded-full" title="Configured" />
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-6">
          {selectedTaskInfo && (
            <motion.div
              key={selectedTask}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Task Details */}
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-start gap-4">
                  <selectedTaskInfo.icon className="w-8 h-8 text-blue-600 mt-1" />
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {selectedTaskInfo.name}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 mt-1">
                      {selectedTaskInfo.description}
                    </p>
                    <div className="flex items-center gap-4 mt-3 text-sm text-gray-500 dark:text-gray-400">
                      <span>Category: {selectedTaskInfo.category}</span>
                      <span>Complexity: {selectedTaskInfo.complexity}</span>
                      <span>Typical tokens: {selectedTaskInfo.typicalTokens}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* LLM Configuration */}
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  LLM Configuration
                </h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Provider Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Provider
                    </label>
                    <select
                      value={currentConfig.provider || ""}
                      onChange={(e) => updateTaskConfig(selectedTask, "provider", e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Select provider...</option>
                      {availableProviders.map(provider => (
                        <option key={provider} value={provider}>
                          {(providerProfiles && providerProfiles[provider]?.name) || provider}
                        </option>
                      ))}
                    </select>
                    {currentConfig.provider && providerProfiles[currentConfig.provider] && (
                      <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-sm text-gray-700 dark:text-gray-300">
                            {providerProfiles[currentConfig.provider].description}
                          </div>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            providerProfiles[currentConfig.provider].costLevel === 'free' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' :
                            providerProfiles[currentConfig.provider].costLevel === 'low' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200' :
                            providerProfiles[currentConfig.provider].costLevel === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200' :
                            'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200'
                          }`}>
                            {providerProfiles[currentConfig.provider].costLevel} cost
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {providerProfiles[currentConfig.provider].capabilities.map(cap => (
                            <span key={cap} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-xs rounded">
                              {cap}
                            </span>
                          ))}
                        </div>
                        <div className="grid grid-cols-2 gap-3 mt-3 text-xs">
                          <div>
                            <div className="font-medium text-green-600 dark:text-green-400 mb-1">Strengths:</div>
                            <div className="text-gray-600 dark:text-gray-400">
                              {providerProfiles[currentConfig.provider].strengths.join(", ")}
                            </div>
                          </div>
                          <div>
                            <div className="font-medium text-orange-600 dark:text-orange-400 mb-1">Limitations:</div>
                            <div className="text-gray-600 dark:text-gray-400">
                              {providerProfiles[currentConfig.provider].limitations.join(", ")}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Model Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Model
                    </label>
                    <select
                      value={currentConfig.model || ""}
                      onChange={(e) => updateTaskConfig(selectedTask, "model", e.target.value)}
                      disabled={!currentConfig.provider}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-100 dark:disabled:bg-gray-600"
                    >
                      <option value="">Select model...</option>
                      {(availableModels[currentConfig.provider] || []).map(model => (
                        <option key={model.name} value={model.name}>
                          {model.name} ({model.size || "unknown size"}{model.context ? `, ${model.context} context` : ""})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Advanced Parameters */}
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Advanced Parameters
                </h4>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Temperature
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="2"
                      step="0.1"
                      value={currentConfig.temperature || 0.7}
                      onChange={(e) => updateTaskConfig(selectedTask, "temperature", parseFloat(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      0 = deterministic, 2 = very creative
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Max Tokens
                    </label>
                    <input
                      type="number"
                      min="50"
                      max="4000"
                      value={currentConfig.max_tokens || selectedTaskInfo.typicalTokens}
                      onChange={(e) => updateTaskConfig(selectedTask, "max_tokens", parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Maximum response length
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Timeout (seconds)
                    </label>
                    <input
                      type="number"
                      min="10"
                      max="300"
                      value={currentConfig.timeout || 120}
                      onChange={(e) => updateTaskConfig(selectedTask, "timeout", parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Request timeout limit
                    </p>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Top P
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={currentConfig.top_p || 1}
                      onChange={(e) => updateTaskConfig(selectedTask, "top_p", parseFloat(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Nucleus sampling parameter
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Frequency Penalty
                    </label>
                    <input
                      type="number"
                      min="-2"
                      max="2"
                      step="0.1"
                      value={currentConfig.frequency_penalty || 0}
                      onChange={(e) => updateTaskConfig(selectedTask, "frequency_penalty", parseFloat(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Reduce repetition
                    </p>
                  </div>
                </div>
              </div>

              {/* System Prompt Override */}
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  System Prompt Override (Optional)
                </h4>
                <textarea
                  value={currentConfig.system_prompt_override || ""}
                  onChange={(e) => updateTaskConfig(selectedTask, "system_prompt_override", e.target.value)}
                  className="w-full h-24 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono resize-none"
                  placeholder="Leave empty to use default system prompt for this task..."
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Override the default system prompt for this specific task
                </p>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* API Key Management Modal */}
      {showKeyManager && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full mx-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  🔑
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    API Key for {providerProfiles[keyManagerProvider]?.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Securely stored in macOS Keychain
                  </p>
                </div>
              </div>
              <button
                onClick={closeKeyManager}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              >
                ❌
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  API Key
                </label>
                <input
                  type="password"
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  placeholder="Enter your API key..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Provider-specific instructions */}
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="text-sm text-blue-800 dark:text-blue-200">
                  <div className="font-medium mb-1">How to get your {keyManagerProvider} API key:</div>
                  {keyManagerProvider === "openai" && (
                    <div>Visit <a href="https://platform.openai.com/api-keys" target="_blank" className="underline">platform.openai.com/api-keys</a></div>
                  )}
                  {keyManagerProvider === "anthropic" && (
                    <div>Visit <a href="https://console.anthropic.com/" target="_blank" className="underline">console.anthropic.com</a></div>
                  )}
                  {keyManagerProvider === "google" && (
                    <div>Visit <a href="https://makersuite.google.com/app/apikey" target="_blank" className="underline">makersuite.google.com/app/apikey</a></div>
                  )}
                  {keyManagerProvider === "groq" && (
                    <div>Visit <a href="https://console.groq.com/keys" target="_blank" className="underline">console.groq.com/keys</a></div>
                  )}
                  {keyManagerProvider === "cohere" && (
                    <div>Visit <a href="https://dashboard.cohere.ai/api-keys" target="_blank" className="underline">dashboard.cohere.ai/api-keys</a></div>
                  )}
                  {keyManagerProvider === "mistral" && (
                    <div>Visit <a href="https://console.mistral.ai/" target="_blank" className="underline">console.mistral.ai</a></div>
                  )}
                  {!["openai", "anthropic", "google", "groq", "cohere", "mistral"].includes(keyManagerProvider) && (
                    <div>Check the {keyManagerProvider} documentation for API key setup</div>
                  )}
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={closeKeyManager}
                  className="flex-1 px-4 py-2 text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={storeApiKey}
                  disabled={!apiKeyInput.trim() || isTestingKey}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {isTestingKey ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Testing...
                    </>
                  ) : (
                    <>
                      🔒 Store Securely
                    </>
                  )}
                </button>
              </div>

              <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                🛡️ Your API key will be encrypted and stored in macOS Keychain
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Ollama Model Manager Modal */}
      {showOllamaManager && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-2xl w-full mx-4 border border-gray-200 dark:border-gray-700 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  🔧
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Ollama Model Manager
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {ollamaStatus?.running ? `${ollamaModels.length} models installed` : "Ollama server not running"}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowOllamaManager(false)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {ollamaStatus?.running ? (
              <div className="space-y-6">
                {/* Pull New Model */}
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-3">Pull New Model</h4>
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={newModelName}
                      onChange={(e) => setNewModelName(e.target.value)}
                      placeholder="e.g. llama3.2:latest, mistral:7b, codellama:13b"
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    />
                    <button
                      onClick={pullOllamaModel}
                      disabled={!newModelName.trim() || isPullingModel}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
                    >
                      {isPullingModel ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Pulling...
                        </>
                      ) : (
                        <>
                          <Download className="w-4 h-4" />
                          Pull
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-xs text-blue-600 dark:text-blue-400 mt-2">
                    Popular models: llama3.2:latest, mistral:7b, codellama:13b, gemma2:9b
                  </p>
                </div>

                {/* Installed Models */}
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-3">Installed Models</h4>
                  {ollamaModels.length > 0 ? (
                    <div className="space-y-2">
                      {ollamaModels.map((model) => (
                        <div key={model.name} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <div className="flex-1">
                            <div className="font-medium text-gray-900 dark:text-white">
                              {model.name}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {model.details?.family && `${model.details.family} • `}
                              {(model.size / (1024**3)).toFixed(1)} GB
                              {model.details?.parameter_size && ` • ${model.details.parameter_size}`}
                            </div>
                          </div>
                          <button
                            onClick={() => deleteOllamaModel(model.name)}
                            className="ml-3 p-1 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition-colors"
                            title="Delete model"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                      No models installed. Pull a model to get started.
                    </div>
                  )}
                </div>

                {/* Server Info */}
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 className="font-medium text-green-900 dark:text-green-100 mb-2">Server Status</h4>
                  <div className="text-sm text-green-800 dark:text-green-200">
                    ✅ Ollama v{ollamaStatus.version} running at {ollamaStatus.host}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-gray-500 dark:text-gray-400 mb-4">
                  Ollama server is not running or not accessible
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-300">
                  Start Ollama with: <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">ollama serve</code>
                </div>
              </div>
            )}

            <div className="flex justify-end mt-6">
              <button
                onClick={() => setShowOllamaManager(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LLMConfigManager;