import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Zap,
  Eye,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Activity,
  Target,
  Layers,
  BarChart3,
  Info,
  Atom
} from 'lucide-react';
import { cn } from '../utils';

/**
 * Semantic Tomography Visualization Component
 * 
 * Visualizes the quantum narrative theory in action:
 * - Before/after meaning-state probabilities
 * - POVM measurement outcomes
 * - Transformation metrics (fidelity, purity, entropy)
 * - Coherence analysis
 */
const SemanticTomography = ({ className = '' }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [tomographyData, setTomographyData] = useState(null);
  const [inputText, setInputText] = useState('');
  const [readingStyle, setReadingStyle] = useState('interpretation');
  const [error, setError] = useState(null);

  const analyzeText = async () => {
    if (!inputText.trim()) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8100/api/narrative-theory/semantic-tomography', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          transformation_attributes: {
            persona: 'analytical',
            namespace: 'scientific',
            style: 'formal'
          },
          reading_style: readingStyle
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      const data = await response.json();
      setTomographyData(data);
    } catch (err) {
      console.error('Semantic tomography failed:', err);
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const checkEngineStatus = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8100/api/narrative-theory/status');
      if (response.ok) {
        const status = await response.json();
        if (!status.available) {
          setError('Quantum Narrative Theory engine not available');
        }
      }
    } catch (err) {
      setError('Cannot connect to narrative theory engine');
    }
  };

  useEffect(() => {
    checkEngineStatus();
  }, []);

  const renderProbabilityBar = (label, probability, maxProb = 1.0) => {
    const percentage = (probability / maxProb) * 100;
    
    return (
      <div key={label} className="mb-2">
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
            {label}
          </span>
          <span className="text-xs text-gray-500">
            {(probability * 100).toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <motion.div 
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </div>
      </div>
    );
  };

  const renderMeaningState = (state, title, icon) => {
    const Icon = icon;
    const maxProb = Math.max(...Object.values(state.canonical_probabilities));
    
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <Icon className="w-5 h-5 text-purple-600" />
          <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {state.purity.toFixed(3)}
            </div>
            <div className="text-xs text-gray-500">Purity</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {state.entropy.toFixed(3)}
            </div>
            <div className="text-xs text-gray-500">Entropy</div>
          </div>
        </div>
        
        <div className="space-y-1">
          {Object.entries(state.canonical_probabilities)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 6) // Show top 6 semantic dimensions
            .map(([label, prob]) => renderProbabilityBar(label, prob, maxProb))}
        </div>
      </div>
    );
  };

  return (
    <div className={cn("max-w-6xl mx-auto p-6 space-y-6", className)}>
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-6 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Atom className="w-8 h-8" />
          <h1 className="text-3xl font-bold">Semantic Tomography</h1>
        </div>
        <p className="text-purple-100">
          Quantum narrative theory visualization: See how narratives transform consciousness via measurement
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Analyze Narrative Text
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Text to Analyze
            </label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter text to analyze its semantic quantum state..."
              className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none focus:border-purple-400 focus:outline-none"
            />
          </div>
          
          <div className="flex items-center gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Reading Style
              </label>
              <select
                value={readingStyle}
                onChange={(e) => setReadingStyle(e.target.value)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:border-purple-400 focus:outline-none"
              >
                <option value="interpretation">Interpretation</option>
                <option value="skeptical">Skeptical</option>
                <option value="devotional">Devotional</option>
              </select>
            </div>
            
            <div className="flex-1" />
            
            <button
              onClick={analyzeText}
              disabled={isAnalyzing || !inputText.trim()}
              className="flex items-center gap-2 px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              {isAnalyzing ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Brain className="w-4 h-4" />
                  Analyze
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
            <Info className="w-5 h-5" />
            <span className="font-medium">Error:</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Results */}
      {tomographyData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-6"
        >
          {/* Transformation Overview */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Transformation Overview
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {tomographyData.transformation_metrics.fidelity.toFixed(3)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Fidelity</div>
                <div className="text-xs text-gray-500 mt-1">
                  Similarity between states
                </div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className={cn(
                  "text-2xl font-bold",
                  tomographyData.transformation_metrics.purity_change > 0 ? "text-green-600" : "text-red-600"
                )}>
                  {tomographyData.transformation_metrics.purity_change > 0 ? '+' : ''}
                  {tomographyData.transformation_metrics.purity_change.toFixed(3)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Purity Change</div>
                <div className="text-xs text-gray-500 mt-1">
                  {tomographyData.transformation_metrics.purity_change > 0 ? 'More focused' : 'More mixed'}
                </div>
              </div>
              
              <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className={cn(
                  "text-2xl font-bold",
                  tomographyData.transformation_metrics.entropy_change > 0 ? "text-orange-600" : "text-blue-600"
                )}>
                  {tomographyData.transformation_metrics.entropy_change > 0 ? '+' : ''}
                  {tomographyData.transformation_metrics.entropy_change.toFixed(3)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Entropy Change</div>
                <div className="text-xs text-gray-500 mt-1">
                  {tomographyData.transformation_metrics.entropy_change > 0 ? 'More uncertain' : 'More certain'}
                </div>
              </div>
            </div>
          </div>

          {/* Before/After States */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {renderMeaningState(tomographyData.before_state, "Before Reading", Eye)}
            
            <div className="flex items-center justify-center lg:hidden">
              <ArrowRight className="w-8 h-8 text-purple-600" />
            </div>
            
            {renderMeaningState(tomographyData.after_state, "After Reading", Brain)}
          </div>

          {/* Measurement Outcome */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-4">
              <Target className="w-5 h-5 text-green-600" />
              <h3 className="font-semibold text-gray-900 dark:text-white">POVM Measurement Outcome</h3>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(tomographyData.measurement_outcome)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 8)
                .map(([label, prob]) => (
                  <div key={label} className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-lg font-bold text-green-600">
                      {(prob * 100).toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      {label}
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* POVM Structure */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-4">
              <Layers className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold text-gray-900 dark:text-white">POVM Structure</h3>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-xl font-bold text-blue-600">
                  {tomographyData.povm_structure.dimension}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Dimension</div>
              </div>
              <div>
                <div className="text-xl font-bold text-purple-600">
                  {tomographyData.povm_structure.num_elements}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Elements</div>
              </div>
              <div>
                <div className="text-xl font-bold text-green-600">
                  {tomographyData.povm_structure.is_sic_like ? 'Yes' : 'No'}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">SIC-like</div>
              </div>
              <div>
                <div className="text-xl font-bold text-orange-600">
                  {tomographyData.transformation_type}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Reading Style</div>
              </div>
            </div>
          </div>

          {/* Theory Explanation */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
              Understanding the Quantum Narrative Theory
            </h3>
            <div className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <p>
                <strong>Meaning-State (ρ):</strong> A quantum-like density matrix representing how meaning is distributed across semantic dimensions before reading.
              </p>
              <p>
                <strong>POVM Measurement:</strong> The narrative acts as a set of semantic detectors that "measure" different interpretations with various probabilities.
              </p>
              <p>
                <strong>State Update:</strong> Reading collapses the meaning-state to a new configuration, changing purity and entropy based on the reading style.
              </p>
              <p>
                <strong>Fidelity:</strong> Measures how similar the before/after states are (1 = identical, 0 = orthogonal).
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default SemanticTomography;