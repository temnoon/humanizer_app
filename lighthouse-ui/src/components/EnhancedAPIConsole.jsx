import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Terminal,
  Play,
  Download,
  Trash2,
  Copy,
  Check,
  AlertCircle,
  Info,
  CheckCircle,
  XCircle,
  Clock,
  Filter,
  Search,
  Settings,
  Book,
  Code,
  FileText,
  ChevronRight,
  ChevronDown,
  Zap,
  Brain,
  Eye,
  Globe,
  Cpu,
  Database,
  Network,
  Layers,
  Command,
  BookOpen,
  HelpCircle,
  Lightbulb,
  Target,
  Wrench,
  Send,
  RefreshCw,
  Save,
  Upload,
  Edit,
  Plus,
  Minus
} from 'lucide-react';

const EnhancedAPIConsole = () => {
  // Core state
  const [logs, setLogs] = useState([]);
  const [selectedEndpoint, setSelectedEndpoint] = useState('/health');
  const [requestMethod, setRequestMethod] = useState('GET');
  const [requestBody, setRequestBody] = useState('');
  const [requestHeaders, setRequestHeaders] = useState('{}');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  // Enhanced features state
  const [activePanel, setActivePanel] = useState('constructor'); // constructor, docs, examples, models
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const [selectedModel, setSelectedModel] = useState('gemma3:4b');
  const [availableModels, setAvailableModels] = useState({});
  const [savedCalls, setSavedCalls] = useState([]);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [callName, setCallName] = useState('');
  const [currentPath, setCurrentPath] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  
  // JSON/MD reader state
  const [readerContent, setReaderContent] = useState('');
  const [readerType, setReaderType] = useState('json');
  const [parsedContent, setParsedContent] = useState(null);

  const logsEndRef = useRef(null);

  // Comprehensive API documentation
  const apiDocs = {
    core: {
      title: "🔧 Core APIs",
      endpoints: [
        {
          method: 'GET',
          path: '/health',
          description: 'System health check and status',
          params: [],
          response: { status: 'healthy', timestamp: '2024-01-01T12:00:00Z' },
          category: 'core'
        },
        {
          method: 'GET',
          path: '/configurations',
          description: 'Available personas, namespaces, and styles',
          params: [],
          response: { personas: [], namespaces: [], styles: [] },
          category: 'core'
        },
        {
          method: 'POST',
          path: '/transform',
          description: '5-step narrative transformation pipeline',
          params: [
            { name: 'narrative', type: 'string', required: true, description: 'Input text to transform' },
            { name: 'target_persona', type: 'string', required: true, description: 'Target persona ID' },
            { name: 'target_namespace', type: 'string', required: true, description: 'Target namespace ID' },
            { name: 'target_style', type: 'string', required: true, description: 'Target style ID' },
            { name: 'show_steps', type: 'boolean', required: false, description: 'Show detailed steps' }
          ],
          response: { transform_id: 'uuid', original: {}, projection: {}, steps: [] },
          category: 'core'
        }
      ]
    },
    llm: {
      title: "🤖 LLM Management",
      endpoints: [
        {
          method: 'GET',
          path: '/api/llm/configurations',
          description: 'Get saved LLM configurations for all tasks',
          params: [],
          response: { task_configs: {} },
          category: 'llm'
        },
        {
          method: 'POST',
          path: '/api/llm/configurations',
          description: 'Save LLM configuration for specific tasks',
          params: [
            { name: 'task_configs', type: 'object', required: true, description: 'Task-specific configurations' }
          ],
          response: { message: 'Configuration saved', tasks_configured: 5 },
          category: 'llm'
        },
        {
          method: 'GET',
          path: '/api/llm/status',
          description: 'Check status of all LLM providers',
          params: [],
          response: { providers: {} },
          category: 'llm'
        },
        {
          method: 'POST',
          path: '/api/llm/refresh-models',
          description: 'Refresh model lists from all providers',
          params: [],
          response: { available_models: {} },
          category: 'llm'
        }
      ]
    },
    maieutic: {
      title: "🧠 Maieutic Dialogue",
      endpoints: [
        {
          method: 'POST',
          path: '/maieutic/start',
          description: 'Start a Socratic dialogue session',
          params: [
            { name: 'narrative', type: 'string', required: true, description: 'Text to explore' },
            { name: 'focus_area', type: 'string', required: false, description: 'Area of focus' }
          ],
          response: { session_id: 'uuid', initial_question: 'string' },
          category: 'maieutic'
        },
        {
          method: 'POST',
          path: '/maieutic/question',
          description: 'Generate next question in dialogue',
          params: [
            { name: 'session_id', type: 'string', required: true, description: 'Session identifier' },
            { name: 'depth_level', type: 'integer', required: false, description: 'Current depth (0-4)' }
          ],
          response: { question: 'string', depth_level: 1 },
          category: 'maieutic'
        }
      ]
    },
    vision: {
      title: "👁️ Vision & Media",
      endpoints: [
        {
          method: 'POST',
          path: '/api/vision/analyze',
          description: 'Analyze images with vision-capable models',
          params: [
            { name: 'prompt', type: 'string', required: true, description: 'Analysis prompt' },
            { name: 'image_data', type: 'string', required: true, description: 'Base64 encoded image' },
            { name: 'provider', type: 'string', required: false, description: 'Vision provider override' },
            { name: 'model', type: 'string', required: false, description: 'Model override' }
          ],
          response: { analysis: 'string', provider_used: 'string', processing_time_ms: 1500 },
          category: 'vision'
        },
        {
          method: 'POST',
          path: '/api/vision/transcribe',
          description: 'Extract text from images (OCR/handwriting)',
          params: [
            { name: 'prompt', type: 'string', required: false, description: 'Transcription prompt' },
            { name: 'image_data', type: 'string', required: true, description: 'Base64 encoded image' }
          ],
          response: { transcription: 'string', confidence: 0.95 },
          category: 'vision'
        }
      ]
    },
    translation: {
      title: "🌐 Translation & Analysis",
      endpoints: [
        {
          method: 'POST',
          path: '/translation/roundtrip',
          description: 'Round-trip translation analysis',
          params: [
            { name: 'text', type: 'string', required: true, description: 'Text to analyze' },
            { name: 'intermediate_language', type: 'string', required: true, description: 'Bridge language' },
            { name: 'source_language', type: 'string', required: false, description: 'Source language (default: english)' }
          ],
          response: { forward_translation: 'string', final_text: 'string', semantic_drift: 0.15 },
          category: 'translation'
        }
      ]
    },
    linguistic: {
      title: "📝 Linguistic Engine",
      endpoints: [
        {
          method: 'POST',
          path: '/api/linguistic/manifests/create-from-examples',
          description: 'Create transformation manifest from examples',
          params: [
            { name: 'original_texts', type: 'array', required: true, description: 'Original text examples' },
            { name: 'transformed_texts', type: 'array', required: true, description: 'Transformed examples' },
            { name: 'manifest_id', type: 'string', required: true, description: 'Unique manifest ID' }
          ],
          response: { manifest: {}, summary: {} },
          category: 'linguistic'
        },
        {
          method: 'POST',
          path: '/api/linguistic/analysis/stylometrics',
          description: 'Analyze text stylometric features',
          params: [
            { name: 'text', type: 'string', required: true, description: 'Text to analyze' },
            { name: 'include_stylometrics', type: 'boolean', required: false, description: 'Include detailed analysis' }
          ],
          response: { analysis: {}, inferred_persona: {}, inferred_style: {} },
          category: 'linguistic'
        }
      ]
    }
  };

  // Sample API calls for different use cases
  const exampleCalls = {
    quickStart: {
      title: "🚀 Quick Start Examples",
      calls: [
        {
          name: "Health Check",
          method: "GET",
          endpoint: "/health",
          body: "",
          description: "Check if the API is running"
        },
        {
          name: "Simple Transform",
          method: "POST",
          endpoint: "/transform",
          body: JSON.stringify({
            narrative: "The team worked hard to meet the deadline.",
            target_persona: "philosopher",
            target_namespace: "lamish-galaxy",
            target_style: "poetic",
            show_steps: true
          }, null, 2),
          description: "Basic narrative transformation"
        }
      ]
    },
    advanced: {
      title: "⚡ Advanced Features",
      calls: [
        {
          name: "Maieutic Exploration",
          method: "POST",
          endpoint: "/maieutic/start",
          body: JSON.stringify({
            narrative: "Technology is changing how we communicate with each other.",
            focus_area: "societal implications"
          }, null, 2),
          description: "Start Socratic dialogue exploration"
        },
        {
          name: "Vision Analysis",
          method: "POST",
          endpoint: "/api/vision/analyze",
          body: JSON.stringify({
            prompt: "What do you see in this image? Describe it in detail.",
            image_data: "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            provider: "openai",
            model: "gpt-4o"
          }, null, 2),
          description: "Analyze image content with AI"
        },
        {
          name: "Round-trip Translation",
          method: "POST",
          endpoint: "/translation/roundtrip",
          body: JSON.stringify({
            text: "The essence of wisdom lies in understanding diverse perspectives.",
            intermediate_language: "spanish",
            source_language: "english"
          }, null, 2),
          description: "Test semantic stability through translation"
        }
      ]
    },
    linguistic: {
      title: "📝 Linguistic Engine",
      calls: [
        {
          name: "Create Transformation Manifest",
          method: "POST",
          endpoint: "/api/linguistic/manifests/create-from-examples",
          body: JSON.stringify({
            original_texts: [
              "The company announced layoffs.",
              "Scientists discovered a new planet."
            ],
            transformed_texts: [
              "The guild proclaimed workforce adjustments within the crystal domains.",
              "Scholars unveiled a celestial realm beyond the known galaxies."
            ],
            manifest_id: "sci_fi_universe_manifest",
            description: "Science fiction universe transformation"
          }, null, 2),
          description: "Learn transformation patterns from examples"
        },
        {
          name: "Stylometric Analysis",
          method: "POST",
          endpoint: "/api/linguistic/analysis/stylometrics",
          body: JSON.stringify({
            text: "Nevertheless, one must consider the implications of such technological advancement. The ramifications extend far beyond immediate applications.",
            include_stylometrics: true
          }, null, 2),
          description: "Analyze writing style and linguistic features"
        }
      ]
    }
  };

  // Load available models on component mount
  useEffect(() => {
    loadAvailableModels();
  }, []);

  const loadAvailableModels = async () => {
    try {
      // First get provider status
      const statusResponse = await fetch('http://127.0.0.1:8100/api/llm/status');
      let providerStatus = {};
      if (statusResponse.ok) {
        providerStatus = await statusResponse.json();
      }

      // Then refresh and get models
      const modelsResponse = await fetch('http://127.0.0.1:8100/api/llm/refresh-models', {
        method: 'POST'
      });
      
      if (modelsResponse.ok) {
        const modelsData = await modelsResponse.json();
        
        // Combine status and models data
        const combinedData = {};
        Object.entries(modelsData.available_models || {}).forEach(([provider, models]) => {
          combinedData[provider] = {
            available: providerStatus[provider]?.available || false,
            status: providerStatus[provider]?.status_message || 'Unknown',
            models: models,
            count: models.length
          };
        });
        
        setAvailableModels(combinedData);
      }
    } catch (error) {
      console.error('Failed to load models:', error);
      addLog('error', 'Failed to load available models', { error: error.message });
    }
  };

  // Auto-scroll logs
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Set sample body when endpoint changes
  useEffect(() => {
    const allEndpoints = Object.values(apiDocs).flatMap(section => section.endpoints);
    const endpoint = allEndpoints.find(ep => ep.path === selectedEndpoint);
    
    if (endpoint && endpoint.params.length > 0 && requestMethod === 'POST') {
      const sampleBody = {};
      endpoint.params.forEach(param => {
        if (param.required) {
          switch (param.type) {
            case 'string':
              sampleBody[param.name] = `sample_${param.name}`;
              break;
            case 'boolean':
              sampleBody[param.name] = true;
              break;
            case 'integer':
              sampleBody[param.name] = 1;
              break;
            case 'array':
              sampleBody[param.name] = [`sample_${param.name}`];
              break;
            case 'object':
              sampleBody[param.name] = {};
              break;
            default:
              sampleBody[param.name] = null;
          }
        }
      });
      setRequestBody(JSON.stringify(sampleBody, null, 2));
    } else if (requestMethod === 'GET') {
      setRequestBody('');
    }
  }, [selectedEndpoint, requestMethod]);

  // Parse JSON/MD content
  useEffect(() => {
    if (readerContent.trim()) {
      try {
        if (readerType === 'json') {
          setParsedContent(JSON.parse(readerContent));
        } else {
          setParsedContent(readerContent);
        }
      } catch (error) {
        setParsedContent({ error: error.message });
      }
    } else {
      setParsedContent(null);
    }
  }, [readerContent, readerType]);

  const addLog = (type, message, data = null) => {
    const timestamp = new Date().toISOString();
    const logEntry = {
      id: Date.now() + Math.random(),
      timestamp,
      type,
      message,
      data,
      endpoint: selectedEndpoint,
      method: requestMethod
    };
    setLogs(prev => [...prev, logEntry]);
  };

  const executeRequest = async () => {
    setIsLoading(true);
    const startTime = Date.now();
    
    try {
      let url = `http://127.0.0.1:8100${selectedEndpoint}`;
      
      addLog('request', `${requestMethod} ${selectedEndpoint}`, {
        headers: requestHeaders,
        body: requestBody,
        provider: selectedProvider,
        model: selectedModel
      });

      const options = {
        method: requestMethod,
        headers: {
          'Content-Type': 'application/json',
          ...JSON.parse(requestHeaders || '{}')
        }
      };

      if (requestMethod !== 'GET' && requestBody.trim()) {
        // Automatically inject provider/model for relevant endpoints
        let bodyData = JSON.parse(requestBody);
        
        // Auto-inject provider/model for certain endpoints
        if (selectedEndpoint.includes('/vision/') || 
            selectedEndpoint.includes('/maieutic/') ||
            selectedEndpoint.includes('/transform')) {
          if (!bodyData.provider && selectedProvider && availableModels[selectedProvider]?.available) {
            bodyData.provider = selectedProvider;
          }
          if (!bodyData.model && selectedModel) {
            bodyData.model = selectedModel;
          }
        }
        
        options.body = JSON.stringify(bodyData);
      }

      const response = await fetch(url, options);
      const duration = Date.now() - startTime;
      const responseData = await response.json();

      if (response.ok) {
        addLog('success', `Response received (${duration}ms)`, {
          status: response.status,
          data: responseData
        });
        setResponse({
          status: response.status,
          statusText: response.statusText,
          data: responseData,
          duration
        });
      } else {
        addLog('error', `Request failed (${duration}ms)`, {
          status: response.status,
          statusText: response.statusText,
          data: responseData
        });
        setResponse({
          status: response.status,
          statusText: response.statusText,
          data: responseData,
          duration,
          error: true
        });
      }

    } catch (error) {
      const duration = Date.now() - startTime;
      addLog('error', `Network error (${duration}ms)`, { error: error.message });
      setResponse({
        error: true,
        message: error.message,
        duration
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadExampleCall = (call) => {
    setRequestMethod(call.method);
    setSelectedEndpoint(call.endpoint);
    setRequestBody(call.body);
    setActivePanel('constructor');
  };

  const saveCurrentCall = () => {
    if (callName.trim()) {
      const savedCall = {
        id: Date.now(),
        name: callName,
        method: requestMethod,
        endpoint: selectedEndpoint,
        body: requestBody,
        headers: requestHeaders,
        timestamp: new Date().toISOString()
      };
      setSavedCalls(prev => [savedCall, ...prev]);
      setCallName('');
      setShowSaveModal(false);
    }
  };

  const copyResponse = () => {
    if (response) {
      navigator.clipboard.writeText(JSON.stringify(response.data || response, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getLogIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'info': return <Info className="w-4 h-4 text-blue-400" />;
      case 'request': return <Send className="w-4 h-4 text-yellow-400" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'success': return 'border-green-500/20 bg-green-500/5';
      case 'error': return 'border-red-500/20 bg-red-500/5';
      case 'info': return 'border-blue-500/20 bg-blue-500/5';
      case 'request': return 'border-yellow-500/20 bg-yellow-500/5';
      default: return 'border-gray-500/20 bg-gray-500/5';
    }
  };

  const allEndpoints = Object.values(apiDocs).flatMap(section => section.endpoints);
  const filteredEndpoints = allEndpoints.filter(endpoint => 
    !searchTerm || 
    endpoint.path.toLowerCase().includes(searchTerm.toLowerCase()) ||
    endpoint.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header with Navigation */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Terminal className="w-6 h-6 text-purple-400" />
            <h2 className="text-2xl font-semibold text-white">Enhanced API Console</h2>
            <span className="px-2 py-1 bg-purple-600/20 text-purple-300 text-xs rounded-full">
              Learning Center
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSaveModal(true)}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              title="Save current call"
            >
              <Save className="w-4 h-4" />
            </button>
            <button
              onClick={loadAvailableModels}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              title="Refresh models"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Panel Navigation */}
        <div className="flex space-x-1 mb-6 bg-white/5 rounded-lg p-1">
          {[
            { id: 'constructor', label: 'API Constructor', icon: Wrench },
            { id: 'docs', label: 'Documentation', icon: Book },
            { id: 'examples', label: 'Examples', icon: Lightbulb },
            { id: 'models', label: 'Models', icon: Cpu },
            { id: 'reader', label: 'JSON/MD Reader', icon: FileText }
          ].map(panel => (
            <button
              key={panel.id}
              onClick={() => setActivePanel(panel.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                activePanel === panel.id
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-white/10'
              }`}
            >
              <panel.icon className="w-4 h-4" />
              <span className="text-sm font-medium">{panel.label}</span>
            </button>
          ))}
        </div>

        {/* Panel Content */}
        <AnimatePresence mode="wait">
          {activePanel === 'constructor' && (
            <motion.div
              key="constructor"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            >
              {/* Left: Request Builder */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white mb-4">🔧 Request Builder</h3>
                
                {/* Method and Endpoint */}
                <div className="flex space-x-2">
                  <select
                    value={requestMethod}
                    onChange={(e) => setRequestMethod(e.target.value)}
                    className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                    <option value="PUT">PUT</option>
                    <option value="DELETE">DELETE</option>
                  </select>
                  
                  <select
                    value={selectedEndpoint}
                    onChange={(e) => setSelectedEndpoint(e.target.value)}
                    className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  >
                    {filteredEndpoints.map(endpoint => (
                      <option key={endpoint.path} value={endpoint.path}>
                        {endpoint.path} - {endpoint.description}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Provider and Model Selection */}
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Provider</label>
                    <select
                      value={selectedProvider}
                      onChange={(e) => {
                        setSelectedProvider(e.target.value);
                        // Reset model when provider changes
                        const provider = availableModels[e.target.value];
                        if (provider?.models?.length > 0) {
                          setSelectedModel(provider.models[0].name);
                        }
                      }}
                      className="w-full px-2 py-1 bg-white/5 border border-white/10 rounded text-white text-sm"
                    >
                      {Object.entries(availableModels).map(([provider, data]) => (
                        <option key={provider} value={provider} disabled={!data.available}>
                          {provider} ({data.available ? data.count || 0 : 'unavailable'})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Model</label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="w-full px-2 py-1 bg-white/5 border border-white/10 rounded text-white text-sm"
                      disabled={!availableModels[selectedProvider]?.models?.length}
                    >
                      {(availableModels[selectedProvider]?.models || []).map((model, idx) => (
                        <option key={idx} value={model.name}>
                          {model.name} {model.size && `(${model.size})`}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Auto-injection indicator */}
                {(selectedEndpoint.includes('/vision/') || 
                  selectedEndpoint.includes('/maieutic/') ||
                  selectedEndpoint.includes('/transform')) && (
                  <div className="flex items-center gap-2 text-xs text-blue-400 bg-blue-600/10 p-2 rounded border border-blue-600/20">
                    <Info className="w-3 h-3" />
                    <span>Provider/model will be auto-injected for this endpoint</span>
                  </div>
                )}

                {/* Endpoint Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search endpoints..."
                    className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                  />
                </div>

                {/* Headers */}
                <div>
                  <label className="block text-sm text-gray-300 mb-2">Headers (JSON)</label>
                  <textarea
                    value={requestHeaders}
                    onChange={(e) => setRequestHeaders(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm font-mono"
                    rows={3}
                    placeholder='{"Authorization": "Bearer token"}'
                  />
                </div>

                {/* Request Body */}
                {requestMethod !== 'GET' && (
                  <div>
                    <label className="block text-sm text-gray-300 mb-2">Request Body (JSON)</label>
                    <textarea
                      value={requestBody}
                      onChange={(e) => setRequestBody(e.target.value)}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm font-mono"
                      rows={10}
                      placeholder="{}"
                    />
                  </div>
                )}

                {/* Execute Button */}
                <button
                  onClick={executeRequest}
                  disabled={isLoading}
                  className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Executing...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-5 h-5" />
                      <span>Execute Request</span>
                    </>
                  )}
                </button>
              </div>

              {/* Right: Response */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white">📡 Response</h3>
                  {response && (
                    <button
                      onClick={copyResponse}
                      className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
                      title="Copy response"
                    >
                      {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  )}
                </div>
                
                {response ? (
                  <div className={`p-4 rounded-lg border ${response.error ? 'border-red-500/20 bg-red-500/5' : 'border-green-500/20 bg-green-500/5'}`}>
                    <div className="flex items-center justify-between mb-3">
                      <span className={`text-sm font-medium ${response.error ? 'text-red-400' : 'text-green-400'}`}>
                        {response.status ? `${response.status} ${response.statusText}` : 'Network Error'}
                      </span>
                      <span className="text-sm text-gray-400">{response.duration}ms</span>
                    </div>
                    <pre className="text-sm text-gray-300 overflow-auto max-h-96 bg-black/20 p-3 rounded border">
                      {JSON.stringify(response.data || { error: response.message }, null, 2)}
                    </pre>
                  </div>
                ) : (
                  <div className="p-8 border border-gray-500/20 bg-gray-500/5 rounded-lg text-center text-gray-400">
                    <Terminal className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No response yet</p>
                    <p className="text-sm mt-1">Execute a request to see the response</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activePanel === 'docs' && (
            <motion.div
              key="docs"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4">📚 API Documentation</h3>
              
              {Object.entries(apiDocs).map(([key, section]) => (
                <details key={key} className="group bg-white/5 rounded-lg border border-white/10">
                  <summary className="p-4 cursor-pointer hover:bg-white/5 transition-colors">
                    <div className="flex items-center justify-between">
                      <h4 className="text-lg font-medium text-white">{section.title}</h4>
                      <ChevronRight className="w-5 h-5 text-gray-400 transition-transform group-open:rotate-90" />
                    </div>
                  </summary>
                  
                  <div className="px-4 pb-4 space-y-4">
                    {section.endpoints.map((endpoint, idx) => (
                      <div key={idx} className="bg-black/20 rounded-lg p-4 border border-white/5">
                        <div className="flex items-center space-x-3 mb-3">
                          <span className={`px-2 py-1 text-xs font-mono rounded ${
                            endpoint.method === 'GET' ? 'bg-green-600/20 text-green-300' :
                            endpoint.method === 'POST' ? 'bg-blue-600/20 text-blue-300' :
                            endpoint.method === 'PUT' ? 'bg-yellow-600/20 text-yellow-300' :
                            'bg-red-600/20 text-red-300'
                          }`}>
                            {endpoint.method}
                          </span>
                          <code className="text-purple-300">{endpoint.path}</code>
                          <button
                            onClick={() => {
                              setRequestMethod(endpoint.method);
                              setSelectedEndpoint(endpoint.path);
                              setActivePanel('constructor');
                            }}
                            className="ml-auto px-2 py-1 bg-purple-600/20 text-purple-300 text-xs rounded hover:bg-purple-600/30"
                          >
                            Try It
                          </button>
                        </div>
                        <p className="text-gray-300 text-sm mb-3">{endpoint.description}</p>
                        
                        {endpoint.params.length > 0 && (
                          <div className="mb-3">
                            <h5 className="text-sm font-medium text-gray-300 mb-2">Parameters:</h5>
                            <div className="space-y-1">
                              {endpoint.params.map((param, pidx) => (
                                <div key={pidx} className="text-xs">
                                  <code className="text-purple-300">{param.name}</code>
                                  <span className="text-gray-400"> ({param.type})</span>
                                  {param.required && <span className="text-red-400 ml-1">*</span>}
                                  <span className="text-gray-400 ml-2">- {param.description}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <details className="mt-2">
                          <summary className="text-xs text-gray-400 cursor-pointer">Sample Response</summary>
                          <pre className="text-xs text-gray-300 mt-2 bg-black/30 p-2 rounded overflow-auto">
                            {JSON.stringify(endpoint.response, null, 2)}
                          </pre>
                        </details>
                      </div>
                    ))}
                  </div>
                </details>
              ))}
            </motion.div>
          )}

          {activePanel === 'examples' && (
            <motion.div
              key="examples"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4">💡 Example API Calls</h3>
              
              {Object.entries(exampleCalls).map(([key, section]) => (
                <div key={key} className="bg-white/5 rounded-lg border border-white/10 p-4">
                  <h4 className="text-lg font-medium text-white mb-4">{section.title}</h4>
                  <div className="grid gap-4">
                    {section.calls.map((call, idx) => (
                      <div key={idx} className="bg-black/20 rounded-lg p-4 border border-white/5">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="font-medium text-white">{call.name}</h5>
                          <button
                            onClick={() => loadExampleCall(call)}
                            className="px-3 py-1 bg-purple-600/20 text-purple-300 text-sm rounded hover:bg-purple-600/30 transition-colors"
                          >
                            Load Example
                          </button>
                        </div>
                        <p className="text-gray-300 text-sm mb-3">{call.description}</p>
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`px-2 py-1 text-xs font-mono rounded ${
                            call.method === 'GET' ? 'bg-green-600/20 text-green-300' :
                            'bg-blue-600/20 text-blue-300'
                          }`}>
                            {call.method}
                          </span>
                          <code className="text-purple-300 text-sm">{call.endpoint}</code>
                        </div>
                        {call.body && (
                          <details className="mt-2">
                            <summary className="text-xs text-gray-400 cursor-pointer">Request Body</summary>
                            <pre className="text-xs text-gray-300 mt-2 bg-black/30 p-2 rounded overflow-auto">
                              {call.body}
                            </pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </motion.div>
          )}

          {activePanel === 'models' && (
            <motion.div
              key="models"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">🤖 Available Models</h3>
                <button
                  onClick={loadAvailableModels}
                  className="flex items-center gap-2 px-3 py-1 bg-purple-600/20 text-purple-300 rounded-lg hover:bg-purple-600/30 transition-colors text-sm"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh Models
                </button>
              </div>
              
              {Object.keys(availableModels).length === 0 ? (
                <div className="text-center py-8">
                  <Cpu className="w-12 h-12 mx-auto mb-4 text-gray-500" />
                  <p className="text-gray-400">Loading models...</p>
                  <button
                    onClick={loadAvailableModels}
                    className="mt-2 px-4 py-2 bg-purple-600/20 text-purple-300 rounded-lg hover:bg-purple-600/30 transition-colors"
                  >
                    Load Models
                  </button>
                </div>
              ) : (
                Object.entries(availableModels).map(([provider, data]) => (
                  <div key={provider} className="bg-white/5 rounded-lg border border-white/10 p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <h4 className="text-lg font-medium text-white capitalize">{provider}</h4>
                        <span className="text-sm text-gray-400">
                          {data.models?.length || 0} models
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 text-xs rounded ${
                          data.available ? 'bg-green-600/20 text-green-300' : 'bg-red-600/20 text-red-300'
                        }`}>
                          {data.available ? 'Available' : 'Unavailable'}
                        </span>
                        {data.available && (
                          <button
                            onClick={() => {
                              setSelectedProvider(provider);
                              if (data.models?.length > 0) {
                                setSelectedModel(data.models[0].name);
                              }
                              setActivePanel('constructor');
                            }}
                            className="px-2 py-1 bg-blue-600/20 text-blue-300 text-xs rounded hover:bg-blue-600/30"
                          >
                            Select
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {!data.available && (
                      <div className="text-red-400 text-sm mb-3">{data.status}</div>
                    )}
                    
                    {data.available && data.models && data.models.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                        {data.models.map((model, idx) => (
                          <div 
                            key={idx} 
                            className="bg-black/20 rounded p-3 border border-white/5 hover:border-purple-500/30 transition-colors cursor-pointer"
                            onClick={() => {
                              setSelectedProvider(provider);
                              setSelectedModel(model.name);
                              setActivePanel('constructor');
                            }}
                          >
                            <div className="flex items-start justify-between mb-2">
                              <code className="text-purple-300 text-sm font-medium break-all">
                                {model.name}
                              </code>
                              {model.size && (
                                <span className="text-xs text-gray-400 ml-2 flex-shrink-0">
                                  {model.size}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center justify-between text-xs text-gray-400">
                              {model.context && (
                                <span>Context: {model.context}</span>
                              )}
                              {model.family && (
                                <span className="ml-auto">{model.family}</span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : data.available ? (
                      <div className="text-gray-400 text-sm text-center py-4">
                        No models available for this provider
                      </div>
                    ) : null}
                  </div>
                ))
              )}
            </motion.div>
          )}

          {activePanel === 'reader' && (
            <motion.div
              key="reader"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <h3 className="text-lg font-semibold text-white mb-4">📄 JSON/Markdown Reader</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Input */}
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <label className="text-sm text-gray-300">Content Type:</label>
                    <select
                      value={readerType}
                      onChange={(e) => setReaderType(e.target.value)}
                      className="px-3 py-1 bg-white/5 border border-white/10 rounded text-white"
                    >
                      <option value="json">JSON</option>
                      <option value="markdown">Markdown</option>
                    </select>
                  </div>
                  
                  <textarea
                    value={readerContent}
                    onChange={(e) => setReaderContent(e.target.value)}
                    placeholder={readerType === 'json' ? 'Paste JSON content here...' : 'Paste Markdown content here...'}
                    className="w-full h-96 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm font-mono resize-none"
                  />
                </div>
                
                {/* Output */}
                <div className="space-y-4">
                  <h4 className="text-sm text-gray-300">Parsed Output:</h4>
                  <div className="h-96 p-3 bg-black/20 border border-white/10 rounded-lg overflow-auto">
                    {parsedContent ? (
                      readerType === 'json' ? (
                        <pre className="text-sm text-gray-300">
                          {JSON.stringify(parsedContent, null, 2)}
                        </pre>
                      ) : (
                        <div className="prose prose-invert text-sm max-w-none">
                          {parsedContent.split('\n').map((line, idx) => (
                            <div key={idx}>{line}</div>
                          ))}
                        </div>
                      )
                    ) : (
                      <div className="text-gray-500 text-center mt-8">
                        Paste content to see parsed output
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Live Logs */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">📊 Live Session Log</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setLogs([])}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              title="Clear logs"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                const logData = logs.map(log => ({
                  timestamp: log.timestamp,
                  type: log.type,
                  message: log.message,
                  endpoint: log.endpoint,
                  method: log.method,
                  data: log.data
                }));
                const blob = new Blob([JSON.stringify(logData, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `api-logs-${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              title="Export logs"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="bg-black/20 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
          {logs.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <Terminal className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No log entries yet</p>
              <p className="text-xs mt-1">Execute requests to see live logging</p>
            </div>
          ) : (
            logs.slice(-50).map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={`mb-2 p-3 rounded border ${getLogColor(log.type)}`}
              >
                <div className="flex items-center space-x-2 mb-1">
                  {getLogIcon(log.type)}
                  <span className="text-gray-300 text-xs">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="text-gray-400 text-xs">
                    {log.method} {log.endpoint}
                  </span>
                </div>
                <div className="text-gray-200">{log.message}</div>
                {log.data && (
                  <details className="mt-2">
                    <summary className="text-gray-400 cursor-pointer text-xs">Details</summary>
                    <pre className="text-gray-300 text-xs mt-1 overflow-auto">
                      {JSON.stringify(log.data, null, 2)}
                    </pre>
                  </details>
                )}
              </motion.div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>

      {/* Save Call Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full"
          >
            <h3 className="text-lg font-semibold mb-4">Save API Call</h3>
            <input
              type="text"
              value={callName}
              onChange={(e) => setCallName(e.target.value)}
              placeholder="Enter a name for this API call..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg mb-4"
              onKeyDown={(e) => e.key === 'Enter' && saveCurrentCall()}
            />
            <div className="flex space-x-3">
              <button
                onClick={() => setShowSaveModal(false)}
                className="flex-1 px-4 py-2 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={saveCurrentCall}
                disabled={!callName.trim()}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                Save
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default EnhancedAPIConsole;