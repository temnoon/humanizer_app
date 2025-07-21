import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Cpu,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  Settings,
  Zap,
  Brain,
  Target,
  TrendingUp,
  TrendingDown,
  Info,
  RefreshCw,
  Download,
  Upload,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  Layers,
  GitBranch,
  Shuffle
} from 'lucide-react';

const AdvancedAttributeManager = () => {
  // State management
  const [activeTab, setActiveTab] = useState('analyze');
  const [selectedPersona, setSelectedPersona] = useState('philosopher');
  const [selectedNamespace, setSelectedNamespace] = useState('lamish-galaxy');
  const [selectedStyle, setSelectedStyle] = useState('poetic');
  const [narrativeText, setNarrativeText] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [transformationResult, setTransformationResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isTransforming, setIsTransforming] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [narrativeDNA, setNarrativeDNA] = useState(null);
  const [systemStats, setSystemStats] = useState(null);

  // API endpoints
  const API_BASE = 'http://localhost:8100';

  // Sample narratives for quick testing
  const sampleNarratives = {
    simple: "John walked to the store and bought milk. He returned home satisfied.",
    complex: "In the sprawling metropolis of New York, Sarah Chen navigated the complex web of corporate politics while pursuing her dream of becoming a renowned architect. Her mentor, Professor Williams, had warned her that the path would be treacherous, filled with compromises that could either elevate her vision or destroy her integrity. As she stood before the gleaming skyscraper that would either make or break her career, Sarah felt the weight of every decision that had led her to this moment.",
    philosophical: "What is the nature of consciousness? Is it merely an emergent property of complex neural networks, or does it represent something more fundamental about the universe itself? These questions have puzzled philosophers and scientists for centuries, yet we seem no closer to definitive answers than when we first began asking them."
  };

  useEffect(() => {
    loadSystemStats();
  }, []);

  const loadSystemStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/balanced/stats`);
      if (response.ok) {
        const stats = await response.json();
        setSystemStats(stats);
      }
    } catch (error) {
      console.error('Failed to load system stats:', error);
    }
  };

  const analyzeBalance = async () => {
    if (!narrativeText.trim()) {
      alert('Please enter a narrative to analyze');
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await fetch(`${API_BASE}/api/balanced/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          persona: selectedPersona,
          namespace: selectedNamespace,
          style: selectedStyle,
          narrative: narrativeText
        })
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
        setNarrativeDNA(result.narrative_dna);
      } else {
        console.error('Analysis failed:', await response.text());
      }
    } catch (error) {
      console.error('Analysis error:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const runBalancedTransformation = async () => {
    if (!narrativeText.trim()) {
      alert('Please enter a narrative to transform');
      return;
    }

    setIsTransforming(true);
    try {
      const response = await fetch(`${API_BASE}/api/balanced/transform`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          narrative: narrativeText,
          persona: selectedPersona,
          namespace: selectedNamespace,
          style: selectedStyle,
          show_steps: true,
          apply_balancing: true
        })
      });

      if (response.ok) {
        const result = await response.json();
        setTransformationResult(result);
      } else {
        console.error('Transformation failed:', await response.text());
      }
    } catch (error) {
      console.error('Transformation error:', error);
    } finally {
      setIsTransforming(false);
    }
  };

  const loadSampleNarrative = (type) => {
    setNarrativeText(sampleNarratives[type]);
    setAnalysisResult(null);
    setTransformationResult(null);
    setNarrativeDNA(null);
  };

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

  const renderAnalysisResults = () => {
    if (!analysisResult) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        {/* Balance Status */}
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Balance Analysis</h3>
            <div className={`flex items-center space-x-2 ${getBalanceStatusColor(analysisResult.is_balanced, analysisResult.template_risk_score)}`}>
              {getBalanceStatusIcon(analysisResult.is_balanced, analysisResult.template_risk_score)}
              <span className="font-medium">
                {analysisResult.is_balanced ? 'Well Balanced' : 'Needs Adjustment'}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-black/20 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Template Risk</span>
                <span className={`font-mono ${analysisResult.template_risk_score > 0.7 ? 'text-red-400' : analysisResult.template_risk_score > 0.4 ? 'text-yellow-400' : 'text-green-400'}`}>
                  {(analysisResult.template_risk_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                <div 
                  className={`h-2 rounded-full ${analysisResult.template_risk_score > 0.7 ? 'bg-red-500' : analysisResult.template_risk_score > 0.4 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${analysisResult.template_risk_score * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-black/20 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Preservation Score</span>
                <span className={`font-mono ${analysisResult.preservation_score > 0.7 ? 'text-green-400' : analysisResult.preservation_score > 0.4 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {(analysisResult.preservation_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                <div 
                  className={`h-2 rounded-full ${analysisResult.preservation_score > 0.7 ? 'bg-green-500' : analysisResult.preservation_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${analysisResult.preservation_score * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-black/20 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Conflicts</span>
                <span className={`font-mono ${analysisResult.conflicts.length === 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {analysisResult.conflicts.length}
                </span>
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {analysisResult.conflicts.length > 0 ? analysisResult.conflicts.join(', ') : 'None detected'}
              </div>
            </div>
          </div>

          {/* Issues and Suggestions */}
          {(analysisResult.dominant_attributes.length > 0 || analysisResult.conflicts.length > 0 || analysisResult.suggestions.length > 0) && (
            <div className="mt-6 space-y-4">
              {analysisResult.dominant_attributes.length > 0 && (
                <div className="bg-orange-900/20 border border-orange-500/30 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <AlertTriangle className="w-4 h-4 text-orange-400" />
                    <span className="font-medium text-orange-300">Dominant Attributes</span>
                  </div>
                  <p className="text-orange-200 text-sm">
                    {analysisResult.dominant_attributes.join(', ')} may overpower the transformation
                  </p>
                </div>
              )}

              {analysisResult.suggestions.length > 0 && (
                <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Info className="w-4 h-4 text-blue-400" />
                    <span className="font-medium text-blue-300">Suggestions</span>
                  </div>
                  <ul className="text-blue-200 text-sm space-y-1">
                    {analysisResult.suggestions.map((suggestion, index) => (
                      <li key={index}>• {suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Narrative DNA */}
        {narrativeDNA && (
          <div className="bg-white/5 rounded-xl p-6 border border-white/10">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-white flex items-center space-x-2">
                <Brain className="w-5 h-5 text-purple-400" />
                <span>Narrative DNA</span>
              </h3>
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center space-x-1 text-purple-400 hover:text-purple-300 transition-colors"
              >
                {showAdvanced ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                <span>{showAdvanced ? 'Hide' : 'Show'} Details</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div className="bg-black/20 rounded-lg p-4">
                <span className="text-gray-300 text-sm">Complexity Score</span>
                <div className="text-xl font-mono text-white">
                  {(narrativeDNA.complexity_score * 100).toFixed(1)}%
                </div>
              </div>
              <div className="bg-black/20 rounded-lg p-4">
                <span className="text-gray-300 text-sm">Semantic Density</span>
                <div className="text-xl font-mono text-white">
                  {(narrativeDNA.semantic_density * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <AnimatePresence>
              {showAdvanced && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-4"
                >
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-300 mb-2">Core Entities</h4>
                      <div className="bg-black/20 rounded-lg p-3 max-h-32 overflow-y-auto">
                        {narrativeDNA.core_entities.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {narrativeDNA.core_entities.map((entity, index) => (
                              <span key={index} className="px-2 py-1 bg-purple-600/20 text-purple-300 rounded text-xs">
                                {entity}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-gray-500 text-sm">None detected</span>
                        )}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-300 mb-2">Thematic Elements</h4>
                      <div className="bg-black/20 rounded-lg p-3 max-h-32 overflow-y-auto">
                        {narrativeDNA.thematic_elements.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {narrativeDNA.thematic_elements.map((theme, index) => (
                              <span key={index} className="px-2 py-1 bg-blue-600/20 text-blue-300 rounded text-xs">
                                {theme}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-gray-500 text-sm">None detected</span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-2">Emotional Trajectory</h4>
                    <div className="bg-black/20 rounded-lg p-3 max-h-24 overflow-y-auto">
                      {narrativeDNA.emotional_trajectory.length > 0 ? (
                        <div className="text-sm text-gray-300 space-y-1">
                          {narrativeDNA.emotional_trajectory.map((emotion, index) => (
                            <div key={index} className="text-xs">{emotion}</div>
                          ))}
                        </div>
                      ) : (
                        <span className="text-gray-500 text-sm">No emotional trajectory detected</span>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </motion.div>
    );
  };

  const renderTransformationResults = () => {
    if (!transformationResult) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        {/* Transformation Overview */}
        <div className="bg-white/5 rounded-xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Transformation Results</h3>
            <div className="flex items-center space-x-4 text-sm text-gray-300">
              <span>Processing Time: {transformationResult.processing_time_ms}ms</span>
              <span className={`px-2 py-1 rounded ${transformationResult.overall_preservation_score > 0.7 ? 'bg-green-600/20 text-green-300' : transformationResult.overall_preservation_score > 0.4 ? 'bg-yellow-600/20 text-yellow-300' : 'bg-red-600/20 text-red-300'}`}>
                Preservation: {(transformationResult.overall_preservation_score * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Original vs Transformed */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-2">Original Narrative</h4>
              <div className="bg-black/20 rounded-lg p-4 max-h-48 overflow-y-auto">
                <p className="text-gray-100 text-sm leading-relaxed">{transformationResult.original_narrative}</p>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-2">Transformed Narrative</h4>
              <div className="bg-black/20 rounded-lg p-4 max-h-48 overflow-y-auto">
                <p className="text-gray-100 text-sm leading-relaxed">{transformationResult.transformed_narrative}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Transformation Steps */}
        {transformationResult.steps && transformationResult.steps.length > 0 && (
          <div className="bg-white/5 rounded-xl p-6 border border-white/10">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
              <GitBranch className="w-5 h-5 text-green-400" />
              <span>Transformation Pipeline</span>
            </h3>

            <div className="space-y-4">
              {transformationResult.steps.map((step, index) => (
                <div key={index} className="bg-black/20 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-white">{step.name}</h4>
                    <div className="flex items-center space-x-4 text-xs text-gray-400">
                      <span>Preservation: {(step.preservation_score * 100).toFixed(1)}%</span>
                      <span>DNA Drift: {(step.dna_drift_score * 100).toFixed(1)}%</span>
                      <span>{step.duration_ms}ms</span>
                      {step.balancing_applied && (
                        <span className="px-2 py-1 bg-blue-600/20 text-blue-300 rounded">
                          Balanced
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Input:</span>
                      <p className="text-gray-300 mt-1">{step.input_snapshot}</p>
                    </div>
                    <div>
                      <span className="text-gray-400">Output:</span>
                      <p className="text-gray-300 mt-1">{step.output_snapshot}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Metrics */}
        {transformationResult.performance_metrics && (
          <div className="bg-white/5 rounded-xl p-6 border border-white/10">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-blue-400" />
              <span>Performance Metrics</span>
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-black/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-mono text-white">
                  {transformationResult.performance_metrics.total_transformations || 0}
                </div>
                <div className="text-xs text-gray-400">Total Transformations</div>
              </div>
              
              <div className="bg-black/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-mono text-green-400">
                  {transformationResult.performance_metrics.templates_avoided || 0}
                </div>
                <div className="text-xs text-gray-400">Templates Avoided</div>
              </div>
              
              <div className="bg-black/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-mono text-blue-400">
                  {(transformationResult.performance_metrics.avg_preservation_score * 100 || 0).toFixed(1)}%
                </div>
                <div className="text-xs text-gray-400">Avg Preservation</div>
              </div>
              
              <div className="bg-black/20 rounded-lg p-4 text-center">
                <div className="text-2xl font-mono text-purple-400">
                  {((transformationResult.performance_metrics.template_avoidance_rate || 0) * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-gray-400">Template Avoidance</div>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center justify-center space-x-3">
          <Cpu className="w-8 h-8 text-purple-400" />
          <span>Advanced Attribute Manager</span>
        </h1>
        <p className="text-gray-300">
          Sophisticated narrative transformation with template avoidance and DNA preservation
        </p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-black/20 rounded-lg p-1">
        {[
          { id: 'analyze', label: 'Balance Analysis', icon: Target },
          { id: 'transform', label: 'Balanced Transform', icon: Zap },
          { id: 'stats', label: 'System Stats', icon: BarChart3 }
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-md transition-colors ${
                activeTab === tab.id 
                  ? 'bg-purple-600 text-white' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'analyze' && (
          <motion.div
            key="analyze"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-6"
          >
            {/* Input Section */}
            <div className="bg-white/5 rounded-xl p-6 border border-white/10">
              <h2 className="text-xl font-semibold text-white mb-4">Narrative & Attributes</h2>
              
              {/* Sample Narratives */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-300 mb-2">Quick Test Narratives</label>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(sampleNarratives).map(([type, _]) => (
                    <button
                      key={type}
                      onClick={() => loadSampleNarrative(type)}
                      className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-sm rounded transition-colors"
                    >
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Narrative Input */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">Narrative Text</label>
                <textarea
                  value={narrativeText}
                  onChange={(e) => setNarrativeText(e.target.value)}
                  placeholder="Enter your narrative here..."
                  className="w-full h-32 p-3 bg-black/20 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:border-purple-400 focus:outline-none resize-none"
                />
              </div>

              {/* Attribute Selection */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Persona</label>
                  <select
                    value={selectedPersona}
                    onChange={(e) => setSelectedPersona(e.target.value)}
                    className="w-full p-3 bg-black/20 border border-white/10 rounded-lg text-white focus:border-purple-400 focus:outline-none"
                  >
                    <option value="philosopher">Philosopher</option>
                    <option value="storyteller">Storyteller</option>
                    <option value="scientist">Scientist</option>
                    <option value="critic">Critic</option>
                    <option value="artist">Artist</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Namespace</label>
                  <select
                    value={selectedNamespace}
                    onChange={(e) => setSelectedNamespace(e.target.value)}
                    className="w-full p-3 bg-black/20 border border-white/10 rounded-lg text-white focus:border-purple-400 focus:outline-none"
                  >
                    <option value="lamish-galaxy">Lamish Galaxy</option>
                    <option value="corporate-dystopia">Corporate Dystopia</option>
                    <option value="medieval-fantasy">Medieval Fantasy</option>
                    <option value="quantum-realm">Quantum Realm</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Style</label>
                  <select
                    value={selectedStyle}
                    onChange={(e) => setSelectedStyle(e.target.value)}
                    className="w-full p-3 bg-black/20 border border-white/10 rounded-lg text-white focus:border-purple-400 focus:outline-none"
                  >
                    <option value="poetic">Poetic</option>
                    <option value="technical">Technical</option>
                    <option value="formal">Formal</option>
                    <option value="casual">Casual</option>
                    <option value="archaic">Archaic</option>
                  </select>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-4">
                <button
                  onClick={analyzeBalance}
                  disabled={isAnalyzing || !narrativeText.trim()}
                  className="flex items-center space-x-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                >
                  {isAnalyzing ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Target className="w-4 h-4" />
                  )}
                  <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Balance'}</span>
                </button>

                <button
                  onClick={runBalancedTransformation}
                  disabled={isTransforming || !narrativeText.trim()}
                  className="flex items-center space-x-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                >
                  {isTransforming ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Zap className="w-4 h-4" />
                  )}
                  <span>{isTransforming ? 'Transforming...' : 'Balanced Transform'}</span>
                </button>
              </div>
            </div>

            {/* Analysis Results */}
            {renderAnalysisResults()}
          </motion.div>
        )}

        {activeTab === 'transform' && (
          <motion.div
            key="transform"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            {renderTransformationResults()}
          </motion.div>
        )}

        {activeTab === 'stats' && (
          <motion.div
            key="stats"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="space-y-6"
          >
            {/* System Statistics */}
            <div className="bg-white/5 rounded-xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-white">System Statistics</h2>
                <button
                  onClick={loadSystemStats}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh</span>
                </button>
              </div>

              {systemStats ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-black/20 rounded-lg p-4 text-center">
                    <div className="text-2xl font-mono text-white">
                      {systemStats.total_transformations || 0}
                    </div>
                    <div className="text-xs text-gray-400">Total Transformations</div>
                  </div>
                  
                  <div className="bg-black/20 rounded-lg p-4 text-center">
                    <div className="text-2xl font-mono text-green-400">
                      {systemStats.templates_avoided || 0}
                    </div>
                    <div className="text-xs text-gray-400">Templates Avoided</div>
                  </div>
                  
                  <div className="bg-black/20 rounded-lg p-4 text-center">
                    <div className="text-2xl font-mono text-blue-400">
                      {((systemStats.avg_preservation_score || 0) * 100).toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-400">Avg Preservation</div>
                  </div>
                  
                  <div className="bg-black/20 rounded-lg p-4 text-center">
                    <div className="text-2xl font-mono text-purple-400">
                      {systemStats.total_registered_attributes || 0}
                    </div>
                    <div className="text-xs text-gray-400">Registered Attributes</div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <RefreshCw className="w-8 h-8 mx-auto mb-2 animate-spin" />
                  <p>Loading system statistics...</p>
                </div>
              )}
            </div>

            {/* System Status */}
            <div className="bg-white/5 rounded-xl p-6 border border-white/10">
              <h3 className="text-lg font-semibold text-white mb-4">System Health</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Attribute Balancing System</span>
                  <div className="flex items-center space-x-2 text-green-400">
                    <CheckCircle className="w-4 h-4" />
                    <span>Operational</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">DNA Extraction System</span>
                  <div className="flex items-center space-x-2 text-green-400">
                    <CheckCircle className="w-4 h-4" />
                    <span>Operational</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Template Detection</span>
                  <div className="flex items-center space-x-2 text-green-400">
                    <CheckCircle className="w-4 h-4" />
                    <span>Active</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdvancedAttributeManager;