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
  Package,
  Archive,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  Cpu,
  Shield,
  BookOpen
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
import SideBySideResults from "./components/SideBySideResults";
import MaieuticDialogue from "./components/MaieuticDialogue";
import TranslationAnalysis from "./components/TranslationAnalysis";
import VisionAnalysis from "./components/VisionAnalysis";
import AttributeStudio from "./components/AttributeStudio";
import LLMConfigManager from "./components/LLMConfigManager";
import ErrorBoundary from "./components/ErrorBoundary";
import ConversationBrowser from "./ConversationBrowser";
import EnhancedAPIConsole from "./components/EnhancedAPIConsole";
import BatchProcessor from "./components/BatchProcessor";
import ArchiveExplorer from "./components/ArchiveExplorer";
import TransformationManager from "./components/TransformationManager";
import WritebookEditor from "./components/WritebookEditor";
import WritebookManager from "./components/WritebookManager";
import WritebookPageEditor from "./components/WritebookPageEditor";
import SemanticTomography from "./components/SemanticTomography";
import IntelligentAttributeEditor from "./components/IntelligentAttributeEditor";
import { AttributeProvider } from "./contexts/AttributeContext";

function App() {
  const [isDark, setIsDark] = useState(true);
  const [narrative, setNarrative] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [deconstruction, setDeconstruction] = useState(null);
  const [projection, setProjection] = useState(null);
  const [transformationSteps, setTransformationSteps] = useState([]);
  const [totalDuration, setTotalDuration] = useState(0);
  const [options, setOptions] = useState(null);
  const [selectedPersona, setSelectedPersona] = useState(
    localStorage.getItem('lastSelectedPersona') || "philosopher"
  );
  const [selectedNamespace, setSelectedNamespace] = useState(
    localStorage.getItem('lastSelectedNamespace') || "lamish-galaxy"
  );
  const [selectedStyle, setSelectedStyle] = useState(
    localStorage.getItem('lastSelectedStyle') || "poetic"
  );
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState("simple");
  const [showSteps, setShowSteps] = useState(true);
  const [maieuticResult, setMaieuticResult] = useState(null);
  const [savedTransformation, setSavedTransformation] = useState(null);
  const [conversationBrowserParams, setConversationBrowserParams] = useState({
    initialConversationId: null,
    initialMessageId: null
  });
  const [writebookView, setWritebookView] = useState('manager'); // 'manager', 'editor', or 'page-editor'
  const [editingPageId, setEditingPageId] = useState(null);

  // Handle URL parameters for direct conversation links
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const conversationId = urlParams.get('conversation');
    const messageId = urlParams.get('message');
    
    if (conversationId) {
      navigateToConversationBrowser(conversationId, messageId);
      // Clear URL parameters to avoid stale state on refresh
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);
  
  // Balanced transformation state - FORCED TO BALANCED MODE
  const [balanceAnalysis, setBalanceAnalysis] = useState(null);
  const [isAnalyzingBalance, setIsAnalyzingBalance] = useState(false);
  const [balancedResult, setBalancedResult] = useState(null);
  const [useBalancedTransformation, setUseBalancedTransformation] = useState(true); // Always balanced
  
  // Quantum narrative theory state
  const [semanticTomography, setSemanticTomography] = useState(null);
  const [isAnalyzingSemantics, setIsAnalyzingSemantics] = useState(false);
  const [showQuantumAnalysis, setShowQuantumAnalysis] = useState(true); // Show by default

  // Navigation helper for switching to conversation browser with specific parameters
  const navigateToConversationBrowser = (conversationId, messageId = null) => {
    setConversationBrowserParams({
      initialConversationId: conversationId,
      initialMessageId: messageId
    });
    setActiveTab("conversation");
    
    // Clear the parameters after a brief delay to prevent stale state
    setTimeout(() => {
      setConversationBrowserParams({
        initialConversationId: null,
        initialMessageId: null
      });
    }, 1000);
  };

  // Navigation helper for switching to writebook editor
  const navigateToWritebook = () => {
    setActiveTab("writebook");
    setWritebookView('editor');
  };

  // Navigation helper for switching to writebook manager
  const navigateToWritebookManager = () => {
    setActiveTab("writebook");
    setWritebookView('manager');
    setEditingPageId(null);
  };

  // Navigation helper for switching to full-page editor
  const navigateToPageEditor = (pageId, writebookData, pages) => {
    setActiveTab("writebook");
    setWritebookView('page-editor');
    setEditingPageId(pageId);
    
    // Store the current writebook data for the page editor
    const editorData = {
      writebookData,
      pages,
      editingPageId: pageId
    };
    localStorage.setItem('writebook_editor_data', JSON.stringify(editorData));
  };

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

  }, []);

  // Toggle theme
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [isDark]);

  const analyzeBalance = async () => {
    if (!narrative.trim()) return;

    setIsAnalyzingBalance(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8100/api/balanced/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          persona: selectedPersona,
          namespace: selectedNamespace,
          style: selectedStyle,
          narrative: narrative,
        }),
      });

      if (!response.ok) {
        throw new Error("Balance analysis failed");
      }

      const data = await response.json();
      setBalanceAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzingBalance(false);
    }
  };

  const analyzeSemanticTomography = async () => {
    if (!narrative.trim()) return;

    setIsAnalyzingSemantics(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8100/api/narrative-theory/semantic-tomography", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: narrative,
          transformation_attributes: {
            persona: selectedPersona,
            namespace: selectedNamespace,
            style: selectedStyle
          },
          reading_style: "interpretation"
        }),
      });

      if (!response.ok) {
        throw new Error("Semantic tomography analysis failed");
      }

      const data = await response.json();
      setSemanticTomography(data);
    } catch (err) {
      console.error("Semantic tomography error:", err);
      setError(err.message);
    } finally {
      setIsAnalyzingSemantics(false);
    }
  };

  const handleTransform = async () => {
    if (!narrative.trim()) return;

    setIsProcessing(true);
    setError(null);
    setTransformationSteps([]); // Clear previous steps
    setBalancedResult(null);

    try {
      let response, data;

      if (useBalancedTransformation) {
        // Use the new balanced transformation API
        response = await fetch("http://localhost:8100/api/balanced/transform", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            narrative,
            persona: selectedPersona,
            namespace: selectedNamespace,
            style: selectedStyle,
            show_steps: showSteps,
            apply_balancing: true,
          }),
        });

        if (!response.ok) {
          throw new Error("Balanced transformation failed");
        }

        data = await response.json();
        setBalancedResult(data);
        
        // Convert to legacy format for compatibility
        setDeconstruction({ elements: data.source_dna });
        setProjection({ 
          narrative: data.transformed_narrative,
          metadata: {
            preservation_score: data.overall_preservation_score,
            balancing_analysis: data.balancing_analysis,
            performance_metrics: data.performance_metrics
          }
        });
        setTransformationSteps(data.steps);
        setTotalDuration(data.processing_time_ms);
      } else {
        // Use the legacy transformation API
        response = await fetch("/transform", {
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
          throw new Error("Legacy transformation failed");
        }

        data = await response.json();
        
        // Set up WebSocket for progress updates if transform_id is provided
        if (data.transform_id) {
          const ws = new WebSocket(`ws://localhost:8100/ws/transform/${data.transform_id}`);
          
          ws.onmessage = (event) => {
            const progressData = JSON.parse(event.data);
            if (progressData.type === "progress") {
              console.log(`Step ${progressData.step} ${progressData.status}:`, progressData.data);
            }
          };
          
          ws.onerror = (error) => {
            console.warn("WebSocket error:", error);
          };
          
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
      }
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

  const handleSaveTransformation = (editedText) => {
    // Save the edited transformation
    setSavedTransformation(editedText);
    // Optionally, you could also update the projection state
    if (projection) {
      setProjection({ ...projection, narrative: editedText });
    }
  };

  // Helper functions for balance analysis display
  const getBalanceStatusColor = (isBalanced, templateRisk) => {
    if (isBalanced) return 'text-green-400';
    if (templateRisk > 0.7) return 'text-red-400';
    return 'text-yellow-400';
  };

  const getBalanceStatusIcon = (isBalanced, templateRisk) => {
    if (isBalanced) return <CheckCircle className="w-5 h-5" />;
    if (templateRisk > 0.7) return <XCircle className="w-5 h-5" />;
    return <AlertTriangle className="w-5 h-5" />;
  };

  const getBalanceStatusText = (isBalanced, templateRisk) => {
    if (isBalanced) return 'Well Balanced';
    if (templateRisk > 0.7) return 'High Template Risk';
    return 'Needs Adjustment';
  };

  // Primary workflow tabs (main row)
  const primaryTabs = [
    { id: "conversation", label: "Conversations", icon: MessageSquare },
    { id: "transform", label: "Transform", icon: Zap },
    { id: "transformations", label: "Saved", icon: Archive },
    { id: "writebook", label: "Writebook", icon: BookOpen },
    { id: "archive", label: "Archive", icon: BarChart3 },
  ];

  // Secondary feature tabs (second row)
  const secondaryTabs = [
    { id: "lamish", label: "Attribute Studio", icon: Layers },
    { id: "maieutic", label: "Maieutic", icon: Brain },
    { id: "translation", label: "Translation", icon: Languages },
    { id: "vision", label: "Vision", icon: Eye },
    { id: "semantic-tomography", label: "Quantum Analysis", icon: Target },
  ];

  // System/developer tabs (third row)
  const systemTabs = [
    { id: "llm-config", label: "LLM Config", icon: Settings },
    { id: "batch", label: "Batch", icon: Package },
    { id: "api-console", label: "API Console", icon: Terminal },
  ];

  return (
    <AttributeProvider>
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

      {/* Tab Navigation - Three Tier System */}
      <nav className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-3">
        {/* Primary Workflow Tabs */}
        <div className="flex space-x-1 bg-white/5 rounded-lg p-1">
          {primaryTabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all",
                  activeTab === tab.id
                    ? "bg-purple-600 text-white shadow-lg"
                    : "text-muted-foreground hover:text-white hover:bg-white/10"
                )}
              >
                <Icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Secondary Feature Tabs */}
        <div className="flex space-x-1 bg-white/3 rounded-lg p-1">
          <div className="flex items-center px-3 py-1 text-xs text-gray-400 font-medium">
            ANALYSIS
          </div>
          {secondaryTabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all text-sm",
                  activeTab === tab.id
                    ? "bg-blue-600 text-white shadow-lg"
                    : "text-muted-foreground hover:text-white hover:bg-white/10"
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* System/Developer Tabs */}
        <div className="flex space-x-1 bg-white/2 rounded-lg p-1">
          <div className="flex items-center px-3 py-1 text-xs text-gray-500 font-medium">
            SYSTEM
          </div>
          {systemTabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center space-x-2 px-3 py-1.5 rounded-lg font-medium transition-all text-sm",
                  activeTab === tab.id
                    ? "bg-gray-600 text-white shadow-lg"
                    : "text-muted-foreground hover:text-white hover:bg-white/10"
                )}
              >
                <Icon className="w-3 h-3" />
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
            {activeTab === "conversation" && (
              <motion.div
                key="conversation"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <ConversationBrowser 
                  initialConversationId={conversationBrowserParams.initialConversationId}
                  initialMessageId={conversationBrowserParams.initialMessageId}
                  onNavigateToConversation={navigateToConversationBrowser}
                  onNavigateToWritebook={navigateToWritebook}
                />
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
                {/* Quantum Narrative Theory Mode */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.05 }}
                  className="glass rounded-2xl p-6 border-l-4 border-purple-500"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Brain className="w-6 h-6 text-purple-400" />
                      <div>
                        <h3 className="text-lg font-semibold text-purple-100">Quantum Narrative Engine</h3>
                        <p className="text-sm text-purple-200">Balanced transformation with quantum consciousness analysis</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                      <span className="text-sm text-green-400 font-medium">Active</span>
                    </div>
                  </div>
                </motion.div>

                {/* Transformation Controls */}
                {options && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass rounded-2xl p-8"
                  >
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center space-x-2">
                        <Layers className="w-5 h-5 text-purple-400" />
                        <h2 className="text-xl font-semibold">Transformation Lens</h2>
                      </div>
                      <div className="flex items-center space-x-3">
                        {useBalancedTransformation && (
                          <>
                            <button
                              onClick={analyzeBalance}
                              disabled={isAnalyzingBalance || !narrative.trim()}
                              className={cn(
                                "px-4 py-2 rounded-lg font-medium transition-all",
                                "bg-blue-600 hover:bg-blue-700 text-white",
                                "disabled:opacity-50 disabled:cursor-not-allowed",
                                "flex items-center space-x-2"
                              )}
                            >
                              {isAnalyzingBalance ? (
                                <>
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                  <span>Analyzing...</span>
                                </>
                              ) : (
                                <>
                                  <Target className="w-4 h-4" />
                                  <span>Analyze Balance</span>
                                </>
                              )}
                            </button>
                            <button
                              onClick={analyzeSemanticTomography}
                              disabled={isAnalyzingSemantics || !narrative.trim()}
                              className={cn(
                                "px-4 py-2 rounded-lg font-medium transition-all",
                                "bg-purple-600 hover:bg-purple-700 text-white",
                                "disabled:opacity-50 disabled:cursor-not-allowed",
                                "flex items-center space-x-2"
                              )}
                            >
                              {isAnalyzingSemantics ? (
                                <>
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                  <span>Analyzing...</span>
                                </>
                              ) : (
                                <>
                                  <Brain className="w-4 h-4" />
                                  <span>QBist Analysis</span>
                                </>
                              )}
                            </button>
                          </>
                        )}
                        <button
                          onClick={handleTransform}
                          disabled={isProcessing || !narrative.trim()}
                          className={cn(
                            "px-8 py-3 rounded-lg font-medium transition-all",
                            useBalancedTransformation 
                              ? "bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
                              : "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700",
                            "text-white disabled:opacity-50 disabled:cursor-not-allowed",
                            "flex items-center space-x-2 shadow-lg"
                          )}
                        >
                          {isProcessing ? (
                            <>
                              <Loader2 className="w-5 h-5 animate-spin" />
                              <span>
                                {useBalancedTransformation ? 'Processing Balanced Pipeline...' : 'Processing 5-Step Pipeline...'}
                              </span>
                            </>
                          ) : (
                            <>
                              {useBalancedTransformation ? <Cpu className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                              <span>
                                {useBalancedTransformation ? 'Start Balanced Transformation' : 'Start Advanced Transformation'}
                              </span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                    <IntelligentAttributeEditor
                      narrative={narrative}
                      onAttributesChange={(attrs) => {
                        setSelectedPersona(attrs.persona);
                        setSelectedNamespace(attrs.namespace);
                        setSelectedStyle(attrs.style);
                        // Persist last selected attributes
                        localStorage.setItem('lastSelectedPersona', attrs.persona);
                        localStorage.setItem('lastSelectedNamespace', attrs.namespace);
                        localStorage.setItem('lastSelectedStyle', attrs.style);
                      }}
                      onAnalysisComplete={(analysis) => {
                        // Store AI analysis for use in transformation
                        console.log('AI attribute analysis:', analysis);
                      }}
                    />
                  </motion.div>
                )}

                {/* Balance Analysis Results */}
                {balanceAnalysis && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 }}
                    className="glass rounded-2xl p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
                        <Target className="w-5 h-5 text-blue-400" />
                        <span>Balance Analysis</span>
                      </h3>
                      <div className={`flex items-center space-x-2 ${getBalanceStatusColor(balanceAnalysis.is_balanced, balanceAnalysis.template_risk_score)}`}>
                        {getBalanceStatusIcon(balanceAnalysis.is_balanced, balanceAnalysis.template_risk_score)}
                        <span className="font-medium">
                          {getBalanceStatusText(balanceAnalysis.is_balanced, balanceAnalysis.template_risk_score)}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="bg-black/20 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-300 text-sm">Template Risk</span>
                          <span className={`font-mono text-sm ${balanceAnalysis.template_risk_score > 0.7 ? 'text-red-400' : balanceAnalysis.template_risk_score > 0.4 ? 'text-yellow-400' : 'text-green-400'}`}>
                            {(balanceAnalysis.template_risk_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                          <div 
                            className={`h-2 rounded-full ${balanceAnalysis.template_risk_score > 0.7 ? 'bg-red-500' : balanceAnalysis.template_risk_score > 0.4 ? 'bg-yellow-500' : 'bg-green-500'}`}
                            style={{ width: `${balanceAnalysis.template_risk_score * 100}%` }}
                          />
                        </div>
                      </div>

                      <div className="bg-black/20 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-300 text-sm">Preservation Score</span>
                          <span className={`font-mono text-sm ${balanceAnalysis.preservation_score > 0.7 ? 'text-green-400' : balanceAnalysis.preservation_score > 0.4 ? 'text-yellow-400' : 'text-red-400'}`}>
                            {(balanceAnalysis.preservation_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                          <div 
                            className={`h-2 rounded-full ${balanceAnalysis.preservation_score > 0.7 ? 'bg-green-500' : balanceAnalysis.preservation_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${balanceAnalysis.preservation_score * 100}%` }}
                          />
                        </div>
                      </div>

                      <div className="bg-black/20 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-300 text-sm">Conflicts</span>
                          <span className={`font-mono text-sm ${balanceAnalysis.conflicts.length === 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {balanceAnalysis.conflicts.length}
                          </span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          {balanceAnalysis.conflicts.length > 0 ? balanceAnalysis.conflicts.join(', ') : 'None detected'}
                        </div>
                      </div>
                    </div>

                    {/* Issues and Suggestions */}
                    {(balanceAnalysis.dominant_attributes.length > 0 || balanceAnalysis.suggestions.length > 0) && (
                      <div className="space-y-3">
                        {balanceAnalysis.dominant_attributes.length > 0 && (
                          <div className="bg-orange-900/20 border border-orange-500/30 rounded-lg p-3">
                            <div className="flex items-center space-x-2 mb-1">
                              <AlertTriangle className="w-4 h-4 text-orange-400" />
                              <span className="font-medium text-orange-300 text-sm">Dominant Attributes</span>
                            </div>
                            <p className="text-orange-200 text-xs">
                              {balanceAnalysis.dominant_attributes.join(', ')} may overpower the transformation
                            </p>
                          </div>
                        )}

                        {balanceAnalysis.suggestions.length > 0 && (
                          <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3">
                            <div className="flex items-center space-x-2 mb-2">
                              <Info className="w-4 h-4 text-blue-400" />
                              <span className="font-medium text-blue-300 text-sm">Suggestions</span>
                            </div>
                            <ul className="text-blue-200 text-xs space-y-1">
                              {balanceAnalysis.suggestions.map((suggestion, index) => (
                                <li key={index}>• {suggestion}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Semantic Tomography Results */}
                {semanticTomography && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass rounded-2xl p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
                        <Brain className="w-5 h-5 text-purple-400" />
                        <span>Quantum Narrative Analysis</span>
                      </h3>
                      <div className="flex items-center space-x-2 text-purple-300">
                        <div className="w-3 h-3 bg-purple-400 rounded-full animate-pulse"></div>
                        <span className="font-medium text-sm">QBist Meaning Analysis Complete</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="bg-black/20 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-300 text-sm">Fidelity</span>
                          <span className="font-mono text-sm text-purple-400">
                            {semanticTomography.transformation_metrics?.fidelity?.toFixed(3) || 'N/A'}
                          </span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          State similarity measure
                        </div>
                      </div>

                      <div className="bg-black/20 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-300 text-sm">Purity Change</span>
                          <span className={cn(
                            "font-mono text-sm",
                            semanticTomography.transformation_metrics?.purity_change > 0 ? "text-green-400" : "text-red-400"
                          )}>
                            {semanticTomography.transformation_metrics?.purity_change > 0 ? '+' : ''}
                            {semanticTomography.transformation_metrics?.purity_change?.toFixed(3) || 'N/A'}
                          </span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          {semanticTomography.transformation_metrics?.purity_change > 0 ? 'More focused' : 'More mixed'}
                        </div>
                      </div>

                      <div className="bg-black/20 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-300 text-sm">Entropy Change</span>
                          <span className={cn(
                            "font-mono text-sm",
                            semanticTomography.transformation_metrics?.entropy_change > 0 ? "text-orange-400" : "text-blue-400"
                          )}>
                            {semanticTomography.transformation_metrics?.entropy_change > 0 ? '+' : ''}
                            {semanticTomography.transformation_metrics?.entropy_change?.toFixed(3) || 'N/A'}
                          </span>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          {semanticTomography.transformation_metrics?.entropy_change > 0 ? 'More uncertain' : 'More certain'}
                        </div>
                      </div>
                    </div>

                    {/* POVM Measurement Outcomes */}
                    {semanticTomography.measurement_outcome && (
                      <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-3">
                          <Target className="w-4 h-4 text-green-400" />
                          <span className="font-medium text-green-300 text-sm">POVM Measurement Outcomes</span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                          {Object.entries(semanticTomography.measurement_outcome)
                            .sort(([,a], [,b]) => b - a)
                            .slice(0, 8)
                            .map(([label, prob]) => (
                              <div key={label} className="text-center p-2 bg-black/30 rounded">
                                <div className="text-sm font-bold text-green-400">
                                  {(prob * 100).toFixed(1)}%
                                </div>
                                <div className="text-xs text-gray-400 truncate">
                                  {label}
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}

                    {/* Toggle for full semantic tomography view */}
                    <div className="mt-4 text-center">
                      <button
                        onClick={() => setActiveTab("semantic-tomography")}
                        className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
                      >
                        View Full Quantum Analysis →
                      </button>
                    </div>
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
                      {/* Side-by-Side Results */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                      >
                        <SideBySideResults
                          originalText={narrative}
                          transformedText={projection.narrative}
                          metadata={{
                            target_persona: selectedPersona,
                            target_namespace: selectedNamespace,
                            target_style: selectedStyle,
                            total_duration_ms: totalDuration,
                            ...projection.metadata
                          }}
                          onCopy={copyProjection}
                          copied={copied}
                          onSave={handleSaveTransformation}
                        />
                      </motion.div>

                      {/* Traditional Analysis Views (Collapsible) */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="space-y-6"
                      >
                        {/* Analysis Toggle */}
                        <details className="group">
                          <summary className="glass rounded-xl p-4 cursor-pointer hover:bg-white/5 transition-colors">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <Zap className="w-5 h-5 text-purple-400" />
                                <h3 className="text-lg font-semibold">Advanced Analysis & Diff</h3>
                              </div>
                              <ChevronRight className="w-5 h-5 text-purple-400 transition-transform group-open:rotate-90" />
                            </div>
                          </summary>
                          
                          <div className="mt-4 space-y-6">
                            {/* Deconstruction View */}
                            <DeconstructionView deconstruction={deconstruction} />

                            {/* Traditional Projection View */}
                            <ProjectionView
                              projection={projection}
                              onCopy={copyProjection}
                              copied={copied}
                            />

                            {/* Diff View */}
                            <div className="glass rounded-2xl p-8">
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
                            </div>
                          </div>
                        </details>
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
                <AttributeStudio />
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
                  <EnhancedAPIConsole />
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

            {activeTab === "archive" && (
              <motion.div
                key="archive"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <ErrorBoundary>
                  <ArchiveExplorer 
                    onNavigateToConversation={navigateToConversationBrowser}
                  />
                </ErrorBoundary>
              </motion.div>
            )}

            {activeTab === "transformations" && (
              <motion.div
                key="transformations"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <ErrorBoundary>
                  <TransformationManager />
                </ErrorBoundary>
              </motion.div>
            )}

            {activeTab === "writebook" && (
              <motion.div
                key="writebook"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <ErrorBoundary>
                  {writebookView === 'manager' ? (
                    <WritebookManager onNavigateToEditor={navigateToWritebook} />
                  ) : writebookView === 'page-editor' ? (
                    <WritebookPageEditor 
                      pageId={editingPageId}
                      onNavigateBack={navigateToWritebookManager}
                      onSave={(page, writebook) => {
                        // Handle any additional save logic here
                        console.log('Page saved:', page.id);
                      }}
                    />
                  ) : (
                    <WritebookEditor 
                      onNavigateToManager={navigateToWritebookManager}
                      onNavigateToPageEditor={navigateToPageEditor}
                    />
                  )}
                </ErrorBoundary>
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

            {activeTab === "semantic-tomography" && (
              <motion.div
                key="semantic-tomography"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <SemanticTomography />
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
    </AttributeProvider>
  );
}

export default App;