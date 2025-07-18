import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play,
  Pause,
  Square,
  RotateCcw,
  Download,
  Upload,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Zap,
  Users,
  Layers,
  Palette,
  Filter,
  Settings,
  BarChart3
} from 'lucide-react';

const BatchProcessor = () => {
  const [narratives, setNarratives] = useState([]);
  const [selectedNarratives, setSelectedNarratives] = useState([]);
  const [batchConfig, setBatchConfig] = useState({
    target_persona: 'philosopher',
    target_namespace: 'lamish-galaxy',
    target_style: 'poetic',
    processing_type: 'transform'
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingResults, setProcessingResults] = useState([]);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [currentItem, setCurrentItem] = useState(null);
  const [configurations, setConfigurations] = useState(null);
  const [filterText, setFilterText] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [showCompleted, setShowCompleted] = useState(true);

  const processingTypes = [
    { id: 'transform', name: 'Transform', description: 'Apply persona/namespace/style transformation', icon: Zap },
    { id: 'analyze', name: 'Analyze', description: 'Extract meaning and attributes', icon: BarChart3 },
    { id: 'maieutic', name: 'Maieutic', description: 'Generate Socratic questions', icon: Users },
    { id: 'translation', name: 'Translation', description: 'Cross-language analysis', icon: Layers }
  ];

  // Load configurations and sample narratives
  useEffect(() => {
    loadConfigurations();
    loadSampleNarratives();
  }, []);

  const loadConfigurations = async () => {
    try {
      const response = await fetch('/configurations');
      const data = await response.json();
      setConfigurations(data);
    } catch (error) {
      console.error('Failed to load configurations:', error);
    }
  };

  const loadSampleNarratives = () => {
    // Sample narratives for demonstration
    const sampleNarratives = [
      {
        id: 1,
        text: "The lighthouse stood sentinel against the storm, its beam cutting through darkness like hope through despair.",
        source: "archive",
        date: "2024-01-15",
        persona: "storyteller",
        namespace: "maritime-realm",
        style: "poetic",
        status: "pending"
      },
      {
        id: 2,
        text: "Quantum entanglement suggests that consciousness might be fundamentally non-local, existing across multiple dimensional planes simultaneously.",
        source: "archive",
        date: "2024-01-14",
        persona: "scientist",
        namespace: "quantum-realm",
        style: "technical",
        status: "pending"
      },
      {
        id: 3,
        text: "The ancient scroll spoke of frequencies that could reshape reality itself, hidden in the resonance between worlds.",
        source: "archive",
        date: "2024-01-13",
        persona: "philosopher",
        namespace: "lamish-galaxy",
        style: "archaic",
        status: "pending"
      },
      {
        id: 4,
        text: "Data flows through neural networks like rivers through landscapes, carving new pathways of understanding.",
        source: "user",
        date: "2024-01-12",
        persona: "scientist",
        namespace: "cyberpunk-future",
        style: "technical",
        status: "pending"
      },
      {
        id: 5,
        text: "In the corporate towers, human creativity was becoming just another resource to be optimized and monetized.",
        source: "archive",
        date: "2024-01-11",
        persona: "critic",
        namespace: "corporate-dystopia",
        style: "formal",
        status: "pending"
      }
    ];
    setNarratives(sampleNarratives);
  };

  const toggleNarrativeSelection = (id) => {
    setSelectedNarratives(prev => 
      prev.includes(id) 
        ? prev.filter(nId => nId !== id)
        : [...prev, id]
    );
  };

  const selectAll = () => {
    const filteredIds = getFilteredNarratives().map(n => n.id);
    setSelectedNarratives(filteredIds);
  };

  const selectNone = () => {
    setSelectedNarratives([]);
  };

  const getFilteredNarratives = () => {
    let filtered = narratives.filter(n => {
      const matchesText = n.text.toLowerCase().includes(filterText.toLowerCase());
      const matchesStatus = showCompleted || n.status === 'pending';
      return matchesText && matchesStatus;
    });

    switch (sortBy) {
      case 'date':
        return filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
      case 'persona':
        return filtered.sort((a, b) => a.persona.localeCompare(b.persona));
      case 'status':
        return filtered.sort((a, b) => a.status.localeCompare(b.status));
      default:
        return filtered;
    }
  };

  const startBatchProcessing = async () => {
    if (selectedNarratives.length === 0) return;

    setIsProcessing(true);
    setProcessingProgress(0);
    setProcessingResults([]);

    const selectedItems = narratives.filter(n => selectedNarratives.includes(n.id));
    
    for (let i = 0; i < selectedItems.length; i++) {
      const narrative = selectedItems[i];
      setCurrentItem(narrative);
      
      try {
        let endpoint, body;
        
        switch (batchConfig.processing_type) {
          case 'transform':
            endpoint = '/transform';
            body = {
              narrative: narrative.text,
              target_persona: batchConfig.target_persona,
              target_namespace: batchConfig.target_namespace,
              target_style: batchConfig.target_style,
              show_steps: false
            };
            break;
          case 'analyze':
            endpoint = '/lamish/analyze';
            body = { content: narrative.text };
            break;
          case 'maieutic':
            endpoint = '/maieutic/start';
            body = { 
              narrative: narrative.text,
              focus_area: 'analysis'
            };
            break;
          case 'translation':
            endpoint = '/translation/roundtrip';
            body = {
              text: narrative.text,
              source_language: 'english',
              intermediate_languages: ['spanish', 'french']
            };
            break;
          default:
            throw new Error('Unknown processing type');
        }

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });

        const result = await response.json();
        
        const processedResult = {
          id: narrative.id,
          original: narrative,
          result: result,
          status: response.ok ? 'completed' : 'failed',
          timestamp: new Date().toISOString(),
          processing_type: batchConfig.processing_type
        };

        setProcessingResults(prev => [...prev, processedResult]);
        
        // Update narrative status
        setNarratives(prev => prev.map(n => 
          n.id === narrative.id 
            ? { ...n, status: response.ok ? 'completed' : 'failed' }
            : n
        ));

      } catch (error) {
        console.error(`Processing failed for narrative ${narrative.id}:`, error);
        
        const failedResult = {
          id: narrative.id,
          original: narrative,
          result: { error: error.message },
          status: 'failed',
          timestamp: new Date().toISOString(),
          processing_type: batchConfig.processing_type
        };

        setProcessingResults(prev => [...prev, failedResult]);
        setNarratives(prev => prev.map(n => 
          n.id === narrative.id ? { ...n, status: 'failed' } : n
        ));
      }

      setProcessingProgress(((i + 1) / selectedItems.length) * 100);
      
      // Small delay between requests
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setIsProcessing(false);
    setCurrentItem(null);
  };

  const exportResults = () => {
    const exportData = {
      batch_config: batchConfig,
      processing_date: new Date().toISOString(),
      results: processingResults
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `batch-results-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const resetBatch = () => {
    setSelectedNarratives([]);
    setProcessingResults([]);
    setProcessingProgress(0);
    setCurrentItem(null);
    setNarratives(prev => prev.map(n => ({ ...n, status: 'pending' })));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-400" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-yellow-400 animate-spin" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-semibold text-white">Batch Processor</h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={resetBatch}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              title="Reset batch"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            {processingResults.length > 0 && (
              <button
                onClick={exportResults}
                className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
                title="Export results"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Processing Configuration */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-white">Processing Configuration</h3>
            
            <div>
              <label className="block text-sm text-gray-300 mb-2">Processing Type</label>
              <select
                value={batchConfig.processing_type}
                onChange={(e) => setBatchConfig(prev => ({ ...prev, processing_type: e.target.value }))}
                className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
              >
                {processingTypes.map(type => (
                  <option key={type.id} value={type.id}>
                    {type.name} - {type.description}
                  </option>
                ))}
              </select>
            </div>

            {batchConfig.processing_type === 'transform' && configurations && (
              <>
                <div>
                  <label className="block text-sm text-gray-300 mb-2">Target Persona</label>
                  <select
                    value={batchConfig.target_persona}
                    onChange={(e) => setBatchConfig(prev => ({ ...prev, target_persona: e.target.value }))}
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    {configurations.personas?.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-300 mb-2">Target Namespace</label>
                  <select
                    value={batchConfig.target_namespace}
                    onChange={(e) => setBatchConfig(prev => ({ ...prev, target_namespace: e.target.value }))}
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    {configurations.namespaces?.map(n => (
                      <option key={n.id} value={n.id}>{n.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-300 mb-2">Target Style</label>
                  <select
                    value={batchConfig.target_style}
                    onChange={(e) => setBatchConfig(prev => ({ ...prev, target_style: e.target.value }))}
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    {configurations.styles?.map(s => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                </div>
              </>
            )}
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-medium text-white">Batch Status</h3>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-blue-400">{narratives.length}</div>
                <div className="text-sm text-gray-400">Total</div>
              </div>
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-purple-400">{selectedNarratives.length}</div>
                <div className="text-sm text-gray-400">Selected</div>
              </div>
              <div className="text-center p-3 bg-white/5 rounded-lg">
                <div className="text-2xl font-bold text-green-400">{processingResults.length}</div>
                <div className="text-sm text-gray-400">Processed</div>
              </div>
            </div>

            {isProcessing && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">Progress</span>
                  <span className="text-gray-300">{Math.round(processingProgress)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-purple-600 to-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${processingProgress}%` }}
                  />
                </div>
                {currentItem && (
                  <div className="text-sm text-gray-400">
                    Processing: {currentItem.text.substring(0, 50)}...
                  </div>
                )}
              </div>
            )}

            <button
              onClick={startBatchProcessing}
              disabled={isProcessing || selectedNarratives.length === 0}
              className="w-full px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {isProcessing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Start Batch Processing</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Narrative Selection */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Archive Narratives</h3>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
                placeholder="Filter narratives..."
                className="px-3 py-1 bg-white/5 border border-white/10 rounded text-sm text-white"
              />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-1 bg-white/5 border border-white/10 rounded text-sm text-white"
              >
                <option value="date">Sort by Date</option>
                <option value="persona">Sort by Persona</option>
                <option value="status">Sort by Status</option>
              </select>
              <label className="flex items-center space-x-2 text-sm text-gray-300">
                <input
                  type="checkbox"
                  checked={showCompleted}
                  onChange={(e) => setShowCompleted(e.target.checked)}
                />
                <span>Show Completed</span>
              </label>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={selectAll}
                className="px-3 py-1 bg-white/5 border border-white/10 rounded text-sm text-white hover:bg-white/10"
              >
                Select All
              </button>
              <button
                onClick={selectNone}
                className="px-3 py-1 bg-white/5 border border-white/10 rounded text-sm text-white hover:bg-white/10"
              >
                Select None
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {getFilteredNarratives().map((narrative) => (
            <motion.div
              key={narrative.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`p-4 border rounded-lg cursor-pointer transition-all ${
                selectedNarratives.includes(narrative.id)
                  ? 'border-purple-500/50 bg-purple-500/10'
                  : 'border-white/10 bg-white/5 hover:bg-white/10'
              }`}
              onClick={() => toggleNarrativeSelection(narrative.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <input
                      type="checkbox"
                      checked={selectedNarratives.includes(narrative.id)}
                      onChange={() => toggleNarrativeSelection(narrative.id)}
                      className="w-4 h-4"
                    />
                    {getStatusIcon(narrative.status)}
                    <span className="text-sm text-gray-400">{narrative.date}</span>
                    <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded">
                      {narrative.persona}
                    </span>
                    <span className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded">
                      {narrative.namespace}
                    </span>
                    <span className="px-2 py-1 bg-orange-500/20 text-orange-300 text-xs rounded">
                      {narrative.style}
                    </span>
                  </div>
                  <p className="text-gray-200 text-sm">{narrative.text}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Results Display */}
      {processingResults.length > 0 && (
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Processing Results</h3>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {processingResults.map((result) => (
              <div
                key={result.id}
                className={`p-4 border rounded-lg ${
                  result.status === 'completed' 
                    ? 'border-green-500/20 bg-green-500/5'
                    : 'border-red-500/20 bg-red-500/5'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(result.status)}
                    <span className="text-sm font-medium text-white">
                      {result.processing_type.charAt(0).toUpperCase() + result.processing_type.slice(1)}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(result.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm text-gray-300 mb-2">
                  <strong>Original:</strong> {result.original.text.substring(0, 100)}...
                </p>
                {result.status === 'completed' && result.result.projection && (
                  <p className="text-sm text-gray-200">
                    <strong>Result:</strong> {result.result.projection.narrative?.substring(0, 100)}...
                  </p>
                )}
                {result.status === 'failed' && (
                  <p className="text-sm text-red-400">
                    <strong>Error:</strong> {result.result.error}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BatchProcessor;