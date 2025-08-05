import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Plus,
  Minus,
  Zap,
  Target,
  RefreshCw,
  BookOpen,
  Eye,
  Settings,
  Layers,
  ArrowRight,
  Copy,
  Sparkles,
  Brain,
  Compass,
  Filter,
  Tag,
  Atom,
  Workflow,
  RotateCcw,
  Play
} from "lucide-react";

const ProjectionTransformationInterface = ({ onNavigate }) => {
  const [inputText, setInputText] = useState("");
  const [transformedText, setTransformedText] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Vocabulary state
  const [vocabularyHealth, setVocabularyHealth] = useState(null);
  const [sourceAttributes, setSourceAttributes] = useState({
    persona: [],
    namespace: [],
    style: []
  });
  
  // Projection targets
  const [personaTerms, setPersonaTerms] = useState([]);
  const [namespaceTerms, setNamespaceTerms] = useState([]);
  const [styleTerms, setStyleTerms] = useState([]);
  const [guidanceWords, setGuidanceWords] = useState([]);
  const [guidanceSymbols, setGuidanceSymbols] = useState([]);
  
  // Search and suggestion state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeCategory, setActiveCategory] = useState("persona");
  
  // Projection settings
  const [projectionIntensity, setProjectionIntensity] = useState(1.0);
  const [readingStyle, setReadingStyle] = useState("interpretation");
  const [semanticDimension, setSemanticDimension] = useState(32);
  const [transformationMethod, setTransformationMethod] = useState("vocabulary");
  
  // Results and analysis
  const [transformationResult, setTransformationResult] = useState(null);
  const [showAnalysis, setShowAnalysis] = useState(false);

  useEffect(() => {
    checkVocabularyHealth();
  }, []);

  const checkVocabularyHealth = async () => {
    try {
      const response = await fetch('http://localhost:8100/api/vocabulary/health');
      if (response.ok) {
        const health = await response.json();
        setVocabularyHealth(health);
      } else {
        setVocabularyHealth({ status: 'error', error: 'API unavailable' });
      }
    } catch (error) {
      setVocabularyHealth({ status: 'error', error: error.message });
    }
  };

  const extractSourceAttributes = async () => {
    if (!inputText.trim()) return;

    try {
      const response = await fetch('http://localhost:8100/api/vocabulary/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: inputText,
          extract_new: true
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSourceAttributes({
          persona: data.persona,
          namespace: data.namespace,
          style: data.style
        });
      }
    } catch (error) {
      console.error('Failed to extract source attributes:', error);
    }
  };

  const searchVocabulary = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const response = await fetch('http://localhost:8100/api/vocabulary/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          category: activeCategory === 'all' ? null : activeCategory,
          max_results: 10
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results);
      }
    } catch (error) {
      console.error('Vocabulary search failed:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const addAttributeToProjection = (term, category) => {
    switch (category) {
      case 'persona':
        if (!personaTerms.includes(term)) {
          setPersonaTerms([...personaTerms, term]);
        }
        break;
      case 'namespace':
        if (!namespaceTerms.includes(term)) {
          setNamespaceTerms([...namespaceTerms, term]);
        }
        break;
      case 'style':
        if (!styleTerms.includes(term)) {
          setStyleTerms([...styleTerms, term]);
        }
        break;
    }
  };

  const removeAttributeFromProjection = (term, category) => {
    switch (category) {
      case 'persona':
        setPersonaTerms(personaTerms.filter(t => t !== term));
        break;
      case 'namespace':
        setNamespaceTerms(namespaceTerms.filter(t => t !== term));
        break;
      case 'style':
        setStyleTerms(styleTerms.filter(t => t !== term));
        break;
    }
  };

  const addGuidanceWord = () => {
    const word = prompt("Enter guidance word:");
    if (word && word.trim() && !guidanceWords.includes(word.trim())) {
      setGuidanceWords([...guidanceWords, word.trim()]);
    }
  };

  const performProjectionTransformation = async () => {
    if (!inputText.trim()) return;

    setIsProcessing(true);
    try {
      const transformationRequest = {
        input_text: inputText,
        persona_terms: personaTerms,
        namespace_terms: namespaceTerms,
        style_terms: styleTerms,
        guidance_words: guidanceWords,
        guidance_symbols: guidanceSymbols,
        projection_intensity: projectionIntensity,
        use_vocabulary_system: true,
        extract_source_attributes: true,
        reading_style: readingStyle,
        semantic_dimension: semanticDimension,
        transformation_method: transformationMethod,
        enable_logging: true,
        validate_coherence: true
      };

      console.log('🚀 Performing projection transformation:', transformationRequest);

      const response = await fetch('http://localhost:8100/api/density-matrix/transform', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transformationRequest)
      });

      if (response.ok) {
        const result = await response.json();
        
        if (result.success) {
          setTransformationResult(result);
          setTransformedText(result.transformed_text);
          
          // Update source attributes if extracted
          if (result.source_attributes) {
            setSourceAttributes(result.source_attributes);
          }
        } else {
          throw new Error(result.error_message || 'Transformation failed');
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API Error: ${response.status}`);
      }
    } catch (error) {
      console.error('❌ Projection transformation failed:', error);
      setTransformedText(`❌ TRANSFORMATION FAILED: ${error.message}\n\nThe projection-based transformation system encountered an error. Please check that:\n1. The vocabulary system is operational\n2. Projection targets are properly defined\n3. The density matrix API is available\n\nNo fallback is provided - only real mathematical projections are supported.`);
    } finally {
      setIsProcessing(false);
    }
  };

  const AttributeTag = ({ term, category, onRemove, source = false }) => (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.8, opacity: 0 }}
      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
        source 
          ? 'bg-blue-100 text-blue-800 border border-blue-200'
          : category === 'persona' ? 'bg-purple-100 text-purple-800 border border-purple-200'
          : category === 'namespace' ? 'bg-green-100 text-green-800 border border-green-200'
          : 'bg-orange-100 text-orange-800 border border-orange-200'
      }`}
    >
      <span>{term}</span>
      {onRemove && (
        <button
          onClick={() => onRemove(term, category)}
          className="ml-2 p-0.5 hover:bg-white rounded-full transition-colors"
        >
          <Minus className="w-3 h-3" />
        </button>
      )}
    </motion.div>
  );

  const SearchResultItem = ({ result }) => (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between p-3 bg-card border border-border rounded-lg hover:border-primary/50 transition-colors"
    >
      <div className="flex-1">
        <div className="flex items-center space-x-2">
          <span className="font-medium text-foreground">{result.term}</span>
          <span className={`text-xs px-2 py-1 rounded ${
            result.category === 'persona' ? 'bg-purple-100 text-purple-700'
            : result.category === 'namespace' ? 'bg-green-100 text-green-700'
            : 'bg-orange-100 text-orange-700'
          }`}>
            {result.category}
          </span>
          {result.match_type && (
            <span className="text-xs text-muted-foreground">
              {result.match_type === 'semantic' ? `${(result.similarity * 100).toFixed(0)}% similar` : 'exact match'}
            </span>
          )}
        </div>
        {result.examples && result.examples.length > 0 && (
          <p className="text-sm text-muted-foreground mt-1">
            {result.examples[0]}
          </p>
        )}
      </div>
      <button
        onClick={() => addAttributeToProjection(result.term, result.category)}
        className="ml-3 p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
        title="Add to projection"
      >
        <Plus className="w-4 h-4" />
      </button>
    </motion.div>
  );

  if (vocabularyHealth?.status === 'error') {
    return (
      <div className="p-8 text-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Vocabulary System Unavailable</h2>
          <p className="text-red-600 mb-4">
            The expandable vocabulary system is not operational: {vocabularyHealth.error}
          </p>
          <p className="text-sm text-red-500">
            Please ensure the backend API is running and the vocabulary system is properly initialized.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-border">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Projection Transformation</h1>
          <p className="text-muted-foreground">
            Mathematical projections between lexical spaces using expandable vocabulary
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="text-xs text-muted-foreground">
            Vocabulary: {vocabularyHealth?.total_attributes || 0} attributes
          </div>
          <div className={`w-2 h-2 rounded-full ${vocabularyHealth?.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'}`} />
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Left Panel - Input and Source Analysis */}
        <div className="w-1/2 p-6 border-r border-border">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Input Text
              </label>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onBlur={extractSourceAttributes}
                placeholder="Enter text to analyze and transform..."
                className="w-full h-32 p-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
              />
            </div>

            {/* Source Attributes */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-foreground">Extracted Source Attributes</h3>
                <button
                  onClick={extractSourceAttributes}
                  disabled={!inputText.trim()}
                  className="text-xs text-primary hover:text-primary/80 disabled:text-muted-foreground"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
              
              <div className="space-y-2">
                {Object.entries(sourceAttributes).map(([category, terms]) => (
                  <div key={category}>
                    <div className="text-xs font-medium text-muted-foreground mb-1 capitalize">
                      {category} ({terms.length})
                    </div>
                    <div className="flex flex-wrap gap-1">
                      <AnimatePresence>
                        {terms.map((term) => (
                          <AttributeTag 
                            key={`${category}-${term}`}
                            term={term} 
                            category={category}
                            source={true}
                          />
                        ))}
                      </AnimatePresence>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Projection Settings */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-foreground">Projection Settings</h3>
              
              <div>
                <label className="block text-xs text-muted-foreground mb-1">Transformation Method</label>
                <select
                  value={transformationMethod}
                  onChange={(e) => setTransformationMethod(e.target.value)}
                  className="w-full p-2 bg-background border border-border rounded text-sm"
                >
                  <option value="vocabulary">Vocabulary Projection (Vector-based)</option>
                  <option value="density_matrix">Density Matrix (Quantum-inspired)</option>
                  <option value="hybrid">Hybrid (Both Methods + Comparison)</option>
                </select>
                <div className="text-xs text-muted-foreground mt-1">
                  {transformationMethod === "vocabulary" && "Uses semantic vector projections in embedding space"}
                  {transformationMethod === "density_matrix" && "Uses quantum density matrix transformations (ρ → ρ')"}
                  {transformationMethod === "hybrid" && "Compares both methods and synthesizes results"}
                </div>
              </div>
              
              <div>
                <label className="block text-xs text-muted-foreground mb-1">
                  Projection Intensity: {projectionIntensity.toFixed(1)}
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={projectionIntensity}
                  onChange={(e) => setProjectionIntensity(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-xs text-muted-foreground mb-1">Reading Style</label>
                <select
                  value={readingStyle}
                  onChange={(e) => setReadingStyle(e.target.value)}
                  className="w-full p-2 bg-background border border-border rounded text-sm"
                >
                  <option value="interpretation">Interpretation</option>
                  <option value="skeptical">Skeptical</option>
                  <option value="devotional">Devotional</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-muted-foreground mb-1">
                  Semantic Dimension: {semanticDimension}
                </label>
                <input
                  type="range"
                  min="4"
                  max="128"
                  step="4"
                  value={semanticDimension}
                  onChange={(e) => setSemanticDimension(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Projection Target and Results */}
        <div className="w-1/2 p-6">
          <div className="space-y-4">
            {/* Vocabulary Search */}
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Search className="w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    searchVocabulary(e.target.value);
                  }}
                  placeholder="Search vocabulary..."
                  className="flex-1 p-2 bg-background border border-border rounded text-sm focus:ring-2 focus:ring-primary focus:border-transparent"
                />
                <select
                  value={activeCategory}
                  onChange={(e) => setActiveCategory(e.target.value)}
                  className="p-2 bg-background border border-border rounded text-sm"
                >
                  <option value="all">All</option>
                  <option value="persona">Persona</option>
                  <option value="namespace">Namespace</option>
                  <option value="style">Style</option>
                </select>
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="max-h-32 overflow-y-auto space-y-1">
                  {searchResults.map((result, index) => (
                    <SearchResultItem key={index} result={result} />
                  ))}
                </div>
              )}
            </div>

            {/* Projection Target */}
            <div>
              <h3 className="text-sm font-medium text-foreground mb-3">Projection Target</h3>
              
              <div className="space-y-3">
                {/* Persona */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-medium text-purple-600">Persona</label>
                    <span className="text-xs text-muted-foreground">{personaTerms.length} terms</span>
                  </div>
                  <div className="flex flex-wrap gap-1 min-h-8 p-2 border border-border rounded-lg">
                    <AnimatePresence>
                      {personaTerms.map((term) => (
                        <AttributeTag 
                          key={term}
                          term={term} 
                          category="persona"
                          onRemove={removeAttributeFromProjection}
                        />
                      ))}
                    </AnimatePresence>
                  </div>
                </div>

                {/* Namespace */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-medium text-green-600">Namespace</label>
                    <span className="text-xs text-muted-foreground">{namespaceTerms.length} terms</span>
                  </div>
                  <div className="flex flex-wrap gap-1 min-h-8 p-2 border border-border rounded-lg">
                    <AnimatePresence>
                      {namespaceTerms.map((term) => (
                        <AttributeTag 
                          key={term}
                          term={term} 
                          category="namespace"
                          onRemove={removeAttributeFromProjection}
                        />
                      ))}
                    </AnimatePresence>
                  </div>
                </div>

                {/* Style */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-medium text-orange-600">Style</label>
                    <span className="text-xs text-muted-foreground">{styleTerms.length} terms</span>
                  </div>
                  <div className="flex flex-wrap gap-1 min-h-8 p-2 border border-border rounded-lg">
                    <AnimatePresence>
                      {styleTerms.map((term) => (
                        <AttributeTag 
                          key={term}
                          term={term} 
                          category="style"
                          onRemove={removeAttributeFromProjection}
                        />
                      ))}
                    </AnimatePresence>
                  </div>
                </div>

                {/* Guidance Words */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label className="text-xs font-medium text-blue-600">Guidance Words</label>
                    <button
                      onClick={addGuidanceWord}
                      className="text-xs text-primary hover:text-primary/80"
                    >
                      <Plus className="w-3 h-3" />
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1 min-h-8 p-2 border border-border rounded-lg">
                    <AnimatePresence>
                      {guidanceWords.map((word) => (
                        <motion.div
                          key={word}
                          initial={{ scale: 0.8, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          exit={{ scale: 0.8, opacity: 0 }}
                          className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs"
                        >
                          <span>{word}</span>
                          <button
                            onClick={() => setGuidanceWords(guidanceWords.filter(w => w !== word))}
                            className="ml-1 p-0.5 hover:bg-blue-200 rounded-full"
                          >
                            <Minus className="w-2 h-2" />
                          </button>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>
                </div>
              </div>
            </div>

            {/* Transform Button */}
            <motion.button
              onClick={performProjectionTransformation}
              disabled={!inputText.trim() || isProcessing}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full p-4 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground rounded-lg font-medium hover:from-primary/90 hover:to-primary/70 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <div className="flex items-center justify-center space-x-2">
                {isProcessing ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      <Atom className="w-5 h-5" />
                    </motion.div>
                    <span>Projecting...</span>
                  </>
                ) : (
                  <>
                    <Target className="w-5 h-5" />
                    <span>Apply Projection</span>
                  </>
                )}
              </div>
            </motion.button>

            {/* Results */}
            {transformedText && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-foreground">Transformation Result</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => navigator.clipboard.writeText(transformedText)}
                      className="text-xs text-muted-foreground hover:text-foreground"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                    {transformationResult && (
                      <button
                        onClick={() => setShowAnalysis(!showAnalysis)}
                        className={`text-xs ${showAnalysis ? 'text-primary' : 'text-muted-foreground'} hover:text-primary`}
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
                
                <div className="p-3 bg-muted/50 border border-border rounded-lg">
                  <pre className="text-sm text-foreground whitespace-pre-wrap font-mono">
                    {transformedText}
                  </pre>
                </div>

                {/* Analysis */}
                <AnimatePresence>
                  {showAnalysis && transformationResult && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="p-3 bg-card border border-border rounded-lg text-xs space-y-2"
                    >
                      <div className="grid grid-cols-2 gap-2">
                        <div>Quality: {(transformationResult.transformation_quality * 100).toFixed(1)}%</div>
                        <div>Time: {transformationResult.processing_time_ms?.toFixed(0)}ms</div>
                        <div>Fidelity: {transformationResult.transformation_metrics?.fidelity?.toFixed(3)}</div>
                        <div>Dimension: {transformationResult.semantic_tomography?.povm_structure?.dimension}</div>
                      </div>
                      
                      {transformationResult.source_attributes && (
                        <div>
                          <div className="font-medium mb-1">Source → Target Projection:</div>
                          <div className="text-muted-foreground">
                            {Object.entries(transformationResult.source_attributes).map(([cat, terms]) => 
                              `${cat}: ${terms.length}`
                            ).join(', ')}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectionTransformationInterface;