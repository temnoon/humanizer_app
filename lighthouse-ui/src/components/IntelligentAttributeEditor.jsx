import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Zap,
  Target,
  Lightbulb,
  Settings,
  RefreshCw,
  Eye,
  Edit3,
  Check,
  X,
  ChevronDown,
  ChevronRight,
  Cpu,
  Activity,
  BarChart3,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import { cn } from '../utils';

/**
 * Intelligent Attribute Editor
 * 
 * Dynamic attribute selection using AI analysis of narrative content.
 * Replaces static dropdowns with intelligent recommendations and 
 * provides detailed pipeline preview and quantum analysis.
 */
const IntelligentAttributeEditor = ({ 
  narrative = '', 
  onAttributesChange = () => {},
  onAnalysisComplete = () => {},
  className = '' 
}) => {
  // Component state
  const [mode, setMode] = useState('ai'); // 'ai', 'manual', 'hybrid'
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [currentAttributes, setCurrentAttributes] = useState({
    persona: 'philosopher',
    namespace: 'philosophical', 
    style: 'contemplative'
  });
  const [showDetails, setShowDetails] = useState(false);
  const [showPipelinePreview, setShowPipelinePreview] = useState(false);
  const [taxonomy, setTaxonomy] = useState(null);
  const [error, setError] = useState(null);
  const [pipelinePreview, setPipelinePreview] = useState(null);

  // Load attribute taxonomy on mount
  useEffect(() => {
    loadTaxonomy();
  }, []);

  // Auto-analyze when narrative changes (debounced)
  useEffect(() => {
    if (narrative && narrative.length > 10 && mode === 'ai') {
      const timeout = setTimeout(() => {
        analyzeNarrative();
      }, 1000);
      return () => clearTimeout(timeout);
    }
  }, [narrative, mode]);

  const loadTaxonomy = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8100/api/intelligent-attributes/taxonomy');
      if (response.ok) {
        const data = await response.json();
        setTaxonomy(data);
      }
    } catch (err) {
      console.error('Failed to load taxonomy:', err);
    }
  };

  const analyzeNarrative = async () => {
    if (!narrative || narrative.length < 10) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8100/api/intelligent-attributes/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          narrative: narrative,
          transformation_intent: 'enhance',
          use_llm_analysis: true
        })
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.status}`);
      }

      const data = await response.json();
      setAnalysis(data);
      
      // Update current attributes with AI recommendations
      const newAttributes = data.selected_attributes;
      setCurrentAttributes(newAttributes);
      
      // Notify parent component
      onAttributesChange(newAttributes);
      onAnalysisComplete(data);
      
    } catch (err) {
      console.error('Attribute analysis failed:', err);
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const previewPipeline = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8100/api/intelligent-attributes/pipeline-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          attributes: currentAttributes,
          narrative: narrative
        })
      });

      if (response.ok) {
        const data = await response.json();
        setPipelinePreview(data);
        setShowPipelinePreview(true);
      }
    } catch (err) {
      console.error('Pipeline preview failed:', err);
    }
  };

  const handleManualAttributeChange = async (attribute, value) => {
    const newAttributes = { ...currentAttributes, [attribute]: value };
    setCurrentAttributes(newAttributes);
    onAttributesChange(newAttributes);

    // If in hybrid mode, get AI feedback on manual change
    if (mode === 'hybrid' && narrative) {
      try {
        const response = await fetch('http://127.0.0.1:8100/api/intelligent-attributes/edit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            current_attributes: newAttributes,
            narrative: narrative,
            edit_type: 'manual',
            target_attribute: attribute,
            target_value: value
          })
        });

        if (response.ok) {
          const data = await response.json();
          // Update with AI suggestions but don't override manual choice
          setAnalysis(prev => prev ? {
            ...prev,
            alternatives: data.suggestions,
            confidence: data.confidence
          } : null);
        }
      } catch (err) {
        console.error('Edit feedback failed:', err);
      }
    }
  };

  const applyAlternative = (alternative) => {
    setCurrentAttributes(alternative);
    onAttributesChange(alternative);
  };

  const renderAttributeSelector = (attribute, options) => {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
          {attribute}
          {analysis && (
            <span className="ml-2 text-xs text-purple-500">
              (AI confidence: {(analysis.confidence * 100).toFixed(0)}%)
            </span>
          )}
        </label>
        <select
          value={currentAttributes[attribute]}
          onChange={(e) => handleManualAttributeChange(attribute, e.target.value)}
          className="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
        >
          {options.map(option => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
        {taxonomy && taxonomy.taxonomy[attribute]?.[currentAttributes[attribute]] && (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {taxonomy.taxonomy[attribute][currentAttributes[attribute]]}
          </p>
        )}
      </div>
    );
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Mode Selection */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-500" />
            Attribute Selection
          </h3>
          <div className="flex items-center space-x-2">
            <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
              {[
                { id: 'ai', label: 'AI-Guided', icon: Brain },
                { id: 'hybrid', label: 'Hybrid', icon: Layers },
                { id: 'manual', label: 'Manual', icon: Settings }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setMode(id)}
                  className={cn(
                    "flex items-center gap-1 px-3 py-1 rounded text-sm font-medium transition-colors",
                    mode === id
                      ? "bg-purple-600 text-white"
                      : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
                  )}
                >
                  <Icon className="w-3 h-3" />
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* AI Analysis Button */}
        {mode !== 'manual' && (
          <div className="flex items-center gap-3 mb-4">
            <button
              onClick={analyzeNarrative}
              disabled={isAnalyzing || !narrative || narrative.length < 10}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all",
                "bg-purple-600 hover:bg-purple-700 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              {isAnalyzing ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Analyze Narrative
                </>
              )}
            </button>
            
            {analysis && (
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="flex items-center gap-2 px-3 py-2 text-sm text-purple-600 hover:text-purple-700"
              >
                <Eye className="w-4 h-4" />
                {showDetails ? 'Hide' : 'Show'} Details
              </button>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-4">
            <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
              <X className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          </div>
        )}

        {/* Attribute Selectors */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {taxonomy && Object.keys(taxonomy.taxonomy).map(attribute => (
            <div key={attribute}>
              {renderAttributeSelector(attribute, Object.keys(taxonomy.taxonomy[attribute]))}
            </div>
          ))}
        </div>

        {/* AI Analysis Results */}
        <AnimatePresence>
          {analysis && showDetails && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-6 space-y-4"
            >
              {/* AI Reasoning */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <Lightbulb className="w-4 h-4 text-yellow-500" />
                  AI Reasoning
                </h4>
                <p className="text-sm text-gray-700 dark:text-gray-300">{analysis.reasoning}</p>
              </div>

              {/* Alternative Suggestions */}
              {analysis.alternatives && analysis.alternatives.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                    <Target className="w-4 h-4 text-green-500" />
                    Alternative Combinations
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {analysis.alternatives.map((alt, idx) => (
                      <button
                        key={idx}
                        onClick={() => applyAlternative(alt)}
                        className="text-left p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                      >
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {alt.persona} • {alt.namespace} • {alt.style}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {alt.reason}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Quantum Analysis */}
              {analysis.quantum_analysis && (
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-blue-500" />
                    Quantum Representation
                  </h4>
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">POVM Coordinates:</span>
                      <div className="text-gray-800 dark:text-gray-200 font-mono">
                        {analysis.quantum_analysis ? 'Computed' : 'Not available'}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-600 dark:text-gray-400">Semantic Position:</span>
                      <div className="text-gray-800 dark:text-gray-200">
                        Embedding space mapped
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Pipeline Preview Button */}
        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={previewPipeline}
            disabled={!narrative}
            className="flex items-center gap-2 px-4 py-2 text-sm text-blue-600 hover:text-blue-700 disabled:opacity-50"
          >
            <Eye className="w-4 h-4" />
            Preview Transformation Pipeline
          </button>
          
          {analysis && (
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <BarChart3 className="w-4 h-4" />
              Confidence: {(analysis.confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      </div>

      {/* Pipeline Preview Modal */}
      <AnimatePresence>
        {showPipelinePreview && pipelinePreview && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Zap className="w-5 h-5 text-purple-500" />
                  Transformation Pipeline Preview
                </h3>
                <button
                  onClick={() => setShowPipelinePreview(false)}
                  className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Pipeline Steps */}
              <div className="space-y-4 mb-6">
                <h4 className="font-medium text-gray-900 dark:text-white">Processing Steps</h4>
                <div className="space-y-2">
                  {pipelinePreview.estimated_steps.map((step, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900 dark:text-white">{step.step}</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">{step.description}</div>
                      </div>
                      <div className="text-xs text-gray-500">{step.duration}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Prompt Components */}
              <div className="space-y-4 mb-6">
                <h4 className="font-medium text-gray-900 dark:text-white">Prompt Construction</h4>
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
                  <div className="space-y-2">
                    <div><span className="text-gray-500"># System Prompt:</span></div>
                    <div className="pl-2">{pipelinePreview.prompt_components.full_system_prompt}</div>
                  </div>
                </div>
              </div>

              {/* Quantum Coordinates */}
              {pipelinePreview.quantum_coordinates && (
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-blue-500" />
                    Quantum Semantic Coordinates
                  </h4>
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                    <div className="text-sm text-gray-700 dark:text-gray-300">
                      <p className="mb-2">POVM measurement probabilities across {pipelinePreview.quantum_coordinates.length} semantic dimensions:</p>
                      <div className="grid grid-cols-8 gap-1">
                        {pipelinePreview.quantum_coordinates.slice(0, 16).map((coord, idx) => (
                          <div key={idx} className="text-center">
                            <div className="text-xs text-gray-500">D{idx + 1}</div>
                            <div className="font-mono text-xs">{(coord * 100).toFixed(1)}%</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default IntelligentAttributeEditor;