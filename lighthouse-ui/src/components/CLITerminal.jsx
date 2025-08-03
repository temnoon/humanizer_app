import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Terminal,
  Play,
  Square,
  Trash2,
  Download,
  ChevronRight,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Copy,
  History,
  Command,
  AlertTriangle,
  Settings,
  Maximize2,
  Minimize2
} from "lucide-react";

const CLITerminal = () => {
  const [command, setCommand] = useState("");
  const [history, setHistory] = useState([]);
  const [commandHistory, setCommandHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [isExecuting, setIsExecuting] = useState(false);
  const [runningCommands, setRunningCommands] = useState(new Map());
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const terminalRef = useRef(null);
  const inputRef = useRef(null);

  // Common HAW commands for quick access
  const quickCommands = [
    { cmd: "haw status", desc: "System health check" },
    { cmd: "haw processes", desc: "Show active processes" },
    { cmd: "haw browse-notebooks list", desc: "List conversations" },
    { cmd: "haw advanced-books --analyze-only", desc: "Preview book generation" },
    { cmd: "haw advanced-books --min-quality 0.4 --max-books 3", desc: "Generate books" },
    { cmd: "haw book-editor", desc: "AI editorial assistant" },
    { cmd: "haw curate-book analyze", desc: "Quick thematic analysis" },
    { cmd: "haw universal-books --source-type notebooks", desc: "Universal book generator" }
  ];

  useEffect(() => {
    // Auto-scroll to bottom when new output is added
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history]);

  useEffect(() => {
    // Focus input when component mounts
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const executeCommand = async (cmdToExecute = command) => {
    if (!cmdToExecute.trim()) return;

    const commandId = Date.now() + Math.random();
    const timestamp = new Date().toLocaleTimeString();
    
    // Add command to history
    const newEntry = {
      id: commandId,
      type: 'command',
      content: cmdToExecute,
      timestamp,
      status: 'running'
    };

    setHistory(prev => [...prev, newEntry]);
    setCommandHistory(prev => [cmdToExecute, ...prev.filter(c => c !== cmdToExecute)].slice(0, 50));
    setHistoryIndex(-1);
    setCommand("");
    setIsExecuting(true);
    setRunningCommands(prev => new Map(prev).set(commandId, { command: cmdToExecute, startTime: Date.now() }));

    try {
      const response = await fetch('http://localhost:8100/api/cli/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          command: cmdToExecute,
          working_directory: '/Users/tem/humanizer-lighthouse',
          timeout: 300000 // 5 minutes
        })
      });

      const result = await response.json();
      const duration = Date.now() - runningCommands.get(commandId)?.startTime || 0;

      // Update command status
      setHistory(prev => prev.map(entry => 
        entry.id === commandId 
          ? { ...entry, status: response.ok ? 'completed' : 'failed', duration }
          : entry
      ));

      // Add output
      if (result.output || result.error) {
        const outputEntry = {
          id: Date.now() + Math.random(),
          type: 'output',
          content: result.output || result.error,
          timestamp: new Date().toLocaleTimeString(),
          status: response.ok ? 'success' : 'error',
          commandId
        };
        setHistory(prev => [...prev, outputEntry]);
      }

      // Add completion info
      const completionEntry = {
        id: Date.now() + Math.random(),
        type: 'completion',
        content: `Command completed in ${(duration / 1000).toFixed(2)}s (exit code: ${result.return_code || 0})`,
        timestamp: new Date().toLocaleTimeString(),
        status: response.ok ? 'success' : 'error',
        commandId
      };
      setHistory(prev => [...prev, completionEntry]);

    } catch (error) {
      console.error('Command execution failed:', error);
      
      // Update command status
      setHistory(prev => prev.map(entry => 
        entry.id === commandId 
          ? { ...entry, status: 'failed' }
          : entry
      ));

      // Add error output
      const errorEntry = {
        id: Date.now() + Math.random(),
        type: 'output',
        content: `Error: ${error.message}`,
        timestamp: new Date().toLocaleTimeString(),
        status: 'error',
        commandId
      };
      setHistory(prev => [...prev, errorEntry]);
    } finally {
      setIsExecuting(false);
      setRunningCommands(prev => {
        const next = new Map(prev);
        next.delete(commandId);
        return next;
      });
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      executeCommand();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (commandHistory.length > 0) {
        const newIndex = Math.min(historyIndex + 1, commandHistory.length - 1);
        setHistoryIndex(newIndex);
        setCommand(commandHistory[newIndex] || "");
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex >= 0) {
        const newIndex = Math.max(historyIndex - 1, -1);
        setHistoryIndex(newIndex);
        setCommand(newIndex >= 0 ? commandHistory[newIndex] : "");
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      // Basic tab completion for haw commands
      if (command.startsWith('haw ') || command === 'haw') {
        const hawCommands = [
          'status', 'processes', 'logs', 'setup',
          'browse-notebooks', 'browse-writing', 'browse-wordclouds',
          'curate-book', 'explore-themes', 'advanced-books',
          'universal-books', 'book-editor', 'book-pipeline'
        ];
        const partial = command.replace('haw ', '');
        const matches = hawCommands.filter(cmd => cmd.startsWith(partial));
        if (matches.length === 1) {
          setCommand(`haw ${matches[0]} `);
        }
      }
    }
  };

  const clearTerminal = () => {
    setHistory([]);
  };

  const stopAllCommands = () => {
    // In a real implementation, this would send kill signals to running processes
    setRunningCommands(new Map());
    setIsExecuting(false);
  };

  const copyOutput = (content) => {
    navigator.clipboard.writeText(content);
  };

  const downloadHistory = () => {
    const content = history.map(entry => {
      const prefix = entry.type === 'command' ? '$ ' : entry.type === 'output' ? '' : '# ';
      return `[${entry.timestamp}] ${prefix}${entry.content}`;
    }).join('\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `haw-terminal-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'running': return <Loader2 className="w-4 h-4 animate-spin text-blue-400" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />;
      default: return <Clock className="w-4 h-4 text-card-secondary" />;
    }
  };

  return (
    <div className={`h-full flex flex-col ${isFullscreen ? 'fixed inset-0 z-50 bg-background' : ''}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border/30 bg-card/30 backdrop-blur-sm">
        <div className="flex items-center space-x-3">
          <Terminal className="w-5 h-5 text-green-400" />
          <h1 className="text-lg font-bold text-foreground">HAW CLI Terminal</h1>
          {runningCommands.size > 0 && (
            <div className="flex items-center space-x-2 text-sm text-blue-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>{runningCommands.size} running</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            onClick={() => setShowHistory(!showHistory)}
            className="p-2 hover:bg-card rounded-lg transition-colors"
            title="Command History"
          >
            <History className="w-4 h-4 text-card-secondary" />
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            onClick={downloadHistory}
            className="p-2 hover:bg-card rounded-lg transition-colors"
            title="Download Session"
          >
            <Download className="w-4 h-4 text-card-secondary" />
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            onClick={clearTerminal}
            className="p-2 hover:bg-card rounded-lg transition-colors"
            title="Clear Terminal"
          >
            <Trash2 className="w-4 h-4 text-card-secondary" />
          </motion.button>
          
          {runningCommands.size > 0 && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              onClick={stopAllCommands}
              className="p-2 hover:bg-destructive/20 rounded-lg transition-colors"
              title="Stop All Commands"
            >
              <Square className="w-4 h-4 text-red-400" />
            </motion.button>
          )}
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 hover:bg-card rounded-lg transition-colors"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4 text-card-secondary" />
            ) : (
              <Maximize2 className="w-4 h-4 text-card-secondary" />
            )}
          </motion.button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Quick Commands Sidebar */}
        <div className="w-80 border-r border-border/30 bg-card/20 overflow-y-auto">
          <div className="p-4">
            <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center">
              <Command className="w-4 h-4 mr-2" />
              Quick Commands
            </h3>
            <div className="space-y-2">
              {quickCommands.map((item, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.02, x: 4 }}
                  onClick={() => setCommand(item.cmd)}
                  className="w-full text-left p-3 rounded-lg hover:bg-card/50 transition-colors border border-border/20"
                >
                  <div className="font-mono text-sm text-primary mb-1">{item.cmd}</div>
                  <div className="text-xs text-card-secondary">{item.desc}</div>
                </motion.button>
              ))}
            </div>
            
            {/* Command History */}
            {showHistory && commandHistory.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-foreground mb-3">Recent Commands</h3>
                <div className="space-y-1">
                  {commandHistory.slice(0, 10).map((cmd, index) => (
                    <motion.button
                      key={index}
                      whileHover={{ scale: 1.02 }}
                      onClick={() => setCommand(cmd)}
                      className="w-full text-left p-2 rounded text-xs font-mono text-card-secondary hover:text-foreground hover:bg-card/30 transition-colors"
                    >
                      {cmd}
                    </motion.button>
                  ))}
                </div>
              </div>
            )}
            
            {/* System Info */}
            <div className="mt-6 p-3 bg-background/50 rounded-lg border border-border/20">
              <h4 className="text-xs font-semibold text-foreground mb-2">Terminal Info</h4>
              <div className="text-xs text-card-secondary space-y-1">
                <div>Working Dir: ~/humanizer-lighthouse</div>
                <div>Shell: HAW CLI Interface</div>
                <div>Session: {history.length} commands</div>
              </div>
            </div>
          </div>
        </div>

        {/* Terminal Content */}
        <div className="flex-1 flex flex-col">
          {/* Terminal Output */}
          <div 
            ref={terminalRef}
            className="flex-1 overflow-y-auto p-4 bg-gray-900 font-mono text-sm"
          >
            {history.length === 0 && (
              <div className="text-green-400 mb-4">
                <div>HAW CLI Terminal - Humanizer Archive Wrapper</div>
                <div className="text-gray-400 mt-2">
                  Type 'haw help' for available commands or use the quick commands sidebar.
                  Use ↑/↓ arrow keys to navigate command history.
                </div>
              </div>
            )}
            
            <AnimatePresence>
              {history.map((entry) => (
                <motion.div
                  key={entry.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-2"
                >
                  {entry.type === 'command' && (
                    <div className="flex items-center space-x-2 text-green-400">
                      <span className="text-gray-400">[{entry.timestamp}]</span>
                      <span>$</span>
                      <span>{entry.content}</span>
                      {getStatusIcon(entry.status)}
                      {entry.duration && (
                        <span className="text-gray-400 text-xs">
                          ({(entry.duration / 1000).toFixed(2)}s)
                        </span>
                      )}
                    </div>
                  )}
                  
                  {entry.type === 'output' && (
                    <div className="group relative">
                      <pre className={`whitespace-pre-wrap ${
                        entry.status === 'error' ? 'text-red-400' : 'text-gray-300'
                      }`}>
                        {entry.content}
                      </pre>
                      <button
                        onClick={() => copyOutput(entry.content)}
                        className="absolute top-0 right-0 p-1 opacity-0 group-hover:opacity-100 hover:bg-gray-700 rounded transition-all"
                        title="Copy output"
                      >
                        <Copy className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                  
                  {entry.type === 'completion' && (
                    <div className={`text-xs ${
                      entry.status === 'error' ? 'text-red-400' : 'text-gray-500'
                    }`}>
                      {entry.content}
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
            
            {isExecuting && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center space-x-2 text-blue-400"
              >
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Executing command...</span>
              </motion.div>
            )}
          </div>

          {/* Command Input */}
          <div className="border-t border-border/30 bg-gray-900 p-4">
            <div className="flex items-center space-x-2 font-mono">
              <span className="text-green-400">$</span>
              <input
                ref={inputRef}
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Enter HAW command..."
                disabled={isExecuting}
                className="flex-1 bg-transparent text-gray-300 placeholder-gray-500 border-none outline-none disabled:opacity-50"
                autoComplete="off"
                spellCheck="false"
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => executeCommand()}
                disabled={!command.trim() || isExecuting}
                className="p-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Execute command (Enter)"
              >
                <Play className="w-4 h-4" />
              </motion.button>
            </div>
            
            {command.trim() && (
              <div className="mt-2 text-xs text-gray-500">
                Press Enter to execute, ↑/↓ for history, Tab for completion
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CLITerminal;