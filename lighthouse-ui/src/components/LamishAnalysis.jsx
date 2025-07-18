import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Brain,
  Zap,
  FileText,
  BarChart3,
  Star,
  Loader2,
  ChevronRight,
  Copy,
  Check
} from "lucide-react";

const LamishAnalysis = () => {
  const [narrative, setNarrative] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleAnalyze = async () => {
    if (!narrative.trim()) return;

    setIsAnalyzing(true);
    setError(null);
    setAnalysis(null);

    try {
      const response = await fetch("/api/lamish/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ narrative }),
      });

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatEmbedding = (embedding) => {
    if (!embedding || embedding.length === 0) return "No embedding data";
    
    // Show first 10 dimensions with some statistical info
    const sample = embedding.slice(0, 10);
    const avg = embedding.reduce((a, b) => a + b, 0) / embedding.length;
    const max = Math.max(...embedding);
    const min = Math.min(...embedding);
    
    return {
      sample: sample.map(v => v.toFixed(4)),
      stats: { avg: avg.toFixed(4), max: max.toFixed(4), min: min.toFixed(4) },
      dimensions: embedding.length
    };
  };

  const getElementColor = (value) => {
    const intensity = Math.min(1, Math.max(0, value));
    const hue = intensity * 120; // Green to red spectrum
    return `hsl(${hue}, 70%, 50%)`;
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="w-6 h-6 text-purple-600" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Lamish Meaning Analysis
          </h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Narrative Text
            </label>
            <textarea
              value={narrative}
              onChange={(e) => setNarrative(e.target.value)}
              placeholder="Enter any narrative text to analyze its essence, derive optimal projection attributes, and see the lamish transformation..."
              className="w-full h-32 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
            />
          </div>
          
          <button
            onClick={handleAnalyze}
            disabled={!narrative.trim() || isAnalyzing}
            className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all duration-200 disabled:cursor-not-allowed"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing Essence...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                Analyze Lamish Meaning
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4"
        >
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </motion.div>
      )}

      {/* Analysis Results */}
      {analysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Suggested Attributes */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <Star className="w-5 h-5 text-yellow-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Suggested Projection Attributes
              </h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="text-sm text-blue-600 dark:text-blue-400 font-medium mb-1">Persona</div>
                <div className="text-lg font-semibold text-blue-900 dark:text-blue-100">
                  {analysis.suggested_attributes.persona}
                </div>
              </div>
              
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <div className="text-sm text-green-600 dark:text-green-400 font-medium mb-1">Namespace</div>
                <div className="text-lg font-semibold text-green-900 dark:text-green-100">
                  {analysis.suggested_attributes.namespace}
                </div>
              </div>
              
              <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <div className="text-sm text-purple-600 dark:text-purple-400 font-medium mb-1">Style</div>
                <div className="text-lg font-semibold text-purple-900 dark:text-purple-100">
                  {analysis.suggested_attributes.style}
                </div>
              </div>
            </div>
          </div>

          {/* Narrative Elements Analysis */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-5 h-5 text-indigo-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Narrative Element Analysis
              </h3>
            </div>
            
            <div className="space-y-3">
              {Object.entries(analysis.narrative_elements).map(([element, value]) => (
                <div key={element} className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                    {element.replace('_', ' ')}
                  </span>
                  <div className="flex items-center gap-3">
                    <div className="w-32 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full transition-all duration-300"
                        style={{
                          width: `${Math.min(100, value * 100)}%`,
                          backgroundColor: getElementColor(value)
                        }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400 w-12 text-right">
                      {(value * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Essence Embedding */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <Brain className="w-5 h-5 text-cyan-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Essence Embedding (Non-Textual Meaning)
              </h3>
            </div>
            
            {(() => {
              const embeddingData = formatEmbedding(analysis.essence_embedding);
              return (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="text-gray-600 dark:text-gray-400">Dimensions</div>
                      <div className="font-mono text-lg">{embeddingData.dimensions}</div>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="text-gray-600 dark:text-gray-400">Average</div>
                      <div className="font-mono text-lg">{embeddingData.stats.avg}</div>
                    </div>
                    <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="text-gray-600 dark:text-gray-400">Range</div>
                      <div className="font-mono text-sm">{embeddingData.stats.min} → {embeddingData.stats.max}</div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      First 10 dimensions (sample):
                    </div>
                    <div className="font-mono text-xs bg-gray-50 dark:bg-gray-700 p-3 rounded-lg overflow-x-auto">
                      [{embeddingData.sample.join(", ")}...]
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>

          {/* Lamish Projection */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-emerald-600" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Lamish Projection
                </h3>
              </div>
              <button
                onClick={() => copyToClipboard(analysis.lamish_projection)}
                className="inline-flex items-center gap-2 px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
            
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <div className="bg-gradient-to-r from-emerald-50 to-cyan-50 dark:from-emerald-900/20 dark:to-cyan-900/20 p-4 rounded-lg border border-emerald-200 dark:border-emerald-800">
                <p className="text-gray-800 dark:text-gray-200 leading-relaxed">
                  {analysis.lamish_projection}
                </p>
              </div>
            </div>
          </div>

          {/* Similar Concepts */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <ChevronRight className="w-5 h-5 text-orange-600" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Similar Concepts in Knowledge Base
              </h3>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {Object.entries(analysis.similar_concepts).map(([type, concepts]) => (
                <div key={type} className="space-y-3">
                  <h4 className="font-medium text-gray-900 dark:text-white capitalize">
                    {type}
                  </h4>
                  <div className="space-y-2">
                    {concepts.map((concept, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-sm text-gray-900 dark:text-white">
                            {concept.name}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {(concept.similarity * 100).toFixed(1)}% match
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
                          {concept.description}
                        </p>
                        <div className="flex items-center gap-2 mt-2 text-xs text-gray-500 dark:text-gray-400">
                          <span>Used: {concept.usage_count}</span>
                          <span>•</span>
                          <span>Quality: {(concept.quality_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default LamishAnalysis;