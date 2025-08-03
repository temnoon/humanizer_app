import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Plus,
  Archive,
  Zap,
  BookOpen,
  Target,
  Brain,
  BarChart3,
  Layers,
  MessageSquare,
  Settings,
  Terminal,
  Search,
  Upload,
  Map,
  Beaker,
  Download,
  Moon,
  Sun,
  HardDrive,
  Loader2,
  Languages,
  Workflow
} from "lucide-react";
import { cn } from "./utils";

// Components - Subjective Narrative Humanizer
import DiscoveryDashboard from "./components/DiscoveryDashboard";
import ContentIngestion from "./components/ContentIngestion";
import FilesystemIngestion from "./components/FilesystemIngestion";
import BookGenerator from "./components/BookGenerator";
import NarrativeStudio from "./components/NarrativeStudio";
import SimpleArchiveExplorer from "./components/SimpleArchiveExplorer";
import APIPlayground from "./components/APIPlayground";
import ErrorBoundary from "./components/ErrorBoundary";
import LighthouseBeacon from "./components/LighthouseBeacon";
import LLMConfigManager from "./components/LLMConfigManager";
import EnhancedAPIConsole from "./components/EnhancedAPIConsole";
import CLITerminal from "./components/CLITerminal";
import TranslationStudio from "./components/TranslationStudio";
import PipelineManager from "./components/PipelineManager";
import ExportHub from "./components/ExportHub";
import ThematicMaps from "./components/ThematicMaps";
import EssenceDistillery from "./components/EssenceDistillery";
import PersonalAnalytics from "./components/PersonalAnalytics";
import TransformationLab from "./components/TransformationLab";

// Placeholder components for tabs not yet implemented
const PlaceholderTab = ({ tabName }) => (
  <div className="h-full flex items-center justify-center">
    <div className="text-center">
      <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
        <Sparkles className="w-8 h-8 text-primary" />
      </div>
      <h2 className="text-xl font-semibold text-foreground mb-2">{tabName}</h2>
      <p className="text-muted-foreground">Coming soon...</p>
    </div>
  </div>
);

function App() {
  const [isDark, setIsDark] = useState(true);
  const [activeTab, setActiveTab] = useState("discovery-dashboard");
  const [isLoading, setIsLoading] = useState(false);
  
  // Navigation helper for Subjective Narrative Humanizer
  const navigateToTab = (tabId, params = {}) => {
    setActiveTab(tabId);
    // Handle additional parameters for specific tabs
    if (params && Object.keys(params).length > 0) {
      console.log(`Navigating to ${tabId} with params:`, params);
    }
  };

  // Core Discovery Tabs (Primary) - Subjective Narrative Humanizer
  const coreDiscoveryTabs = [
    { id: "discovery-dashboard", label: "Discovery", icon: Sparkles, description: "AI-curated insights from your content" },
    { id: "content-ingestion", label: "Ingest", icon: Plus, description: "Upload and process new content" },
    { id: "filesystem-ingestion", label: "Filesystem", icon: HardDrive, description: "Import documents from filesystem with embeddings" },
    { id: "archive-explorer", label: "Archive", icon: Archive, description: "Search and browse your content" },
    { id: "narrative-studio", label: "Studio", icon: Zap, description: "Transform and refine narratives" },
    { id: "book-generator", label: "Books", icon: BookOpen, description: "Generate books from insights" },
  ];

  // Analysis Tabs (Secondary) - Advanced Tools
  const analysisTools = [
    { id: "translation-studio", label: "Translation", icon: Languages, description: "Translation chains and semantic analysis" },
    { id: "thematic-maps", label: "Themes", icon: Map, description: "Visualize concept connections" },
    { id: "essence-distillery", label: "Essence", icon: Beaker, description: "Extract core insights" },
    { id: "personal-analytics", label: "Analytics", icon: BarChart3, description: "Writing patterns and trends" },
    { id: "transformation-lab", label: "Transform", icon: Layers, description: "Advanced perspective tools" },
  ];

  // System Tabs (Utility) - Configuration & Technical
  const systemTabs = [
    { id: "pipeline-manager", label: "Pipelines", icon: Layers, description: "Batch operations and workflows" },
    { id: "export-hub", label: "Export", icon: Download, description: "Joplin, Discourse, PDF export" },
    { id: "settings", label: "Settings", icon: Settings, description: "LLM config and preferences" },
    { id: "api-console", label: "Console", icon: Terminal, description: "Technical interface" },
    { id: "cli-terminal", label: "Terminal", icon: MessageSquare, description: "HAW CLI command execution" },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "discovery-dashboard":
        return <DiscoveryDashboard onNavigate={navigateToTab} />;
      case "content-ingestion":
        return <ContentIngestion onNavigate={navigateToTab} />;
      case "filesystem-ingestion":
        return <FilesystemIngestion onNavigate={navigateToTab} />;
      case "archive-explorer":
        try {
          console.log("Rendering SimpleArchiveExplorer...");
          return <SimpleArchiveExplorer onNavigate={navigateToTab} />;
        } catch (error) {
          console.error("Error rendering SimpleArchiveExplorer:", error);
          return <PlaceholderTab tabName="Archive (Error)" />;
        }
      case "narrative-studio":
        return <NarrativeStudio onNavigate={navigateToTab} />;
      case "book-generator":
        return <BookGenerator onNavigate={navigateToTab} />;
      case "settings":
        return <LLMConfigManager />;
      case "api-console":
        return <APIPlayground />;
      case "cli-terminal":
        return <CLITerminal />;
      case "translation-studio":
        return <TranslationStudio onNavigate={navigateToTab} />;
      case "pipeline-manager":
        return <PipelineManager onNavigate={navigateToTab} />;
      case "export-hub":
        return <ExportHub onNavigate={navigateToTab} />;
      case "thematic-maps":
        return <ThematicMaps onNavigate={navigateToTab} />;
      case "essence-distillery":
        return <EssenceDistillery onNavigate={navigateToTab} />;
      case "personal-analytics":
        return <PersonalAnalytics onNavigate={navigateToTab} />;
      case "transformation-lab":
        return <TransformationLab onNavigate={navigateToTab} />;
      default:
        return <PlaceholderTab tabName={activeTab.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())} />;
    }
  };

  const TabButton = ({ tab, isActive, size = "normal" }) => {
    const Icon = tab.icon;
    const sizeClasses = {
      normal: "px-6 py-3 text-base",
      medium: "px-4 py-2 text-sm",
      small: "px-3 py-1.5 text-sm"
    };

    return (
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => setActiveTab(tab.id)}
        className={cn(
          "flex items-center space-x-2 rounded-lg font-medium transition-all",
          sizeClasses[size],
          isActive
            ? "bg-primary text-primary-foreground shadow-lg"
            : "text-muted-foreground hover:text-foreground hover:bg-primary/10"
        )}
        title={tab.description}
      >
        <Icon className={cn("shrink-0", size === "small" ? "w-3 h-3" : "w-4 h-4")} />
        <span className="whitespace-nowrap">{tab.label}</span>
      </motion.button>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 via-blue-800 to-royal-blue-700 text-foreground dark">
      {/* Background effects - Floating cloudy shapes */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Ambient floating clouds */}
        <div className="absolute top-20 left-10 w-96 h-64 bg-blue-400/10 rounded-full filter blur-3xl animate-float-slow" style={{animationDelay: '0s'}}></div>
        <div className="absolute top-60 right-20 w-80 h-48 bg-indigo-300/8 rounded-[60%] filter blur-2xl animate-float-medium" style={{animationDelay: '3s'}}></div>
        <div className="absolute bottom-40 left-1/4 w-72 h-72 bg-purple-400/12 rounded-full filter blur-3xl animate-float-slow-reverse" style={{animationDelay: '7s'}}></div>
        <div className="absolute top-1/3 right-1/3 w-64 h-40 bg-blue-300/15 rounded-[70%] filter blur-xl animate-float-drift" style={{animationDelay: '5s'}}></div>
        <div className="absolute bottom-20 right-10 w-56 h-56 bg-cyan-400/10 rounded-full filter blur-2xl animate-float-gentle" style={{animationDelay: '2s'}}></div>
        <div className="absolute top-40 left-1/2 w-48 h-80 bg-indigo-400/8 rounded-[50%] filter blur-3xl animate-float-vertical" style={{animationDelay: '8s'}}></div>
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-border backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <LighthouseBeacon className="w-8 h-8" />
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Subjective Narrative Humanizer
                </h1>
                <p className="text-sm text-card-secondary">Mining the best of yourself through AI-assisted discovery</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsDark(!isDark)}
                className="p-2 rounded-lg bg-card hover:bg-muted transition-colors"
              >
                {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </motion.button>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation - Three Tier System */}
      <nav className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 space-y-3">
        {/* Core Discovery Tabs */}
        <div className="flex flex-wrap gap-1 bg-muted rounded-lg p-1">
          <div className="flex items-center px-3 py-2 text-xs text-card-secondary font-medium uppercase tracking-wider">
            Core Discovery
          </div>
          {coreDiscoveryTabs.map((tab) => (
            <TabButton
              key={tab.id}
              tab={tab}
              isActive={activeTab === tab.id}
              size="normal"
            />
          ))}
        </div>

        {/* Analysis Tools */}
        <div className="flex flex-wrap gap-1 bg-muted/80 rounded-lg p-1">
          <div className="flex items-center px-3 py-1.5 text-xs text-card-secondary font-medium uppercase tracking-wider">
            Analysis Tools
          </div>
          {analysisTools.map((tab) => (
            <TabButton
              key={tab.id}
              tab={tab}
              isActive={activeTab === tab.id}
              size="medium"
            />
          ))}
        </div>

        {/* System Tabs */}
        <div className="flex flex-wrap gap-1 bg-muted/60 rounded-lg p-1">
          <div className="flex items-center px-3 py-1 text-xs text-card-secondary font-medium uppercase tracking-wider">
            System
          </div>
          {systemTabs.map((tab) => (
            <TabButton
              key={tab.id}
              tab={tab}
              isActive={activeTab === tab.id}
              size="small"
            />
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-card/90 border border-border rounded-2xl min-h-[calc(100vh-300px)] backdrop-blur-md">
          <ErrorBoundary>
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                {isLoading ? (
                  <div className="h-full flex items-center justify-center">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      <Loader2 className="w-8 h-8 text-primary" />
                    </motion.div>
                  </div>
                ) : (
                  renderTabContent()
                )}
              </motion.div>
            </AnimatePresence>
          </ErrorBoundary>
        </div>
      </main>

      {/* Status Bar */}
      <footer className="relative z-10 border-t border-white/10 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center space-x-4">
              <span>Enhanced Lighthouse API</span>
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            </div>
            <div className="flex items-center space-x-4">
              <span>Quantum Narrative Engine</span>
              <span>•</span>
              <span>Local Privacy Mode</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;