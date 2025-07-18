import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Layers,
  Zap,
  ChevronRight,
  Loader2,
  Info,
  Copy,
  Check,
  Moon,
  Sun,
  Brain,
  Languages,
  Settings,
  Play,
  MessageSquare,
  BarChart3,
  Eye,
  Terminal,
  Package
} from "lucide-react";
import ReactDiffViewer from "react-diff-viewer-continued";
import { cn } from "./utils";

// Components
import NarrativeInput from "./components/NarrativeInput";
import DeconstructionView from "./components/DeconstructionView";
import TransformationControls from "./components/TransformationControls";
import ProjectionView from "./components/ProjectionView";
import LighthouseBeacon from "./components/LighthouseBeacon";
import TransformationSteps from "./components/TransformationSteps";
import MaieuticDialogue from "./components/MaieuticDialogue";
import TranslationAnalysis from "./components/TranslationAnalysis";
import VisionAnalysis from "./components/VisionAnalysis";
import UnifiedAttributeManager from "./components/UnifiedAttributeManager";
import LLMConfigManager from "./components/LLMConfigManager";
import ErrorBoundary from "./components/ErrorBoundary";
import SimpleTransformApp from "./SimpleTransformApp";
import APIConsole from "./components/APIConsole";
import BatchProcessor from "./components/BatchProcessor";

function App() {
  const [isDark, setIsDark] = useState(true);
  const [narrative, setNarrative] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [deconstruction, setDeconstruction] = useState(null);
  const [projection, setProjection] = useState(null);
  const [transformationSteps, setTransformationSteps] = useState([]);
  const [totalDuration, setTotalDuration] = useState(0);
  const [options, setOptions] = useState(null);
  const [selectedPersona, setSelectedPersona] = useState("philosopher");
  const [selectedNamespace, setSelectedNamespace] = useState("lamish-galaxy");
  const [selectedStyle, setSelectedStyle] = useState("poetic");
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState("simple");
  const [showSteps, setShowSteps] = useState(true);
  const [maieuticResult, setMaieuticResult] = useState(null);
  const [availableModels, setAvailableModels] = useState(null);
  const [selectedModel, setSelectedModel] = useState("llama3.2:latest");

  // Load transformation options and models on mount
  useEffect(() => {
    // Load configurations
    fetch("/configurations")
      .then((res) => res.json())
      .then((data) => {
        setOptions(data);
        // Set default selections based on new API structure
        if (data.personas && data.personas.length > 0) {
          setSelectedPersona(data.personas[0].id);
        }
        if (data.namespaces && data.namespaces.length > 0) {
          setSelectedNamespace(data.namespaces[0].id);
        }
        if (data.styles && data.styles.length > 0) {
          setSelectedStyle(data.styles[0].id);
        }
      })
      .catch((err) => console.error("Failed to load configurations:", err));

    // Load available models
    fetch("/models")
      .then((res) => res.json())
      .then((data) => {
        setAvailableModels(data);
        // Set default model if available
        if (data.text_models && data.text_models.length > 0) {
          setSelectedModel(data.text_models[0].name);
        }
      })
      .catch((err) => console.error("Failed to load models:", err));
  }, []);

  // Toggle theme
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [isDark]);

  const handleTransform = async () => {
    if (!narrative.trim()) return;

    setIsProcessing(true);
    setError(null);
    setTransformationSteps([]); // Clear previous steps

    try {
      // Start transformation request
      const response = await fetch("/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          narrative,
          target_persona: selectedPersona,
          target_namespace: selectedNamespace,
          target_style: selectedStyle,
          show_steps: showSteps,
        }),
      });

      if (!response.ok) {
        throw new Error("Transformation failed");
      }

      const data = await response.json();
      
      // Set up WebSocket for progress updates if transform_id is provided
      if (data.transform_id) {
        const ws = new WebSocket(`ws://localhost:8100/ws/transform/${data.transform_id}`);
        
        ws.onmessage = (event) => {
          const progressData = JSON.parse(event.data);
          if (progressData.type === "progress") {
            // Update UI with real-time progress
            console.log(`Step ${progressData.step} ${progressData.status}:`, progressData.data);
            // You can add visual progress indicators here
          }
        };
        
        ws.onerror = (error) => {
          console.warn("WebSocket error:", error);
        };
        
        // Clean up WebSocket after a reasonable time
        setTimeout(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.close();
          }
        }, 600000); // 10 minutes
      }
      
      setDeconstruction(data.original);
      setProjection(data.projection);
      setTransformationSteps(data.steps);
      setTotalDuration(data.total_duration_ms);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleMaieuticComplete = (result) => {
    setMaieuticResult(result);
    
    // Auto-configure transformation based on maieutic insights
    if (result.suggestedConfig) {
      setSelectedPersona(result.suggestedConfig.persona);
      setSelectedNamespace(result.suggestedConfig.namespace);
      setSelectedStyle(result.suggestedConfig.style);
      
      // Optionally update narrative with enriched version
      if (result.enrichedNarrative) {
        setNarrative(result.enrichedNarrative);
      }
      
      // Switch to transform tab
      setActiveTab("transform");
    }
  };

  const copyProjection = () => {
    if (projection?.narrative) {
      navigator.clipboard.writeText(projection.narrative);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const tabs = [
    { id: "simple", label: "Simple", icon: Sparkles },
    { id: "transform", label: "Transform", icon: Zap },
    { id: "lamish", label: "Lamish", icon: Layers },
    { id: "llm-config", label: "LLM Config", icon: Settings },
    { id: "batch", label: "Batch", icon: Package },
    { id: "api-console", label: "API Console", icon: Terminal },
    { id: "maieutic", label: "Maieutic", icon: Brain },
    { id: "translation", label: "Translation", icon: Languages },
    { id: "vision", label: "Vision", icon: Eye },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Background effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-white/10 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <LighthouseBeacon />
              <div>
                <h1 className="text-2xl font-bold gradient-text">
                  Humanizer Lighthouse
                </h1>
                <p className="text-sm text-muted-foreground">
                  Full-featured Lamish Projection Engine
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Settings className="w-4 h-4 text-muted-foreground" />
                <label className="text-sm text-muted-foreground">
                  <input
                    type="checkbox"
                    checked={showSteps}
                    onChange={(e) => setShowSteps(e.target.checked)}
                    className="mr-2"
                  />
                  Show Steps
                </label>
              </div>
              
              {availableModels && (
                <div className="flex items-center space-x-2">
                  <label className="text-sm text-muted-foreground">Model:</label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="text-sm bg-white/5 border border-white/10 rounded px-2 py-1 text-white"
                  >
                    {availableModels.text_models.map(model => (
                      <option key={model.name} value={model.name} className="bg-slate-900">
                        {model.name} ({model.size})
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <button
                onClick={() => setIsDark(!isDark)}
                className="p-2 rounded-lg glass hover:bg-white/10 transition-colors"
              >
                {isDark ? (
                  <Sun className="w-5 h-5" />
                ) : (
                  <Moon className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex space-x-1 bg-white/5 rounded-lg p-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all",
                  activeTab === tab.id
                    ? "bg-purple-600 text-white shadow-lg"
                    : "text-muted-foreground hover:text-white hover:bg-white/10"
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Narrative Input - Always visible */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-2xl p-8"
          >
            <div className="flex items-center space-x-2 mb-4">
              <Sparkles className="w-5 h-5 text-purple-400" />
              <h2 className="text-xl font-semibold">Enter Your Narrative</h2>
              {maieuticResult && (
                <div className="flex items-center space-x-2 text-sm text-green-400">
                  <Check className="w-4 h-4" />
                  <span>Enhanced by Maieutic Dialogue</span>
                </div>
              )}
            </div>
            <NarrativeInput
              value={narrative}
              onChange={setNarrative}
              onTransform={null}
              isProcessing={isProcessing}
              placeholder={
                activeTab === "maieutic"
                  ? "Enter a narrative to explore through Socratic questioning..."
                  : activeTab === "translation"
                  ? "Enter text to analyze through translation..."
                  : activeTab === "lamish"
                  ? "Enter narrative text to analyze its essence and derive projection attributes..."
                  : "Enter your narrative to transform through the 5-step LPE pipeline..."
              }
            />
          </motion.div>

          {/* Tab Content */}
          <AnimatePresence mode="wait">
            {activeTab === "simple" && (
              <motion.div
                key="simple"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <SimpleTransformApp />
              </motion.div>
            )}

            {activeTab === "transform" && (
              <motion.div
                key="transform"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-8"
              >
                {/* Transformation Controls */}
                {options && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass rounded-2xl p-8"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        <Layers className="w-5 h-5 text-purple-400" />
                        <h2 className="text-xl font-semibold">Transformation Lens</h2>
                      </div>
                      <button
                        onClick={handleTransform}
                        disabled={isProcessing || !narrative.trim()}
                        className={cn(
                          "px-8 py-3 rounded-lg font-medium transition-all",
                          "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white",
                          "disabled:opacity-50 disabled:cursor-not-allowed",
                          "flex items-center space-x-2 shadow-lg"
                        )}
                      >
                        {isProcessing ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Processing 5-Step Pipeline...</span>
                          </>
                        ) : (
                          <>
                            <Play className="w-5 h-5" />
                            <span>Start Advanced Transformation</span>
                          </>
                        )}
                      </button>
                    </div>
                    <TransformationControls
                      options={options}
                      selectedPersona={selectedPersona}
                      selectedNamespace={selectedNamespace}
                      selectedStyle={selectedStyle}
                      onPersonaChange={setSelectedPersona}
                      onNamespaceChange={setSelectedNamespace}
                      onStyleChange={setSelectedStyle}
                    />
                  </motion.div>
                )}

                {/* Transformation Steps */}
                {transformationSteps.length > 0 && (
                  <TransformationSteps
                    steps={transformationSteps}
                    totalDuration={totalDuration}
                    isVisible={showSteps}
                  />
                )}

                {/* Results Section */}
                <AnimatePresence mode="wait">
                  {isProcessing && (
                    <motion.div
                      key="processing"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center py-20"
                    >
                      <Loader2 className="w-12 h-12 animate-spin text-purple-400 mb-4" />
                      <p className="text-lg text-muted-foreground">
                        Processing through {showSteps ? "5-step" : ""} transformation pipeline...
                      </p>
                    </motion.div>
                  )}

                  {!isProcessing && deconstruction && projection && (
                    <motion.div
                      key="results"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="space-y-8"
                    >
                      {/* Deconstruction View */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                      >
                        <DeconstructionView deconstruction={deconstruction} />
                      </motion.div>

                      {/* Projection View */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                      >
                        <ProjectionView
                          projection={projection}
                          onCopy={copyProjection}
                          copied={copied}
                        />
                      </motion.div>

                      {/* Diff View */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="glass rounded-2xl p-8"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-2">
                            <Zap className="w-5 h-5 text-purple-400" />
                            <h2 className="text-xl font-semibold">
                              Transformation Analysis
                            </h2>
                          </div>
                        </div>
                        <div className="bg-black/20 rounded-lg overflow-hidden">
                          <ReactDiffViewer
                            oldValue={narrative}
                            newValue={projection.narrative}
                            splitView={false}
                            useDarkTheme={isDark}
                            hideLineNumbers
                          />
                        </div>
                      </motion.div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}

            {activeTab === "lamish" && (
              <motion.div
                key="lamish"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <UnifiedAttributeManager />
              </motion.div>
            )}

            {activeTab === "llm-config" && (
              <motion.div
                key="llm-config"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <ErrorBoundary>
                  <LLMConfigManager />
                </ErrorBoundary>
              </motion.div>
            )}

            {activeTab === "batch" && (
              <motion.div
                key="batch"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <ErrorBoundary>
                  <BatchProcessor />
                </ErrorBoundary>
              </motion.div>
            )}

            {activeTab === "api-console" && (
              <motion.div
                key="api-console"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <ErrorBoundary>
                  <APIConsole />
                </ErrorBoundary>
              </motion.div>
            )}

            {activeTab === "maieutic" && (
              <motion.div
                key="maieutic"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <MaieuticDialogue
                  narrative={narrative}
                  onComplete={handleMaieuticComplete}
                  isActive={true}
                />
              </motion.div>
            )}

            {activeTab === "translation" && (
              <motion.div
                key="translation"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <TranslationAnalysis
                  narrative={narrative}
                  isActive={true}
                />
              </motion.div>
            )}

            {activeTab === "vision" && (
              <motion.div
                key="vision"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <VisionAnalysis
                  isActive={true}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error display */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-500/10 border border-red-500/20 rounded-lg p-4"
            >
              <p className="text-red-400">{error}</p>
            </motion.div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 mt-20 border-t border-white/10 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-sm text-muted-foreground">
            <p>Enhanced with full Lamish Projection Engine features</p>
            <p className="mt-2">
              Narrative transformation • Maieutic dialogue • Translation analysis
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;