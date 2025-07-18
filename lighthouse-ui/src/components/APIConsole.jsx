import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
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
  Settings
} from 'lucide-react';

const APIConsole = () => {
  const [logs, setLogs] = useState([]);
  const [selectedEndpoint, setSelectedEndpoint] = useState('/health');
  const [requestMethod, setRequestMethod] = useState('GET');
  const [requestBody, setRequestBody] = useState('');
  const [requestHeaders, setRequestHeaders] = useState('{}');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [logFilter, setLogFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const [wsConnections, setWsConnections] = useState({});
  const [copied, setCopied] = useState(false);
  const logsEndRef = useRef(null);

  const endpoints = [
    // Core APIs
    { method: 'GET', path: '/health', description: 'Health check' },
    { method: 'GET', path: '/models', description: 'Available models' },
    { method: 'GET', path: '/configurations', description: 'Personas, namespaces, styles' },
    { method: 'POST', path: '/transform', description: '5-step narrative transformation' },
    
    // LLM Configuration
    { method: 'GET', path: '/api/llm/configurations', description: 'LLM configurations' },
    { method: 'POST', path: '/api/llm/configurations', description: 'Save LLM config' },
    { method: 'GET', path: '/api/llm/status', description: 'Provider status' },
    { method: 'GET', path: '/api/llm/keys', description: 'Stored API keys' },
    { method: 'POST', path: '/api/llm/keys/{provider}', description: 'Store API key' },
    
    // Maieutic Dialogue
    { method: 'POST', path: '/maieutic/start', description: 'Start dialogue session' },
    { method: 'POST', path: '/maieutic/question', description: 'Generate question' },
    { method: 'POST', path: '/maieutic/answer', description: 'Submit answer' },
    { method: 'POST', path: '/maieutic/complete', description: 'Complete session' },
    
    // Translation & Analysis
    { method: 'POST', path: '/translation/roundtrip', description: 'Round-trip translation' },
    { method: 'POST', path: '/translation/stability', description: 'Translation stability' },
    
    // Vision
    { method: 'POST', path: '/vision/analyze', description: 'Image analysis' },
    { method: 'POST', path: '/vision/transcribe', description: 'Handwriting transcription' },
    { method: 'POST', path: '/image/generate', description: 'Image generation' },
    
    // Lamish Analysis
    { method: 'POST', path: '/lamish/analyze', description: 'Extract meaning' },
    { method: 'GET', path: '/lamish/concepts', description: 'Get concepts' },
    { method: 'GET', path: '/lamish/stats', description: 'Dashboard stats' },
    { method: 'POST', path: '/lamish/extract-attributes', description: 'Extract attributes' },
    { method: 'POST', path: '/lamish/inspect-prompts', description: 'Get prompts' },
  ];

  const sampleBodies = {
    '/transform': JSON.stringify({
      narrative: "The old lighthouse stood against the storm.",
      target_persona: "philosopher",
      target_namespace: "lamish-galaxy",
      target_style: "poetic",
      show_steps: true
    }, null, 2),
    '/maieutic/start': JSON.stringify({
      narrative: "Technology is changing how we communicate.",
      focus_area: "implications"
    }, null, 2),
    '/translation/roundtrip': JSON.stringify({
      text: "The essence of wisdom lies in understanding.",
      source_language: "english",
      intermediate_languages: ["spanish", "french", "german"]
    }, null, 2),
    '/vision/analyze': JSON.stringify({
      image_url: "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
      analysis_type: "comprehensive"
    }, null, 2),
    '/lamish/analyze': JSON.stringify({
      content: "The lighthouse beacon cuts through the darkness."
    }, null, 2),
    '/api/llm/configurations': JSON.stringify({
      task_configs: {
        deconstruct: {
          provider: "openai",
          model: "gpt-4-turbo-preview",
          parameters: { temperature: 0.3, max_tokens: 1000 }
        }
      }
    }, null, 2)
  };

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  useEffect(() => {
    // Set sample body when endpoint changes
    if (sampleBodies[selectedEndpoint]) {
      setRequestBody(sampleBodies[selectedEndpoint]);
    } else if (requestMethod === 'POST') {
      setRequestBody('{}');
    } else {
      setRequestBody('');
    }
  }, [selectedEndpoint, requestMethod]);

  const addLog = (type, message, data = null) => {
    const timestamp = new Date().toISOString();
    const logEntry = {
      id: Date.now() + Math.random(),
      timestamp,
      type, // success, error, info, request, response
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
        body: requestBody
      });

      const options = {
        method: requestMethod,
        headers: {
          'Content-Type': 'application/json',
          ...JSON.parse(requestHeaders || '{}')
        }
      };

      if (requestMethod !== 'GET' && requestBody.trim()) {
        options.body = requestBody;
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

  const clearLogs = () => {
    setLogs([]);
    setResponse(null);
  };

  const exportLogs = () => {
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
  };

  const copyResponse = () => {
    if (response) {
      navigator.clipboard.writeText(JSON.stringify(response.data || response, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesFilter = logFilter === 'all' || log.type === logFilter;
    const matchesSearch = !searchTerm || 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.endpoint.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getLogIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'info': return <Info className="w-4 h-4 text-blue-400" />;
      case 'request': return <Play className="w-4 h-4 text-yellow-400" />;
      case 'response': return <CheckCircle className="w-4 h-4 text-green-400" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'success': return 'border-green-500/20 bg-green-500/5';
      case 'error': return 'border-red-500/20 bg-red-500/5';
      case 'info': return 'border-blue-500/20 bg-blue-500/5';
      case 'request': return 'border-yellow-500/20 bg-yellow-500/5';
      case 'response': return 'border-green-500/20 bg-green-500/5';
      default: return 'border-gray-500/20 bg-gray-500/5';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Terminal className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-semibold text-white">API Console</h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={clearLogs}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              title="Clear logs"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <button
              onClick={exportLogs}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              title="Export logs"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Request Configuration */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Request Setup */}
          <div className="space-y-4">
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
                {endpoints.map(endpoint => (
                  <option key={endpoint.path} value={endpoint.path}>
                    {endpoint.path} - {endpoint.description}
                  </option>
                ))}
              </select>
            </div>

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

            {requestMethod !== 'GET' && (
              <div>
                <label className="block text-sm text-gray-300 mb-2">Request Body (JSON)</label>
                <textarea
                  value={requestBody}
                  onChange={(e) => setRequestBody(e.target.value)}
                  className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm font-mono"
                  rows={8}
                  placeholder="{}"
                />
              </div>
            )}

            <button
              onClick={executeRequest}
              disabled={isLoading}
              className="w-full px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Executing...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Execute Request</span>
                </>
              )}
            </button>
          </div>

          {/* Right: Response */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-white">Response</h3>
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
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-sm font-medium ${response.error ? 'text-red-400' : 'text-green-400'}`}>
                    {response.status ? `${response.status} ${response.statusText}` : 'Network Error'}
                  </span>
                  <span className="text-sm text-gray-400">{response.duration}ms</span>
                </div>
                <pre className="text-sm text-gray-300 overflow-auto max-h-64">
                  {JSON.stringify(response.data || { error: response.message }, null, 2)}
                </pre>
              </div>
            ) : (
              <div className="p-4 border border-gray-500/20 bg-gray-500/5 rounded-lg text-center text-gray-400">
                No response yet
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Live Logs */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">Live Session Log</h3>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Search className="w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search logs..."
                className="px-3 py-1 bg-white/5 border border-white/10 rounded text-sm text-white"
              />
            </div>
            <select
              value={logFilter}
              onChange={(e) => setLogFilter(e.target.value)}
              className="px-3 py-1 bg-white/5 border border-white/10 rounded text-sm text-white"
            >
              <option value="all">All Logs</option>
              <option value="request">Requests</option>
              <option value="success">Success</option>
              <option value="error">Errors</option>
              <option value="info">Info</option>
            </select>
            <label className="flex items-center space-x-2 text-sm text-gray-300">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="w-4 h-4"
              />
              <span>Auto-scroll</span>
            </label>
          </div>
        </div>

        <div className="bg-black/20 rounded-lg p-4 h-96 overflow-y-auto font-mono text-sm">
          {filteredLogs.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              No log entries yet. Execute a request to see live logging.
            </div>
          ) : (
            filteredLogs.map((log) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
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
    </div>
  );
};

export default APIConsole;