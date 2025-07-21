import React, { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Archive,
  Search,
  Filter,
  Database,
  Clock,
  User,
  MessageSquare,
  BarChart3,
  Download,
  Upload,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  Eye,
  Layers,
  Hash,
  Zap,
  Brain,
  TreePine,
  Network,
  Loader2,
  FileText,
  Calendar,
  Tag,
  Folder,
  FileArchive,
  Image,
  Music,
  Video,
  File,
  Activity,
  Check,
  Plus,
  X,
  Save,
  Edit3,
  Trash2
} from "lucide-react";
import { cn } from "../utils";

const ArchiveExplorer = ({ onNavigateToConversation }) => {
  // State management
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSourceTypes, setSelectedSourceTypes] = useState(["node_conversation"]);
  const [selectedAuthor, setSelectedAuthor] = useState("");
  const [dateRange, setDateRange] = useState({ from: "", to: "" });
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [archiveStats, setArchiveStats] = useState(null);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversationThread, setConversationThread] = useState([]);
  const [embeddingStats, setEmbeddingStats] = useState(null);
  const [showEmbeddingPanel, setShowEmbeddingPanel] = useState(false);
  const [semanticSearchMode, setSemanticSearchMode] = useState(false);
  const [chunkAnalysis, setChunkAnalysis] = useState(null);
  const [processingProgress, setProcessingProgress] = useState(null);
  const [searchType, setSearchType] = useState("text"); // "text" or "semantic"
  const [searchLimit, setSearchLimit] = useState(20);
  const [lastSearchTime, setLastSearchTime] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingSessions, setProcessingSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [websocket, setWebsocket] = useState(null);
  const [showFileDialog, setShowFileDialog] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [archiveAnalysis, setArchiveAnalysis] = useState(null);
  const [importLogs, setImportLogs] = useState([]);
  const [showLogs, setShowLogs] = useState(false);
  const [processingStatus, setProcessingStatus] = useState('idle'); // 'idle', 'processing', 'completed', 'failed'
  
  // New features state
  const [conversations, setConversations] = useState([]);
  const [conversationsPagination, setConversationsPagination] = useState({});
  const [selectedConversationMessages, setSelectedConversationMessages] = useState([]);
  const [messagesPagination, setMessagesPagination] = useState({});
  const [savedSearches, setSavedSearches] = useState([]);
  const [transformationQueue, setTransformationQueue] = useState([]);
  const [selectedForTransformation, setSelectedForTransformation] = useState([]);
  const [currentView, setCurrentView] = useState("search"); // "search", "browse", "queue", "saved"
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [showFullMessage, setShowFullMessage] = useState(null);
  const [showSaveSearchDialog, setShowSaveSearchDialog] = useState(false);

  // Archive API base URL (Enhanced Archive API)
  const ARCHIVE_API_BASE = "http://localhost:7200";
  const RAILS_API_BASE = "http://localhost:3000/api/v1/unified_archive";

  // Load archive statistics on mount
  useEffect(() => {
    loadArchiveStats();
    loadEmbeddingStats();
    loadProcessingSessions();
    loadImportLogs();
    loadSavedSearches();
    loadTransformationQueue();
  }, []);

  // Load conversations when browse view is selected
  useEffect(() => {
    if (currentView === "browse") {
      loadConversations();
    }
  }, [currentView]);

  // Auto-refresh logs when processing
  useEffect(() => {
    if (isProcessing) {
      const logInterval = setInterval(loadImportLogs, 2000); // Refresh every 2 seconds
      return () => clearInterval(logInterval);
    }
  }, [isProcessing]);

  // Setup WebSocket for progress updates
  useEffect(() => {
    if (currentSessionId && !websocket) {
      const ws = new WebSocket(`ws://localhost:7200/ws/progress/${currentSessionId}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected for session:', currentSessionId);
        setWebsocket(ws);
      };
      
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'progress_update') {
          setProcessingProgress(message.data);
        } else if (message.type === 'processing_complete') {
          setIsProcessing(false);
          loadArchiveStats(); // Refresh stats after completion
        }
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setWebsocket(null);
      };
      
      return () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
    }
  }, [currentSessionId, websocket]);

  const loadArchiveStats = async () => {
    try {
      const response = await fetch(`${RAILS_API_BASE}/statistics`);
      if (response.ok) {
        const stats = await response.json();
        setArchiveStats(stats);
      }
    } catch (error) {
      console.warn("Failed to load archive statistics:", error);
    }
  };

  const loadEmbeddingStats = async () => {
    try {
      const response = await fetch(`${ARCHIVE_API_BASE}/embeddings/statistics`);
      if (response.ok) {
        const stats = await response.json();
        setEmbeddingStats(stats);
      }
    } catch (error) {
      console.warn("Failed to load embedding statistics:", error);
    }
  };

  const loadProcessingSessions = async () => {
    try {
      const response = await fetch(`${ARCHIVE_API_BASE}/progress/sessions`);
      if (response.ok) {
        const data = await response.json();
        setProcessingSessions(data.sessions || []);
        
        // Check if there's an active session
        const activeSessions = data.sessions.filter(s => 
          s.status === 'processing' || s.status === 'initializing'
        );
        if (activeSessions.length > 0) {
          setCurrentSessionId(activeSessions[0].session_id);
          setIsProcessing(true);
        }
      }
    } catch (error) {
      console.warn("Failed to load processing sessions:", error);
    }
  };

  const loadImportLogs = async () => {
    try {
      const response = await fetch(`${ARCHIVE_API_BASE}/logs/import?lines=100`);
      if (response.ok) {
        const data = await response.json();
        setImportLogs(data.log_entries || []);
      }
    } catch (error) {
      console.warn("Failed to load import logs:", error);
    }
  };

  const handleFileSelection = () => {
    setShowFileDialog(true);
  };

  const analyzeSelectedFiles = async (files) => {
    const analysis = {
      total_files: files.length,
      conversations: 0,
      media_files: 0,
      other_files: 0,
      file_types: {},
      size_mb: 0,
      estimated_conversations: 0
    };

    for (const file of files) {
      analysis.size_mb += file.size / (1024 * 1024);
      
      const ext = file.name.split('.').pop().toLowerCase();
      analysis.file_types[ext] = (analysis.file_types[ext] || 0) + 1;
      
      if (file.name === 'conversation.json' || file.name.includes('conversations')) {
        analysis.conversations++;
      } else if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp3', 'mp4', 'wav', 'pdf'].includes(ext)) {
        analysis.media_files++;
      } else {
        analysis.other_files++;
      }
    }

    // Estimate conversations from folder structure
    const folderNames = [...new Set(files.map(f => f.webkitRelativePath?.split('/')[0] || f.name))];
    analysis.estimated_conversations = Math.max(analysis.conversations, folderNames.length);

    return analysis;
  };

  const handleFilesSelected = async (files) => {
    setSelectedFiles(Array.from(files));
    const analysis = await analyzeSelectedFiles(Array.from(files));
    setArchiveAnalysis(analysis);
  };

  const uploadAndProcessFiles = async () => {
    try {
      setIsProcessing(true);
      setProcessingStatus('processing');
      setUploadProgress(0);
      setShowLogs(true); // Auto-show logs when processing starts

      // Create FormData for file upload
      const formData = new FormData();
      selectedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file);
        formData.append(`path_${index}`, file.webkitRelativePath || file.name);
      });

      // Upload files with progress tracking
      const response = await fetch(`${ARCHIVE_API_BASE}/upload-archive`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        setProcessingStatus('failed');
        throw new Error(`Failed to upload archive: ${response.status} ${errorText}`);
      }

      const uploadResult = await response.json();
      console.log('Upload completed:', uploadResult);

      // Start processing the uploaded archive
      const processResponse = await fetch(`${ARCHIVE_API_BASE}/smart-processing/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          archive_path: uploadResult.archive_path,
          max_conversations: null
        })
      });

      if (processResponse.ok) {
        const data = await processResponse.json();
        setCurrentSessionId(data.session_id);
        setProcessingStatus('completed');
        console.log('Processing started:', data);
      } else {
        setProcessingStatus('failed');
        throw new Error('Failed to start processing');
      }

    } catch (error) {
      console.error('Failed to upload and process files:', error);
      setIsProcessing(false);
      setProcessingStatus('failed');
      // Load logs immediately to show the error
      loadImportLogs();
    }
  };

  const startArchiveProcessing = async (maxConversations = null) => {
    // Open file dialog instead of using fixed path
    handleFileSelection();
  };

  const startFolderProcessing = async () => {
    try {
      setIsProcessing(true);
      setProcessingStatus('processing');
      setShowLogs(true);

      const response = await fetch(`${ARCHIVE_API_BASE}/process-local-folder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          folder_path: "/Users/tem/nab/exploded_archive_node",
          max_conversations: null
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSessionId(data.session_id);
        console.log('Folder processing started:', data);
      } else {
        throw new Error('Failed to start folder processing');
      }

    } catch (error) {
      console.error('Failed to start folder processing:', error);
      setIsProcessing(false);
      setProcessingStatus('failed');
      loadImportLogs();
    }
  };

  const performSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setLastSearchTime(Date.now());
    
    try {
      // Build URL parameters for the PostgreSQL search API
      const params = new URLSearchParams({
        query: searchQuery,
        limit: searchLimit.toString(),
        semantic_search: (searchType === "semantic").toString()
      });

      // Add optional filters
      if (selectedAuthor) {
        params.append("author", selectedAuthor);
      }
      if (dateRange.from) {
        params.append("date_from", dateRange.from);
      }
      if (dateRange.to) {
        params.append("date_to", dateRange.to);
      }
      if (selectedSourceTypes.length > 0) {
        selectedSourceTypes.forEach(type => params.append("source_types", type));
      }

      const response = await fetch(`${ARCHIVE_API_BASE}/search?${params}`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });

      if (response.ok) {
        const results = await response.json();
        setSearchResults(results.results || []);
        
        // Store search metadata
        setChunkAnalysis({
          total_found: results.total_found,
          query_used: results.query_used,
          search_type: results.search_type,
          search_time_ms: Date.now() - lastSearchTime
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || "Search failed");
      }
    } catch (error) {
      console.error("Search error:", error);
      setSearchResults([]);
      setChunkAnalysis({ error: error.message });
    } finally {
      setIsSearching(false);
    }
  };

  // New functions for enhanced features
  const loadConversations = async (page = 1, sortBy = "timestamp", order = "desc") => {
    try {
      const response = await fetch(
        `${ARCHIVE_API_BASE}/conversations?page=${page}&limit=50&sort_by=${sortBy}&order=${order}`
      );
      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
        setConversationsPagination(data.pagination || {});
      }
    } catch (error) {
      console.error("Failed to load conversations:", error);
    }
  };

  const loadConversationMessages = async (conversationId, page = 1) => {
    try {
      const response = await fetch(
        `${ARCHIVE_API_BASE}/conversations/${conversationId}/messages?page=${page}&limit=100`
      );
      if (response.ok) {
        const data = await response.json();
        setSelectedConversationMessages(data.messages || []);
        setMessagesPagination(data.pagination || {});
        setCurrentConversationId(conversationId);
      }
    } catch (error) {
      console.error("Failed to load conversation messages:", error);
    }
  };

  const loadSavedSearches = async () => {
    try {
      const response = await fetch(`${ARCHIVE_API_BASE}/saved-searches`);
      if (response.ok) {
        const data = await response.json();
        setSavedSearches(data.searches || []);
      }
    } catch (error) {
      console.error("Failed to load saved searches:", error);
    }
  };

  const saveCurrentSearch = async (name) => {
    try {
      const response = await fetch(`${ARCHIVE_API_BASE}/saved-searches`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          name,
          query: searchQuery,
          search_type: searchType,
          filters: JSON.stringify({
            author: selectedAuthor,
            date_from: dateRange.from,
            date_to: dateRange.to,
            source_types: selectedSourceTypes
          })
        })
      });
      if (response.ok) {
        loadSavedSearches();
        setShowSaveSearchDialog(false);
      }
    } catch (error) {
      console.error("Failed to save search:", error);
    }
  };

  const loadTransformationQueue = async () => {
    try {
      const response = await fetch(`${ARCHIVE_API_BASE}/transformation-queue`);
      if (response.ok) {
        const data = await response.json();
        setTransformationQueue(data.queue || []);
      }
    } catch (error) {
      console.error("Failed to load transformation queue:", error);
    }
  };

  const addToTransformationQueue = async (contentIds, transformationType = "humanize") => {
    try {
      const response = await fetch(`${ARCHIVE_API_BASE}/transformation-queue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content_ids: contentIds,
          transformation_type: transformationType,
          priority: "normal"
        })
      });
      if (response.ok) {
        loadTransformationQueue();
        setSelectedForTransformation([]);
      }
    } catch (error) {
      console.error("Failed to add to transformation queue:", error);
    }
  };

  const handleConversationSelect = (result) => {
    if (onNavigateToConversation) {
      if (result.content_type === "conversation") {
        // Navigate to the conversation browser with this conversation
        onNavigateToConversation(result.id);
      } else if (result.content_type === "message") {
        // Navigate to the conversation browser with the parent conversation and highlight this message
        onNavigateToConversation(result.conversation_id, result.id);
      } else {
        // Fallback: try to use the conversation ID from the result
        const conversationId = result.conversation_id || result.parent_id || result.id;
        onNavigateToConversation(conversationId, result.id);
      }
    } else {
      // Fallback to original behavior if no navigation callback provided
      if (result.content_type === "conversation") {
        loadConversationMessages(result.id);
        setCurrentView("conversation");
      } else {
        setSelectedConversation(result);
        loadConversationThread(result.id);
      }
    }
  };

  const toggleMessageSelection = (messageId) => {
    setSelectedForTransformation(prev => 
      prev.includes(messageId) 
        ? prev.filter(id => id !== messageId)
        : [...prev, messageId]
    );
  };

  const loadConversationThread = async (contentId) => {
    try {
      const response = await fetch(`${RAILS_API_BASE}/${contentId}/thread`);
      if (response.ok) {
        const thread = await response.json();
        setConversationThread(thread);
      }
    } catch (error) {
      console.error("Failed to load conversation thread:", error);
    }
  };

  const renderProgressDisplay = () => {
    if (!isProcessing && !processingProgress) {
      return (
        <div className="text-center py-4 text-muted-foreground">
          No active processing
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {/* Simple progress indicator */}
        <div className="flex items-center justify-center space-x-3">
          <div className="w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-lg">Processing archive...</span>
        </div>
        
        {processingProgress && (
          <div className="text-sm text-center text-muted-foreground">
            {processingProgress.stats.conversations_processed || 0} conversations processed
          </div>
        )}
      </div>
    );
  };

  // Memoized statistics display
  const statsDisplay = useMemo(() => {
    if (!archiveStats) return null;

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Database className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-muted-foreground">Total Content</span>
          </div>
          <div className="text-2xl font-bold">{archiveStats.total_content?.toLocaleString() || 0}</div>
        </div>
        
        <div className="glass rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <MessageSquare className="w-4 h-4 text-green-400" />
            <span className="text-sm text-muted-foreground">Conversations</span>
          </div>
          <div className="text-2xl font-bold">{archiveStats.conversations_count?.toLocaleString() || 0}</div>
        </div>
        
        <div className="glass rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <BarChart3 className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-muted-foreground">Avg Quality</span>
          </div>
          <div className="text-2xl font-bold">{(archiveStats.average_quality_score || 0).toFixed(2)}</div>
        </div>
        
        <div className="glass rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Archive className="w-4 h-4 text-yellow-400" />
            <span className="text-sm text-muted-foreground">Sources</span>
          </div>
          <div className="text-2xl font-bold">{Object.keys(archiveStats.by_source_type || {}).length}</div>
        </div>
      </div>
    );
  }, [archiveStats]);

  const sourceTypes = [
    { id: "node_conversation", label: "ChatGPT Conversations", color: "text-green-400" },
    { id: "twitter", label: "Twitter/X", color: "text-blue-400" },
    { id: "email", label: "Email", color: "text-yellow-400" },
    { id: "slack", label: "Slack", color: "text-purple-400" },
    { id: "discord", label: "Discord", color: "text-indigo-400" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Archive className="w-6 h-6 text-purple-400" />
            <div>
              <h2 className="text-2xl font-bold">Archive Explorer</h2>
              <p className="text-muted-foreground">Search and explore your unified PostgreSQL archive</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowEmbeddingPanel(!showEmbeddingPanel)}
              className={cn(
                "px-4 py-2 rounded-lg transition-colors",
                showEmbeddingPanel ? "bg-purple-600 text-white" : "glass hover:bg-white/10"
              )}
            >
              <Brain className="w-4 h-4 mr-2" />
              Embedding System
            </button>
            <button
              onClick={() => startArchiveProcessing(10)}
              disabled={isProcessing}
              className={cn(
                "px-4 py-2 rounded-lg transition-colors",
                isProcessing 
                  ? "bg-gray-600 text-gray-300 cursor-not-allowed" 
                  : "bg-green-600 hover:bg-green-700 text-white"
              )}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Start Import
                </>
              )}
            </button>
            <button
              onClick={() => startFolderProcessing()}
              disabled={isProcessing}
              className={cn(
                "px-4 py-2 rounded-lg transition-colors",
                isProcessing 
                  ? "bg-gray-600 text-gray-300 cursor-not-allowed" 
                  : "bg-blue-600 hover:bg-blue-700 text-white"
              )}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Folder className="w-4 h-4 mr-2" />
                  Process Local Folder
                </>
              )}
            </button>
            <button
              onClick={loadArchiveStats}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Statistics */}
        {statsDisplay}
        
        {/* View Navigation */}
        <div className="mt-6 border-t border-white/10 pt-4">
          <div className="flex space-x-1 bg-black/20 p-1 rounded-lg">
            <button
              onClick={() => setCurrentView("search")}
              className={cn(
                "flex-1 px-4 py-2 text-sm font-medium rounded transition-colors",
                currentView === "search"
                  ? "bg-purple-600 text-white"
                  : "text-gray-300 hover:text-white hover:bg-white/10"
              )}
            >
              <Search className="w-4 h-4 inline mr-2" />
              Search Archive
            </button>
            <button
              onClick={() => setCurrentView("browse")}
              className={cn(
                "flex-1 px-4 py-2 text-sm font-medium rounded transition-colors",
                currentView === "browse"
                  ? "bg-purple-600 text-white"
                  : "text-gray-300 hover:text-white hover:bg-white/10"
              )}
            >
              <MessageSquare className="w-4 h-4 inline mr-2" />
              Browse Conversations
            </button>
            <button
              onClick={() => setCurrentView("saved")}
              className={cn(
                "flex-1 px-4 py-2 text-sm font-medium rounded transition-colors",
                currentView === "saved"
                  ? "bg-purple-600 text-white"
                  : "text-gray-300 hover:text-white hover:bg-white/10"
              )}
            >
              <Archive className="w-4 h-4 inline mr-2" />
              Saved Searches ({savedSearches.length})
            </button>
            <button
              onClick={() => setCurrentView("queue")}
              className={cn(
                "flex-1 px-4 py-2 text-sm font-medium rounded transition-colors",
                currentView === "queue"
                  ? "bg-purple-600 text-white"
                  : "text-gray-300 hover:text-white hover:bg-white/10"
              )}
            >
              <Zap className="w-4 h-4 inline mr-2" />
              Transformation Queue ({transformationQueue.length})
            </button>
          </div>
        </div>
      </motion.div>

      {/* Embedding System Panel */}
      <AnimatePresence>
        {showEmbeddingPanel && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center space-x-2 mb-4">
              <Brain className="w-5 h-5 text-purple-400" />
              <h3 className="text-xl font-semibold">Advanced Embedding System</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Chunking Strategy */}
              <div className="space-y-4">
                <h4 className="font-medium flex items-center space-x-2">
                  <Hash className="w-4 h-4" />
                  <span>Chunking Strategy</span>
                </h4>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between p-3 glass rounded-lg">
                    <span>Chunk Size</span>
                    <span className="font-mono text-blue-400">240 words</span>
                  </div>
                  <div className="flex items-center justify-between p-3 glass rounded-lg">
                    <span>Overlap</span>
                    <span className="font-mono text-green-400">50 words</span>
                  </div>
                  <div className="flex items-center justify-between p-3 glass rounded-lg">
                    <span>Summary Levels</span>
                    <span className="font-mono text-purple-400">3 deep</span>
                  </div>
                </div>
              </div>

              {/* Embedding Stats */}
              <div className="space-y-4">
                <h4 className="font-medium flex items-center space-x-2">
                  <BarChart3 className="w-4 h-4" />
                  <span>Embedding Statistics</span>
                </h4>
                {embeddingStats ? (
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center justify-between p-3 glass rounded-lg">
                      <span>Total Chunks</span>
                      <span className="font-mono text-blue-400">{embeddingStats.total_chunks?.toLocaleString() || 0}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 glass rounded-lg">
                      <span>Summary Chunks</span>
                      <span className="font-mono text-green-400">{embeddingStats.summary_chunks?.toLocaleString() || 0}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 glass rounded-lg">
                      <span>Vector Dimension</span>
                      <span className="font-mono text-purple-400">{embeddingStats.vector_dimension || 1536}</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-muted-foreground text-sm">Loading embedding statistics...</div>
                )}
              </div>

              {/* Semantic Matching */}
              <div className="space-y-4">
                <h4 className="font-medium flex items-center space-x-2">
                  <Network className="w-4 h-4" />
                  <span>Semantic Matching</span>
                </h4>
                <div className="space-y-3">
                  <label className="flex items-center space-x-2 text-sm">
                    <input
                      type="checkbox"
                      checked={semanticSearchMode}
                      onChange={(e) => setSemanticSearchMode(e.target.checked)}
                      className="rounded border-gray-600 bg-gray-700 text-purple-500"
                    />
                    <span>Enable semantic search</span>
                  </label>
                  
                  <div className="p-3 glass rounded-lg text-sm">
                    <div className="flex items-center space-x-2 mb-2">
                      <TreePine className="w-4 h-4 text-green-400" />
                      <span className="font-medium">Multi-Level Matching</span>
                    </div>
                    <div className="text-muted-foreground">
                      • Chunk-level: Direct content similarity<br/>
                      • Section-level: Paragraph context<br/>
                      • Document-level: Big picture themes
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Simple Progress Section */}
      {(processingStatus === 'processing' || processingStatus === 'completed') && (
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Activity className="mr-2" size={20} />
            Processing Progress
          </h3>
          
          {renderProgressDisplay()}
        </div>
      )}

      {/* Processing Progress Panel */}
      <AnimatePresence>
        {(isProcessing || processingProgress) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center space-x-2 mb-4">
              <Zap className="w-5 h-5 text-green-400" />
              <h3 className="text-xl font-semibold">Archive Processing Progress</h3>
              {processingProgress && (
                <span className="px-2 py-1 bg-green-600/20 text-green-300 text-sm rounded-full">
                  {(processingProgress.overall_progress * 100).toFixed(1)}% Complete
                </span>
              )}
            </div>
            
            {processingProgress ? (
              <div className="space-y-4">
                {/* Overall Progress Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Overall Progress</span>
                    <span>{(processingProgress.overall_progress * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${processingProgress.overall_progress * 100}%` }}
                    />
                  </div>
                </div>

                {/* Current Step */}
                <div className="p-3 glass rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    <span className="font-medium">Current Step: {processingProgress.current_step}</span>
                  </div>
                </div>

                {/* Step Progress */}
                <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
                  {processingProgress.steps.map((step, index) => (
                    <div key={step.id} className="p-3 glass rounded-lg">
                      <div className="flex items-center space-x-2 mb-2">
                        {step.status === 'completed' ? (
                          <Check className="w-4 h-4 text-green-400" />
                        ) : step.status === 'processing' ? (
                          <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                        ) : step.status === 'failed' ? (
                          <span className="w-4 h-4 text-red-400">✕</span>
                        ) : (
                          <Clock className="w-4 h-4 text-gray-400" />
                        )}
                        <span className="text-sm font-medium">{step.name}</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-1">
                        <div 
                          className={cn(
                            "h-1 rounded-full transition-all duration-300",
                            step.status === 'completed' ? "bg-green-500" :
                            step.status === 'processing' ? "bg-blue-500" :
                            step.status === 'failed' ? "bg-red-500" : "bg-gray-600"
                          )}
                          style={{ width: `${step.progress * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Statistics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-white/10">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">
                      {processingProgress.statistics.processed_conversations}
                    </div>
                    <div className="text-sm text-muted-foreground">Processed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">
                      {processingProgress.statistics.total_chunks}
                    </div>
                    <div className="text-sm text-muted-foreground">Chunks</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">
                      {processingProgress.statistics.total_embeddings}
                    </div>
                    <div className="text-sm text-muted-foreground">Embeddings</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-400">
                      {processingProgress.statistics.failed_conversations}
                    </div>
                    <div className="text-sm text-muted-foreground">Failed</div>
                  </div>
                </div>

                {/* Timing Info */}
                {processingProgress.timing.estimated_completion && (
                  <div className="p-3 glass rounded-lg">
                    <div className="flex items-center space-x-2 text-sm">
                      <Clock className="w-4 h-4 text-purple-400" />
                      <span>Estimated completion: {new Date(processingProgress.timing.estimated_completion).toLocaleTimeString()}</span>
                      {processingProgress.timing.elapsed_seconds && (
                        <span className="text-muted-foreground">
                          • Elapsed: {Math.round(processingProgress.timing.elapsed_seconds / 60)}m
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-8 h-8 animate-spin text-purple-400 mr-3" />
                <span>Initializing archive processing...</span>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Log Display Section */}
      <AnimatePresence>
        {(processingStatus === 'processing' || processingStatus === 'failed' || showLogs) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                <FileText className="mr-2" size={20} />
                Import Logs
              </h3>
              <button
                onClick={() => setShowLogs(!showLogs)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                {showLogs ? 'Hide Logs' : 'Show Logs'}
              </button>
            </div>
            
            {showLogs && (
              <div className="bg-black rounded-lg p-4 max-h-96 overflow-y-auto">
                <div className="font-mono text-sm">
                  {importLogs.length === 0 ? (
                    <div className="text-gray-500">No logs available</div>
                  ) : (
                    importLogs.map((logLine, index) => (
                      <div 
                        key={index} 
                        className={`mb-1 ${
                          logLine.includes('ERROR') ? 'text-red-400' :
                          logLine.includes('WARNING') ? 'text-yellow-400' :
                          logLine.includes('INFO') ? 'text-green-400' :
                          'text-gray-300'
                        }`}
                      >
                        {logLine}
                      </div>
                    ))
                  )}
                </div>
                
                {processingStatus === 'processing' && (
                  <div className="mt-4 text-center">
                    <div className="inline-flex items-center text-blue-400">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400 mr-2"></div>
                      Live updating...
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* File Selection Dialog */}
      <AnimatePresence>
        {showFileDialog && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                setShowFileDialog(false);
                setSelectedFiles([]);
                setArchiveAnalysis(null);
              }
            }}
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="glass rounded-2xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-2">
                  <FileArchive className="w-6 h-6 text-purple-400" />
                  <h3 className="text-xl font-semibold">Select Archive to Import</h3>
                </div>
                <button
                  onClick={() => {
                    setShowFileDialog(false);
                    setSelectedFiles([]);
                    setArchiveAnalysis(null);
                  }}
                  className="text-muted-foreground hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-6">
                {/* File Input Options */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Folder Upload */}
                  <div className="p-4 glass rounded-lg">
                    <div className="flex items-center space-x-2 mb-3">
                      <Folder className="w-5 h-5 text-blue-400" />
                      <h4 className="font-medium">Archive Folder</h4>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      Select a folder containing conversation.json files and media
                    </p>
                    <label className="block">
                      <input
                        type="file"
                        webkitdirectory="true"
                        multiple
                        onChange={(e) => handleFilesSelected(e.target.files)}
                        className="hidden"
                      />
                      <div className="border-2 border-dashed border-white/20 rounded-lg p-6 text-center hover:border-purple-400 transition-colors cursor-pointer">
                        <Folder className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                        <span className="text-sm">Click to select folder</span>
                      </div>
                    </label>
                  </div>

                  {/* Zip Upload */}
                  <div className="p-4 glass rounded-lg">
                    <div className="flex items-center space-x-2 mb-3">
                      <FileArchive className="w-5 h-5 text-green-400" />
                      <h4 className="font-medium">ZIP Archive</h4>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      Upload a ZIP file containing your archive
                    </p>
                    <label className="block">
                      <input
                        type="file"
                        accept=".zip,.tar,.tar.gz,.7z"
                        onChange={(e) => handleFilesSelected(e.target.files)}
                        className="hidden"
                      />
                      <div className="border-2 border-dashed border-white/20 rounded-lg p-6 text-center hover:border-green-400 transition-colors cursor-pointer">
                        <FileArchive className="w-8 h-8 text-green-400 mx-auto mb-2" />
                        <span className="text-sm">Click to select ZIP file</span>
                      </div>
                    </label>
                  </div>
                </div>

                {/* File Analysis */}
                {archiveAnalysis && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 glass rounded-lg"
                  >
                    <div className="flex items-center space-x-2 mb-4">
                      <BarChart3 className="w-5 h-5 text-purple-400" />
                      <h4 className="font-medium">Archive Analysis</h4>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400">
                          {archiveAnalysis.estimated_conversations}
                        </div>
                        <div className="text-sm text-muted-foreground">Conversations</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">
                          {archiveAnalysis.media_files}
                        </div>
                        <div className="text-sm text-muted-foreground">Media Files</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-400">
                          {archiveAnalysis.total_files}
                        </div>
                        <div className="text-sm text-muted-foreground">Total Files</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-400">
                          {archiveAnalysis.size_mb.toFixed(1)}MB
                        </div>
                        <div className="text-sm text-muted-foreground">Total Size</div>
                      </div>
                    </div>

                    {/* File Types Breakdown */}
                    <div className="mb-4">
                      <h5 className="text-sm font-medium mb-2">File Types:</h5>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(archiveAnalysis.file_types).map(([ext, count]) => (
                          <span
                            key={ext}
                            className="px-2 py-1 bg-white/10 rounded text-xs flex items-center space-x-1"
                          >
                            {['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext) && <Image className="w-3 h-3" />}
                            {['mp3', 'wav', 'ogg'].includes(ext) && <Music className="w-3 h-3" />}
                            {['mp4', 'avi', 'mov'].includes(ext) && <Video className="w-3 h-3" />}
                            {!['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp3', 'wav', 'ogg', 'mp4', 'avi', 'mov'].includes(ext) && <File className="w-3 h-3" />}
                            <span>{ext}: {count}</span>
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Processing Estimate */}
                    <div className="p-3 bg-purple-600/20 rounded-lg">
                      <div className="flex items-center space-x-2 text-sm">
                        <Clock className="w-4 h-4 text-purple-400" />
                        <span>
                          Estimated processing time: ~{Math.ceil(archiveAnalysis.estimated_conversations * 2 / 60)} minutes
                        </span>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Action Buttons */}
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => {
                      setShowFileDialog(false);
                      setSelectedFiles([]);
                      setArchiveAnalysis(null);
                    }}
                    className="px-4 py-2 glass rounded-lg hover:bg-white/10 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => {
                      setShowFileDialog(false);
                      uploadAndProcessFiles();
                    }}
                    disabled={selectedFiles.length === 0}
                    className={cn(
                      "px-6 py-2 rounded-lg transition-colors",
                      selectedFiles.length > 0
                        ? "bg-green-600 hover:bg-green-700 text-white"
                        : "bg-gray-600 text-gray-300 cursor-not-allowed"
                    )}
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Import Archive
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Search Interface */}
      <AnimatePresence>
        {currentView === "search" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ delay: 0.1 }}
            className="glass rounded-2xl p-6"
          >
        <div className="flex items-center space-x-2 mb-4">
          <Search className="w-5 h-5 text-purple-400" />
          <h3 className="text-xl font-semibold">Archive Search</h3>
          <span className="px-2 py-1 bg-blue-600/20 text-blue-300 text-xs rounded-full">
            PostgreSQL + pgvector
          </span>
        </div>

        <div className="space-y-4">
          {/* Search Query */}
          <div className="flex space-x-2">
            <div className="flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && performSearch()}
                placeholder={searchType === "semantic" ? "Enter concepts or themes to find semantically similar content..." : "Search conversations, messages, and content..."}
                className="w-full px-4 py-3 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none"
              />
            </div>
            <button
              onClick={performSearch}
              disabled={isSearching || !searchQuery.trim()}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
            >
              {isSearching ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
            </button>
          </div>

          {/* Search Type and Options */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium">Search Type:</label>
                <div className="flex bg-black/20 rounded-lg p-1">
                  <button
                    onClick={() => setSearchType("text")}
                    className={cn(
                      "px-3 py-1 text-sm rounded transition-colors",
                      searchType === "text"
                        ? "bg-purple-600 text-white"
                        : "text-gray-300 hover:text-white"
                    )}
                  >
                    <FileText className="w-4 h-4 inline mr-1" />
                    Text Search
                  </button>
                  <button
                    onClick={() => setSearchType("semantic")}
                    disabled={!embeddingStats?.total_embeddings}
                    className={cn(
                      "px-3 py-1 text-sm rounded transition-colors",
                      searchType === "semantic"
                        ? "bg-purple-600 text-white"
                        : "text-gray-300 hover:text-white",
                      !embeddingStats?.total_embeddings && "opacity-50 cursor-not-allowed"
                    )}
                  >
                    <Brain className="w-4 h-4 inline mr-1" />
                    Semantic
                    {!embeddingStats?.total_embeddings && " (No embeddings)"}
                  </button>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium">Limit:</label>
                <select
                  value={searchLimit}
                  onChange={(e) => setSearchLimit(Number(e.target.value))}
                  className="px-2 py-1 bg-black/20 border border-white/10 rounded text-sm focus:border-purple-400 focus:outline-none"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>

            {/* Search metadata */}
            {chunkAnalysis && (
              <div className="text-sm text-gray-400">
                {chunkAnalysis.error ? (
                  <span className="text-red-400">Error: {chunkAnalysis.error}</span>
                ) : (
                  <span>
                    Found {chunkAnalysis.total_found} results in {chunkAnalysis.search_time_ms}ms
                    ({chunkAnalysis.search_type} search)
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Source Types */}
            <div>
              <label className="block text-sm font-medium mb-2">Source Types</label>
              <div className="space-y-2">
                {sourceTypes.map((type) => (
                  <label key={type.id} className="flex items-center space-x-2 text-sm">
                    <input
                      type="checkbox"
                      checked={selectedSourceTypes.includes(type.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedSourceTypes([...selectedSourceTypes, type.id]);
                        } else {
                          setSelectedSourceTypes(selectedSourceTypes.filter(t => t !== type.id));
                        }
                      }}
                      className="rounded border-gray-600 bg-gray-700 text-purple-500"
                    />
                    <span className={type.color}>{type.label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Author Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Author</label>
              <input
                type="text"
                value={selectedAuthor}
                onChange={(e) => setSelectedAuthor(e.target.value)}
                placeholder="Filter by author..."
                className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none"
              />
            </div>

            {/* Date Range */}
            <div>
              <label className="block text-sm font-medium mb-2">Date Range</label>
              <div className="space-y-2">
                <input
                  type="date"
                  value={dateRange.from}
                  onChange={(e) => setDateRange({...dateRange, from: e.target.value})}
                  className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
                />
                <input
                  type="date"
                  value={dateRange.to}
                  onChange={(e) => setDateRange({...dateRange, to: e.target.value})}
                  className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
                />
              </div>
            </div>
          </div>
          
          {/* Save Search Button */}
          {searchQuery && searchResults.length > 0 && (
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => setShowSaveSearchDialog(true)}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                <Archive className="w-4 h-4 inline mr-2" />
                Save Search
              </button>
            </div>
          )}
        </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Conversation Browser */}
      <AnimatePresence>
        {currentView === "browse" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <MessageSquare className="w-5 h-5 text-purple-400" />
                <h3 className="text-xl font-semibold">All Conversations</h3>
                {conversationsPagination.total && (
                  <span className="px-2 py-1 bg-purple-600/20 text-purple-300 text-sm rounded-full">
                    {conversationsPagination.total} total
                  </span>
                )}
              </div>
              <button
                onClick={() => loadConversations()}
                className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {conversations.map((conversation, index) => (
                <motion.div
                  key={conversation.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.03 }}
                  onClick={() => loadConversationMessages(conversation.id)}
                  className="p-4 glass rounded-lg hover:bg-white/5 cursor-pointer transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h4 className="font-medium line-clamp-1">{conversation.title}</h4>
                      <div className="flex items-center space-x-4 mt-1 text-sm text-gray-400">
                        <div className="flex items-center space-x-1">
                          <MessageSquare className="w-3 h-3" />
                          <span>{conversation.message_count} messages</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Hash className="w-3 h-3" />
                          <span>{conversation.total_word_count?.toLocaleString() || 0} words</span>
                        </div>
                        {conversation.has_media && (
                          <div className="flex items-center space-x-1">
                            <Image className="w-3 h-3" />
                            <span>Media</span>
                          </div>
                        )}
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{conversation.timestamp ? new Date(conversation.timestamp).toLocaleDateString() : "No date"}</span>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleMessageSelection(conversation.id);
                      }}
                      className={cn(
                        "p-2 rounded transition-colors",
                        selectedForTransformation.includes(conversation.id)
                          ? "bg-green-600 text-white"
                          : "glass hover:bg-white/10"
                      )}
                    >
                      {selectedForTransformation.includes(conversation.id) ? (
                        <Check className="w-4 h-4" />
                      ) : (
                        <Plus className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
            
            {/* Add Selected to Queue */}
            {selectedForTransformation.length > 0 && (
              <div className="mt-4 p-3 bg-green-600/20 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-green-300">
                    {selectedForTransformation.length} conversations selected
                  </span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => addToTransformationQueue(selectedForTransformation, "humanize")}
                      className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                    >
                      Add to Humanizer Queue
                    </button>
                    <button
                      onClick={() => setSelectedForTransformation([])}
                      className="px-3 py-1 glass hover:bg-white/10 text-sm rounded transition-colors"
                    >
                      Clear Selection
                    </button>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Search Results */}
      <AnimatePresence>
        {currentView === "search" && searchResults.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                {searchType === "semantic" ? (
                  <Brain className="w-5 h-5 text-purple-400" />
                ) : (
                  <FileText className="w-5 h-5 text-purple-400" />
                )}
                <h3 className="text-xl font-semibold">Search Results</h3>
                <span className="px-2 py-1 bg-purple-600/20 text-purple-300 text-sm rounded-full">
                  {searchResults.length} found
                </span>
                {chunkAnalysis && (
                  <span className="px-2 py-1 bg-blue-600/20 text-blue-300 text-sm rounded-full">
                    {chunkAnalysis.search_type} search
                  </span>
                )}
              </div>
              
              {chunkAnalysis && !chunkAnalysis.error && (
                <div className="text-sm text-gray-400">
                  Query: "{chunkAnalysis.query_used}" • {chunkAnalysis.search_time_ms}ms
                </div>
              )}
            </div>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              {searchResults.map((result, index) => (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => handleConversationSelect(result)}
                  className="p-4 glass rounded-lg hover:bg-white/5 cursor-pointer transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2 flex-1">
                      <div className={cn("w-2 h-2 rounded-full", 
                        result.source_type === "node_conversation" ? "bg-green-400" :
                        result.source_type === "twitter" ? "bg-blue-400" :
                        result.source_type === "email" ? "bg-yellow-400" : "bg-purple-400"
                      )} />
                      <div className="flex items-center space-x-2">
                        {result.content_type === "conversation" ? (
                          <MessageSquare className="w-4 h-4 text-green-400" />
                        ) : (
                          <FileText className="w-4 h-4 text-blue-400" />
                        )}
                        <span className="font-medium">{result.title || `${result.content_type} ${result.id}`}</span>
                      </div>
                      {result.semantic_score && (
                        <span className="px-2 py-1 bg-purple-600/20 text-purple-300 text-xs rounded-full">
                          {(result.semantic_score * 100).toFixed(1)}% match
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-3 text-sm text-gray-400">
                      <div className="flex items-center space-x-1">
                        <User className="w-3 h-3" />
                        <span>{result.author || "Unknown"}</span>
                      </div>
                      {result.word_count && (
                        <div className="flex items-center space-x-1">
                          <Hash className="w-3 h-3" />
                          <span>{result.word_count} words</span>
                        </div>
                      )}
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3" />
                        <span>{result.timestamp ? new Date(result.timestamp).toLocaleDateString() : "No date"}</span>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {result.body_text || result.content_preview}
                  </p>
                  
                  {result.content_quality_score && (
                    <div className="mt-2 flex items-center space-x-2">
                      <BarChart3 className="w-3 h-3 text-purple-400" />
                      <span className="text-xs text-muted-foreground">
                        Quality: {(result.content_quality_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Saved Searches View */}
      <AnimatePresence>
        {currentView === "saved" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Archive className="w-5 h-5 text-purple-400" />
                <h3 className="text-xl font-semibold">Saved Searches</h3>
                <span className="px-2 py-1 bg-purple-600/20 text-purple-300 text-sm rounded-full">
                  {savedSearches.length} saved
                </span>
              </div>
              <button
                onClick={loadSavedSearches}
                className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
            
            {savedSearches.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <Archive className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No saved searches yet</p>
                <p className="text-sm">Save searches from the Search tab to access them here</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {savedSearches.map((search, index) => (
                  <motion.div
                    key={search.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 glass rounded-lg hover:bg-white/5 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium">{search.name}</h4>
                        <p className="text-sm text-gray-400 mt-1">"{search.query}"</p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span className="flex items-center space-x-1">
                            <Search className="w-3 h-3" />
                            <span>{search.search_type} search</span>
                          </span>
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>Saved {new Date(search.created_at).toLocaleDateString()}</span>
                          </span>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            setSearchQuery(search.query);
                            setSearchType(search.search_type);
                            // Apply filters if any
                            const filters = search.filters || {};
                            if (filters.author) setSelectedAuthor(filters.author);
                            if (filters.date_from) setDateRange(prev => ({...prev, from: filters.date_from}));
                            if (filters.date_to) setDateRange(prev => ({...prev, to: filters.date_to}));
                            if (filters.source_types) setSelectedSourceTypes(filters.source_types);
                            setCurrentView("search");
                          }}
                          className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                        >
                          <Search className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => {
                            // TODO: Implement delete search
                            console.log("Delete search:", search.id);
                          }}
                          className="p-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Transformation Queue View */}
      <AnimatePresence>
        {currentView === "queue" && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-purple-400" />
                <h3 className="text-xl font-semibold">Transformation Queue</h3>
                <span className="px-2 py-1 bg-purple-600/20 text-purple-300 text-sm rounded-full">
                  {transformationQueue.filter(item => item.status === "pending").length} pending
                </span>
              </div>
              <button
                onClick={loadTransformationQueue}
                className="p-2 glass rounded-lg hover:bg-white/10 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
            
            {transformationQueue.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <Zap className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No items in transformation queue</p>
                <p className="text-sm">Add conversations from Browse or Search to process them</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {transformationQueue.map((item, index) => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 glass rounded-lg"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <div className={cn("w-2 h-2 rounded-full",
                            item.status === "pending" ? "bg-yellow-400" :
                            item.status === "processing" ? "bg-blue-400" :
                            item.status === "completed" ? "bg-green-400" : "bg-red-400"
                          )} />
                          <span className="font-medium capitalize">{item.transformation_type}</span>
                          <span className={cn("px-2 py-1 text-xs rounded-full",
                            item.status === "pending" ? "bg-yellow-600/20 text-yellow-300" :
                            item.status === "processing" ? "bg-blue-600/20 text-blue-300" :
                            item.status === "completed" ? "bg-green-600/20 text-green-300" : "bg-red-600/20 text-red-300"
                          )}>
                            {item.status}
                          </span>
                        </div>
                        <p className="text-sm text-gray-400">Content ID: {item.content_id}</p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>Added {new Date(item.created_at).toLocaleDateString()}</span>
                          </span>
                          <span className="flex items-center space-x-1">
                            <Tag className="w-3 h-3" />
                            <span>{item.priority} priority</span>
                          </span>
                        </div>
                        {item.error && (
                          <div className="mt-2 p-2 bg-red-600/20 rounded text-sm text-red-300">
                            Error: {item.error}
                          </div>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        {item.status === "pending" && (
                          <button
                            onClick={() => {
                              // TODO: Implement start processing
                              console.log("Start processing:", item.id);
                            }}
                            className="p-2 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                          >
                            <Zap className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => {
                            // TODO: Implement remove from queue
                            console.log("Remove from queue:", item.id);
                          }}
                          className="p-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Conversation Thread View */}
      <AnimatePresence>
        {selectedConversation && conversationThread.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <MessageSquare className="w-5 h-5 text-purple-400" />
                <h3 className="text-xl font-semibold">{selectedConversation.title}</h3>
              </div>
              <button
                onClick={() => {
                  setSelectedConversation(null);
                  setConversationThread([]);
                }}
                className="text-muted-foreground hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              {conversationThread.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    "p-4 rounded-lg",
                    message.author === "user" ? "bg-purple-600/20 ml-8" : "bg-blue-600/20 mr-8"
                  )}
                >
                  <div className="flex items-center space-x-2 mb-2">
                    <div className={cn("w-2 h-2 rounded-full",
                      message.author === "user" ? "bg-purple-400" : "bg-blue-400"
                    )} />
                    <span className="font-medium capitalize">{message.author}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm whitespace-pre-wrap">{message.body_text}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Full Message View Modal */}
      <AnimatePresence>
        {currentView === "conversation" && selectedConversationMessages.length > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => {
              setCurrentView("browse");
              setSelectedConversationMessages([]);
              setCurrentConversationId(null);
            }}
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="glass rounded-2xl p-6 max-w-4xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-2">
                  <MessageSquare className="w-6 h-6 text-purple-400" />
                  <h3 className="text-xl font-semibold">
                    Conversation Messages ({selectedConversationMessages.length})
                  </h3>
                </div>
                <button
                  onClick={() => {
                    setCurrentView("browse");
                    setSelectedConversationMessages([]);
                    setCurrentConversationId(null);
                  }}
                  className="text-muted-foreground hover:text-white transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                {selectedConversationMessages.map((message, index) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={cn(
                      "p-4 rounded-lg",
                      message.author === "user" ? "bg-purple-600/20 ml-8" : "bg-blue-600/20 mr-8"
                    )}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <div className={cn("w-3 h-3 rounded-full",
                          message.author === "user" ? "bg-purple-400" : "bg-blue-400"
                        )} />
                        <span className="font-medium capitalize">{message.role || message.author}</span>
                        <span className="text-xs text-muted-foreground">
                          {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : ""}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {message.word_count} words
                        </span>
                      </div>
                      <button
                        onClick={() => addToTransformationQueue([message.id], "humanize")}
                        className="px-2 py-1 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded transition-colors"
                      >
                        <Zap className="w-3 h-3 inline mr-1" />
                        Transform
                      </button>
                    </div>
                    <div className="text-sm whitespace-pre-wrap max-h-64 overflow-y-auto">
                      {message.body_text}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Save Search Dialog */}
      <AnimatePresence>
        {showSaveSearchDialog && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowSaveSearchDialog(false)}
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="glass rounded-2xl p-6 max-w-lg w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center space-x-2 mb-4">
                <Save className="w-5 h-5 text-green-400" />
                <h3 className="text-lg font-semibold">Save Search</h3>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Search Name</label>
                  <input
                    type="text"
                    placeholder="Enter a name for this search..."
                    className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none"
                    onKeyPress={(e) => {
                      if (e.key === "Enter" && e.target.value.trim()) {
                        saveCurrentSearch(e.target.value.trim());
                      }
                    }}
                  />
                </div>
                
                <div className="p-3 bg-purple-600/20 rounded-lg">
                  <div className="text-sm">
                    <div className="flex items-center space-x-2 mb-1">
                      <Search className="w-4 h-4" />
                      <span className="font-medium">Query:</span>
                      <span>"{searchQuery}"</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Brain className="w-4 h-4" />
                      <span className="font-medium">Type:</span>
                      <span>{searchType} search</span>
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowSaveSearchDialog(false)}
                    className="px-4 py-2 glass rounded-lg hover:bg-white/10 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={(e) => {
                      const input = e.target.closest('.glass').querySelector('input');
                      if (input.value.trim()) {
                        saveCurrentSearch(input.value.trim());
                      }
                    }}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                  >
                    <Save className="w-4 h-4 inline mr-2" />
                    Save Search
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ArchiveExplorer;