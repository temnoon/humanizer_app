import React, { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import MarkdownRenderer from "./components/MarkdownRenderer";
import "./styles/markdown.css";
import {
  MessageSquare,
  Search,
  RefreshCw,
  Copy,
  Zap,
  Check,
  User,
  Calendar,
  Hash,
  Image,
  ChevronRight,
  ChevronDown,
  X,
  Plus,
  Edit3,
  Trash2,
  Clock,
  Tag,
  Filter,
  Download,
  ArrowLeft,
  Settings,
  FileText,
  Layers,
  CheckSquare,
  Cpu,
  Play,
  GitBranch,
  BookOpen
} from "lucide-react";

const ConversationBrowser = ({ initialConversationId = null, initialMessageId = null, onNavigateToConversation = null, onNavigateToWritebook = null }) => {
  // Main state
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversationMessages, setConversationMessages] = useState([]);
  const [transformationQueue, setTransformationQueue] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentView, setCurrentView] = useState("browser"); // "browser", "conversation", "queue"
  
  // Filtering and sorting state
  const [sortBy, setSortBy] = useState("timestamp");
  const [sortOrder, setSortOrder] = useState("desc");
  const [filters, setFilters] = useState({
    minWords: "",
    maxWords: "",
    minMessages: "",
    maxMessages: "",
    dateFrom: "",
    dateTo: "",
    author: ""
  });
  const [showFilters, setShowFilters] = useState(false);
  
  // Embeddings state
  const [isGeneratingEmbeddings, setIsGeneratingEmbeddings] = useState(false);
  const [embeddingsProgress, setEmbeddingsProgress] = useState(null);
  const [embeddingsStats, setEmbeddingsStats] = useState(null);
  
  // Chunking state
  const [isGeneratingChunks, setIsGeneratingChunks] = useState(false);
  const [chunkingProgress, setChunkingProgress] = useState(null);
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [pagination, setPagination] = useState({ page: 1, limit: 20, total: 0 });
  const [selectedMessages, setSelectedMessages] = useState([]);
  const [expandedMessages, setExpandedMessages] = useState(new Set());
  const [highlightedMessageId, setHighlightedMessageId] = useState(null);
  const [showQueueDialog, setShowQueueDialog] = useState(false);
  const [queueSettings, setQueueSettings] = useState({
    transformationType: "humanize",
    priority: "normal",
    description: ""
  });

  // API base
  const ARCHIVE_API_BASE = "http://localhost:7200";
  const LIGHTHOUSE_API_BASE = "http://localhost:8100/api";

  // Load conversations on mount and when pagination changes
  useEffect(() => {
    loadConversations(searchQuery);
  }, [pagination.page]);
  
  // Search state for manual control
  const [searchInput, setSearchInput] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  
  // Manual search function
  const handleSearch = () => {
    setSearchQuery(searchInput);
    setPagination(prev => ({ ...prev, page: 1 }));
    setIsSearching(true);
    loadConversations(searchInput).finally(() => setIsSearching(false));
  };
  
  // Handle search input key events
  const handleSearchKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearch();
    }
    // Don't trigger search on spacebar
    if (e.key === ' ') {
      e.stopPropagation();
    }
  };

  // Reload when sorting changes
  useEffect(() => {
    setPagination(prev => ({ ...prev, page: 1 }));
    loadConversations(searchQuery);
  }, [sortBy, sortOrder]);

  // Reload when filters change (with debouncing)
  useEffect(() => {
    const filterTimer = setTimeout(() => {
      setPagination(prev => ({ ...prev, page: 1 }));
      loadConversations(searchQuery);
    }, 800); // 800ms debounce for filters
    
    return () => clearTimeout(filterTimer);
  }, [filters]);

  // Load transformation queue on mount
  useEffect(() => {
    loadTransformationQueue();
    loadEmbeddingsStats();
  }, []);

  // Handle initial conversation loading from props or URL
  useEffect(() => {
    if (initialConversationId) {
      // Find conversation from ID and load it
      const findAndLoadConversation = async () => {
        try {
          // Try lighthouse API first (imported conversations)
          let response = await fetch(`${LIGHTHOUSE_API_BASE}/conversations/${initialConversationId}/messages?limit=1000`);
          let data = null;
          
          if (response.ok) {
            data = await response.json();
          } else {
            // Try archive API (existing conversations)
            response = await fetch(`${ARCHIVE_API_BASE}/conversations/${initialConversationId}/messages?limit=1000`);
            if (response.ok) {
              data = await response.json();
            }
          }
          
          if (data && data.conversation) {
            setSelectedConversation(data.conversation);
            setConversationMessages(data.messages || []);
            setCurrentView("conversation");
            
            // If there's an initial message ID, scroll to it and highlight it
            if (initialMessageId) {
              setTimeout(() => {
                scrollToAndHighlightMessage(initialMessageId, 'start');
              }, 500);
            }
          }
        } catch (error) {
          console.error("Failed to load initial conversation:", error);
        }
      };
      findAndLoadConversation();
    }
  }, [initialConversationId, initialMessageId]);

  const loadConversations = async (searchTerm = "") => {
    setIsLoading(true);
    try {
      let allConversations = [];
      
      // Query both archive API and lighthouse API
      const promises = [];
      
      // 1. Query archive API (existing conversations)
      const archiveParams = new URLSearchParams({
        page: pagination.page.toString(),
        limit: pagination.limit.toString(),
        sort_by: sortBy,
        order: sortOrder
      });
      
      if (searchTerm.trim()) {
        archiveParams.append("search", searchTerm.trim());
      }
      
      // Add filters for archive API
      if (filters.minWords) archiveParams.append("min_words", filters.minWords);
      if (filters.maxWords) archiveParams.append("max_words", filters.maxWords);
      if (filters.minMessages) archiveParams.append("min_messages", filters.minMessages);
      if (filters.maxMessages) archiveParams.append("max_messages", filters.maxMessages);
      if (filters.dateFrom) archiveParams.append("date_from", filters.dateFrom);
      if (filters.dateTo) archiveParams.append("date_to", filters.dateTo);
      if (filters.author) archiveParams.append("author", filters.author);
      
      promises.push(
        fetch(`${ARCHIVE_API_BASE}/conversations?${archiveParams}`)
          .then(res => res.ok ? res.json() : { conversations: [] })
          .catch(() => ({ conversations: [] }))
      );
      
      // 2. Query lighthouse API (imported conversations)
      const lighthouseParams = new URLSearchParams({
        page: 1,  // Get all from lighthouse for now
        limit: 100,
        sort_by: sortBy,
        order: sortOrder
      });
      
      if (searchTerm.trim()) {
        lighthouseParams.append("search", searchTerm.trim());
      }
      
      promises.push(
        fetch(`${LIGHTHOUSE_API_BASE}/conversations?${lighthouseParams}`)
          .then(res => res.ok ? res.json() : { conversations: [] })
          .catch(() => ({ conversations: [] }))
      );
      
      // Wait for both APIs
      const [archiveData, lighthouseData] = await Promise.all(promises);
      
      // Combine results and mark sources
      const archiveConversations = (archiveData.conversations || []).map(conv => ({
        ...conv,
        _source: 'archive'
      }));
      
      const lighthouseConversations = (lighthouseData.conversations || []).map(conv => ({
        ...conv,
        _source: 'lighthouse'
      }));
      
      allConversations = [...archiveConversations, ...lighthouseConversations];
      
      // Apply client-side filtering and sorting since we're combining sources
      if (filters.minMessages) {
        allConversations = allConversations.filter(c => (c.messages || c.message_count || 0) >= filters.minMessages);
      }
      if (filters.maxMessages) {
        allConversations = allConversations.filter(c => (c.messages || c.message_count || 0) <= filters.maxMessages);
      }
      
      // Sort combined results
      if (sortBy === "timestamp") {
        allConversations.sort((a, b) => {
          const aTime = a.imported || a.timestamp || '';
          const bTime = b.imported || b.timestamp || '';
          return sortOrder === 'desc' ? bTime.localeCompare(aTime) : aTime.localeCompare(bTime);
        });
      } else if (sortBy === "title") {
        allConversations.sort((a, b) => {
          const aTitle = a.title || '';
          const bTitle = b.title || '';
          return sortOrder === 'desc' ? bTitle.localeCompare(aTitle) : aTitle.localeCompare(bTitle);
        });
      }
      
      setConversations(allConversations);
      setPagination(prev => ({ ...prev, total: allConversations.length }));
      
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadConversationMessages = async (conversationId) => {
    setIsLoading(true);
    try {
      // Try lighthouse API first (imported conversations)
      let response = await fetch(`${LIGHTHOUSE_API_BASE}/conversations/${conversationId}/messages?limit=1000`);
      let data = null;
      
      if (response.ok) {
        data = await response.json();
      } else {
        // Try archive API (existing conversations)
        response = await fetch(`${ARCHIVE_API_BASE}/conversations/${conversationId}/messages?limit=1000`);
        if (response.ok) {
          data = await response.json();
        }
      }
      
      if (data) {
        setConversationMessages(data.messages || []);
        setCurrentView("conversation");
      }
    } catch (error) {
      console.error("Failed to load conversation messages:", error);
    } finally {
      setIsLoading(false);
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

  const loadEmbeddingsStats = async () => {
    try {
      const response = await fetch(`${ARCHIVE_API_BASE}/embeddings/statistics`);
      if (response.ok) {
        const data = await response.json();
        setEmbeddingsStats(data);
      }
    } catch (error) {
      console.error("Failed to load embeddings statistics:", error);
    }
  };

  const generateEmbeddings = async (conversationIds = null, batchSize = 10, maxConversations = null) => {
    setIsGeneratingEmbeddings(true);
    setEmbeddingsProgress({ processed: 0, total: 0, currentBatch: 0 });
    
    try {
      const requestBody = {
        batch_size: batchSize
      };
      
      if (conversationIds && conversationIds.length > 0) {
        requestBody.conversation_ids = conversationIds;
      }
      
      if (maxConversations) {
        requestBody.max_conversations = maxConversations;
      }

      const response = await fetch(`${ARCHIVE_API_BASE}/generate-embeddings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Embeddings generation completed:", data);
        
        // Refresh embeddings stats
        await loadEmbeddingsStats();
        
        // Show success message
        setEmbeddingsProgress({
          ...data,
          completed: true,
          message: `Successfully generated embeddings for ${data.total_processed} messages in ${data.conversations_processed} conversations`
        });
      } else {
        const errorData = await response.json();
        console.error("Failed to generate embeddings:", errorData);
        setEmbeddingsProgress({
          error: true,
          message: errorData.detail || "Failed to generate embeddings"
        });
      }
    } catch (error) {
      console.error("Error generating embeddings:", error);
      setEmbeddingsProgress({
        error: true,
        message: "Network error while generating embeddings"
      });
    } finally {
      setIsGeneratingEmbeddings(false);
      
      // Clear progress after 5 seconds
      setTimeout(() => {
        setEmbeddingsProgress(null);
      }, 5000);
    }
  };

  const generateChunks = async (contentIds = null, maxContent = 10) => {
    setIsGeneratingChunks(true);
    setChunkingProgress({ processed: 0, total: 0 });
    
    try {
      const requestBody = {
        max_content: maxContent,
        include_summaries: true
      };
      
      if (contentIds && contentIds.length > 0) {
        requestBody.content_ids = contentIds;
      }

      const response = await fetch(`${ARCHIVE_API_BASE}/generate-hierarchical-chunks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Hierarchical chunking completed:", data);
        
        // Show success message
        setChunkingProgress({
          ...data,
          completed: true,
          message: `Successfully generated hierarchical chunks for ${data.processed} content items`
        });
      } else {
        const errorData = await response.json();
        console.error("Failed to generate chunks:", errorData);
        setChunkingProgress({
          error: true,
          message: errorData.detail || "Failed to generate hierarchical chunks"
        });
      }
    } catch (error) {
      console.error("Error generating chunks:", error);
      setChunkingProgress({
        error: true,
        message: "Network error while generating chunks"
      });
    } finally {
      setIsGeneratingChunks(false);
      
      // Clear progress after 5 seconds
      setTimeout(() => {
        setChunkingProgress(null);
      }, 5000);
    }
  };

  const addToQueue = async (contentIds, transformationType = "humanize", priority = "normal", description = "") => {
    try {
      const response = await fetch(`${ARCHIVE_API_BASE}/transformation-queue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content_ids: contentIds,
          transformation_type: transformationType,
          priority: priority,
          description: description
        })
      });
      if (response.ok) {
        loadTransformationQueue();
        setSelectedMessages([]);
        setShowQueueDialog(false);
      }
    } catch (error) {
      console.error("Failed to add to queue:", error);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      // Show brief success feedback
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  const exportToWritebook = () => {
    if (!selectedConversation || conversationMessages.length === 0) return;

    // Convert conversation messages to writebook pages
    const pages = conversationMessages.map((message, index) => ({
      id: message.id || `msg_${index}`,
      type: 'page',
      content: message.body_text || '',
      author: message.role || message.author || 'Unknown',
      timestamp: message.timestamp,
      original_message_id: message.id
    }));

    // Create writebook export data with unique ID
    const writebookId = `writebook_${selectedConversation.id}_${Date.now()}`;
    const writebookData = {
      id: writebookId,
      title: selectedConversation.title || 'Exported Conversation',
      pages: pages,
      metadata: {
        conversation_id: selectedConversation.id,
        participant_count: new Set(conversationMessages.map(msg => msg.role || msg.author)).size,
        date_range: [
          conversationMessages[0]?.timestamp || '',
          conversationMessages[conversationMessages.length - 1]?.timestamp || ''
        ],
        total_messages: conversationMessages.length,
        total_words: conversationMessages.reduce((sum, msg) => sum + (msg.word_count || 0), 0),
        exported_at: new Date().toISOString(),
        created_at: new Date().toISOString()
      }
    };

    // Store the export data temporarily
    localStorage.setItem('writebookExportData', JSON.stringify(writebookData));
    
    // Navigate to the writebook editor
    if (onNavigateToWritebook) {
      onNavigateToWritebook();
    } else {
      // Fallback - try direct navigation
      console.warn('No navigation callback provided for writebook export');
    }
  };

  const toggleMessageSelection = (messageId) => {
    setSelectedMessages(prev => 
      prev.includes(messageId) 
        ? prev.filter(id => id !== messageId)
        : [...prev, messageId]
    );
  };

  const toggleMessageExpansion = (messageId) => {
    setExpandedMessages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
  };

  // Handle clicking on a message to navigate to its conversation
  const handleMessageClick = (message, event) => {
    // Check if ctrl/cmd key is pressed for new tab
    if (event.ctrlKey || event.metaKey) {
      // Open in new tab by creating a URL
      const conversationUrl = `${window.location.origin}${window.location.pathname}?conversation=${message.conversation_id}&message=${message.id}`;
      window.open(conversationUrl, '_blank');
    } else {
      // Navigate within the same tab
      if (onNavigateToConversation) {
        onNavigateToConversation(message.conversation_id, message.id);
      } else {
        // Fallback: just load the conversation in current view
        setSelectedConversation({ id: message.conversation_id });
        loadConversationMessages(message.conversation_id);
        setCurrentView("conversation");
      }
    }
  };

  // Enhanced function to scroll to and highlight a specific message
  const scrollToAndHighlightMessage = (messageId, scrollPosition = 'center') => {
    const messageElement = document.getElementById(`message-${messageId}`);
    if (messageElement) {
      // Set the highlighted message state
      setHighlightedMessageId(messageId);
      
      // Scroll to message with proper positioning
      messageElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: scrollPosition, // 'center', 'start', 'end', 'nearest'
        inline: 'nearest'
      });
      
      // Focus on the message content to enable cursor placement
      const messageContent = messageElement.querySelector('.message-content');
      if (messageContent) {
        // Make content focusable and focus it
        messageContent.setAttribute('tabindex', '0');
        setTimeout(() => {
          messageContent.focus();
          
          // Try to select all text content if it exists
          const range = document.createRange();
          const selection = window.getSelection();
          
          try {
            range.selectNodeContents(messageContent);
            selection.removeAllRanges();
            selection.addRange(range);
          } catch (e) {
            // Fallback: just focus without selection
            console.log('Text selection not available');
          }
        }, 300);
      }
      
      // Remove highlighting after 5 seconds
      setTimeout(() => {
        setHighlightedMessageId(null);
      }, 5000);
    }
  };

  // No longer need client-side filtering since we're doing server-side search
  const filteredConversations = conversations;

  const renderConversationList = () => (
    <div className="space-y-4">
      {/* Search Box - Full Width Above Controls */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            placeholder={`Search conversations... (${pagination.total || 1923} total) - Press Enter to search`}
            className="w-full pl-12 pr-24 py-4 text-lg bg-black/20 border border-white/10 rounded-xl focus:border-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-400/20 transition-all"
          />
          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            {isSearching ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Search
          </button>
        </div>
        {searchQuery && (
          <div className="mt-2 flex items-center justify-between text-sm text-gray-400">
            <span>Searching for: "{searchQuery}"</span>
            <button
              onClick={() => {
                setSearchQuery("");
                setSearchInput("");
                loadConversations("");
              }}
              className="text-purple-400 hover:text-purple-300 flex items-center gap-1"
            >
              <X className="w-3 h-3" />
              Clear
            </button>
          </div>
        )}
      </div>
      
      {/* Controls Row */}
      <div className="flex items-center justify-between mb-6">
        {/* Left: Sort Controls */}
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-400">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none"
          >
            <option value="timestamp">Date Created</option>
            <option value="title">Title</option>
            <option value="word_count">Word Count</option>
            <option value="message_count">Message Count</option>
          </select>
          
          <button
            onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
            className="p-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition-colors"
            title={`Sort ${sortOrder === "asc" ? "Descending" : "Ascending"}`}
          >
            {sortOrder === "asc" ? <ChevronDown className="w-4 h-4" /> : <ChevronDown className="w-4 h-4 transform rotate-180" />}
          </button>
        </div>
        
        {/* Right: Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sm ${showFilters ? 'bg-purple-600 text-white' : 'bg-gray-600 hover:bg-gray-700 text-white'}`}
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
          
          <button
            onClick={() => loadConversations(searchQuery)}
            className="flex items-center gap-2 px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors text-white text-sm"
            title="Refresh conversations"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          
          <button
            onClick={() => generateEmbeddings(null, 10, 100)}
            disabled={isGeneratingEmbeddings}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
            isGeneratingEmbeddings 
              ? 'bg-gray-600 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
          title="Generate embeddings for conversations"
        >
          {isGeneratingEmbeddings ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Cpu className="w-4 h-4" />
          )}
          <span>
            {isGeneratingEmbeddings ? 'Generating...' : 'Embeddings'}
            {embeddingsStats && ` (${embeddingsStats.total_embeddings || 0})`}
          </span>
        </button>
        
        <button
          onClick={() => generateChunks(null, 10)}
          disabled={isGeneratingChunks}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
            isGeneratingChunks 
              ? 'bg-gray-600 cursor-not-allowed' 
              : 'bg-orange-600 hover:bg-orange-700'
          }`}
          title="Generate hierarchical chunks and summaries"
        >
          {isGeneratingChunks ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <GitBranch className="w-4 h-4" />
          )}
          <span>
            {isGeneratingChunks ? 'Chunking...' : 'Summaries'}
          </span>
        </button>
        
          <button
            onClick={() => setCurrentView("queue")}
            className="flex items-center space-x-2 px-3 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors text-white text-sm"
          >
            <Zap className="w-4 h-4" />
            <span>Queue ({transformationQueue.filter(item => item.status === "pending").length})</span>
          </button>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="mb-6 p-4 bg-white/5 rounded-lg border border-white/10">
          <h4 className="text-sm font-medium mb-3 flex items-center">
            <Filter className="w-4 h-4 mr-2" />
            Advanced Filters
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Min Words</label>
              <input
                type="number"
                value={filters.minWords}
                onChange={(e) => setFilters(prev => ({ ...prev, minWords: e.target.value }))}
                placeholder="0"
                className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Max Words</label>
              <input
                type="number"
                value={filters.maxWords}
                onChange={(e) => setFilters(prev => ({ ...prev, maxWords: e.target.value }))}
                placeholder="∞"
                className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Min Messages</label>
              <input
                type="number"
                value={filters.minMessages}
                onChange={(e) => setFilters(prev => ({ ...prev, minMessages: e.target.value }))}
                placeholder="0"
                className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Max Messages</label>
              <input
                type="number"
                value={filters.maxMessages}
                onChange={(e) => setFilters(prev => ({ ...prev, maxMessages: e.target.value }))}
                placeholder="∞"
                className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Date From</label>
              <input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters(prev => ({ ...prev, dateFrom: e.target.value }))}
                className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Date To</label>
              <input
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters(prev => ({ ...prev, dateTo: e.target.value }))}
                className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-1">Author</label>
              <input
                type="text"
                value={filters.author}
                onChange={(e) => setFilters(prev => ({ ...prev, author: e.target.value }))}
                placeholder="Filter by author..."
                className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none text-sm"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({
                  minWords: "",
                  maxWords: "",
                  minMessages: "",
                  maxMessages: "",
                  dateFrom: "",
                  dateTo: "",
                  author: ""
                })}
                className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Embeddings Progress Panel */}
      {embeddingsProgress && (
        <div className={`mb-6 p-4 rounded-lg border ${
          embeddingsProgress.error 
            ? 'bg-red-900/20 border-red-500/30 text-red-200' 
            : embeddingsProgress.completed 
              ? 'bg-green-900/20 border-green-500/30 text-green-200'
              : 'bg-blue-900/20 border-blue-500/30 text-blue-200'
        }`}>
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium flex items-center">
              <Cpu className="w-4 h-4 mr-2" />
              Embeddings Generation
            </h4>
            {!embeddingsProgress.error && !embeddingsProgress.completed && (
              <button
                onClick={() => setEmbeddingsProgress(null)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          
          {embeddingsProgress.message && (
            <p className="text-sm mt-2">{embeddingsProgress.message}</p>
          )}
          
          {embeddingsProgress.total_processed !== undefined && (
            <div className="mt-3">
              <div className="text-xs mb-1">
                Progress: {embeddingsProgress.total_processed || 0} messages processed
                {embeddingsProgress.conversations_processed && 
                  ` in ${embeddingsProgress.conversations_processed} conversations`
                }
              </div>
              {embeddingsProgress.processing_time && (
                <div className="text-xs text-gray-400">
                  Processing time: {embeddingsProgress.processing_time}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Chunking Progress Panel */}
      {chunkingProgress && (
        <div className={`mb-6 p-4 rounded-lg border ${
          chunkingProgress.error 
            ? 'bg-red-900/20 border-red-500/30 text-red-200' 
            : chunkingProgress.completed 
              ? 'bg-green-900/20 border-green-500/30 text-green-200'
              : 'bg-orange-900/20 border-orange-500/30 text-orange-200'
        }`}>
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium flex items-center">
              <GitBranch className="w-4 h-4 mr-2" />
              Hierarchical Chunking
            </h4>
            {!chunkingProgress.error && !chunkingProgress.completed && (
              <button
                onClick={() => setChunkingProgress(null)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          
          {chunkingProgress.message && (
            <p className="text-sm mt-2">{chunkingProgress.message}</p>
          )}
          
          {chunkingProgress.processed !== undefined && (
            <div className="mt-3">
              <div className="text-xs mb-1">
                Progress: {chunkingProgress.processed || 0} content items processed
                {chunkingProgress.failed > 0 && ` (${chunkingProgress.failed} failed)`}
              </div>
              {chunkingProgress.processing_time && (
                <div className="text-xs text-gray-400">
                  Processing time: {chunkingProgress.processing_time}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Conversation List */}
      <div className="space-y-3">
        {filteredConversations.map((conversation, index) => (
          <motion.div
            key={conversation.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => {
              setSelectedConversation(conversation);
              loadConversationMessages(conversation.id);
            }}
            className="p-4 bg-white/5 hover:bg-white/10 rounded-lg cursor-pointer transition-colors border border-white/10"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-medium text-white line-clamp-2 mb-2">{conversation.title}</h3>
                <div className="flex items-center space-x-4 text-sm text-gray-400">
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
              <ChevronRight className="w-5 h-5 text-gray-400" />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Pagination */}
      {pagination.total > pagination.limit && (
        <div className="flex items-center justify-between mt-6">
          <button
            onClick={() => setPagination(prev => ({ ...prev, page: Math.max(1, prev.page - 1) }))}
            disabled={pagination.page === 1}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
          >
            Previous
          </button>
          <span className="text-sm text-gray-400">
            Page {pagination.page} of {Math.ceil(pagination.total / pagination.limit)}
          </span>
          <button
            onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
            disabled={pagination.page >= Math.ceil(pagination.total / pagination.limit)}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );

  const renderConversationView = () => (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setCurrentView("browser")}
            className="p-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h2 className="text-xl font-semibold text-white">{selectedConversation?.title}</h2>
            <div className="flex items-center space-x-4 text-sm text-gray-400 mt-1">
              <span>{conversationMessages.length} messages</span>
              <span>{conversationMessages.reduce((sum, msg) => sum + (msg.word_count || 0), 0).toLocaleString()} words</span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {selectedMessages.length > 0 && (
            <button
              onClick={() => setShowQueueDialog(true)}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
            >
              <Zap className="w-4 h-4 inline mr-2" />
              Queue {selectedMessages.length} message{selectedMessages.length !== 1 ? 's' : ''}
            </button>
          )}
          <button
            onClick={() => {
              const allText = conversationMessages.map(msg => 
                `[${msg.role || msg.author}]: ${msg.body_text}`
              ).join('\n\n');
              copyToClipboard(allText);
            }}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            <Copy className="w-4 h-4 inline mr-2" />
            Copy All
          </button>
          <button
            onClick={exportToWritebook}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
          >
            <BookOpen className="w-4 h-4 inline mr-2" />
            Export to Writebook
          </button>
        </div>
      </div>

      {/* Narrative Consolidation Tools */}
      {selectedMessages.length > 1 && (
        <div className="mb-4 p-4 bg-purple-600/20 border border-purple-400/30 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Layers className="w-5 h-5 text-purple-400" />
              <div>
                <h4 className="font-medium text-white">Narrative Consolidation</h4>
                <p className="text-sm text-gray-300">
                  {selectedMessages.length} messages selected • Combine into single narrative for processing
                </p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  const selectedMessageTexts = conversationMessages
                    .filter(msg => selectedMessages.includes(msg.id))
                    .map(msg => `[${msg.role || msg.author}]: ${msg.body_text}`)
                    .join('\n\n');
                  copyToClipboard(selectedMessageTexts);
                }}
                className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                <Copy className="w-4 h-4 inline mr-2" />
                Copy Combined
              </button>
              <button
                onClick={() => {
                  setQueueSettings(prev => ({
                    ...prev,
                    description: `Consolidated narrative from ${selectedMessages.length} messages`
                  }));
                  setShowQueueDialog(true);
                }}
                className="px-3 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
              >
                <Zap className="w-4 h-4 inline mr-2" />
                Queue Narrative
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="space-y-4">
        {conversationMessages.map((message, index) => {
          const isExpanded = expandedMessages.has(message.id);
          const isSelected = selectedMessages.includes(message.id);
          const isHighlighted = highlightedMessageId === message.id;
          const messageText = message.body_text || "";
          const previewText = messageText.length > 300 ? messageText.substring(0, 300) + "..." : messageText;
          
          return (
            <motion.div
              key={message.id}
              id={`message-${message.id}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.02 }}
              className={`p-4 rounded-lg border transition-all duration-500 ${
                isHighlighted
                  ? "bg-yellow-500/30 border-yellow-400 shadow-xl ring-2 ring-yellow-400/50"
                  : isSelected 
                    ? "bg-green-600/20 border-green-400 shadow-lg" 
                    : message.author === "user" 
                      ? "bg-purple-600/20 border-purple-400/30 hover:bg-purple-600/30" 
                      : "bg-blue-600/20 border-blue-400/30 hover:bg-blue-600/30"
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => toggleMessageSelection(message.id)}
                    className={`p-2 rounded transition-colors ${
                      isSelected ? "bg-green-600 text-white" : "bg-gray-600 hover:bg-gray-700"
                    }`}
                    title={isSelected ? "Remove from selection" : "Add to selection"}
                  >
                    {isSelected ? <CheckSquare className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                  </button>
                  <div className={`w-3 h-3 rounded-full ${
                    message.author === "user" ? "bg-purple-400" : "bg-blue-400"
                  }`} />
                  <span className="font-medium capitalize text-white">
                    {message.role || message.author}
                  </span>
                  <span className="text-xs text-gray-400">
                    {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : ""}
                  </span>
                  <span className="text-xs text-gray-400">
                    {message.word_count} words
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => copyToClipboard(messageText)}
                    className="p-2 bg-gray-600 hover:bg-gray-700 rounded transition-colors"
                    title="Copy message text"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => addToQueue([message.id])}
                    className="p-2 bg-green-600 hover:bg-green-700 rounded transition-colors"
                    title="Add to transformation queue"
                  >
                    <Zap className="w-4 h-4" />
                  </button>
                  {messageText.length > 300 && (
                    <button
                      onClick={() => toggleMessageExpansion(message.id)}
                      className="p-2 bg-gray-600 hover:bg-gray-700 rounded transition-colors"
                      title={isExpanded ? "Show less" : "Show full message"}
                    >
                      {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                    </button>
                  )}
                </div>
              </div>
              
              <div 
                onClick={(e) => handleMessageClick(message, e)}
                className="cursor-pointer hover:bg-white/5 rounded p-2 -m-2 transition-colors group"
                title="Click to open conversation (Ctrl/Cmd+Click for new tab)"
              >
                <div className="message-content">
                  <MarkdownRenderer 
                    content={isExpanded ? messageText : previewText}
                    className="text-sm text-gray-100 leading-relaxed group-hover:text-white transition-colors"
                    enableTables={true}
                    enableCodeHighlighting={true}
                  />
                </div>
                <div className="opacity-0 group-hover:opacity-100 transition-opacity text-xs text-gray-400 mt-2">
                  💡 Click to open conversation • Ctrl/Cmd+Click for new tab
                </div>
              </div>
              
              {isSelected && (
                <div className="mt-3 pt-3 border-t border-green-400/20">
                  <div className="flex items-center space-x-2 text-xs text-green-300">
                    <Check className="w-3 h-3" />
                    <span>Selected for narrative consolidation</span>
                  </div>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );

  const renderQueueView = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setCurrentView("browser")}
            className="p-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <h2 className="text-xl font-semibold text-white">Transformation Queue</h2>
          <span className="px-2 py-1 bg-purple-600/20 text-purple-300 text-sm rounded-full">
            {transformationQueue.filter(item => item.status === "pending").length} pending
          </span>
        </div>
        <button
          onClick={loadTransformationQueue}
          className="p-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-3">
        {transformationQueue.map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="p-4 bg-white/5 rounded-lg border border-white/10"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <div className={`w-2 h-2 rounded-full ${
                    item.status === "pending" ? "bg-yellow-400" :
                    item.status === "processing" ? "bg-blue-400" :
                    item.status === "completed" ? "bg-green-400" : "bg-red-400"
                  }`} />
                  <span className="font-medium text-white capitalize">{item.transformation_type}</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    item.status === "pending" ? "bg-yellow-600/20 text-yellow-300" :
                    item.status === "processing" ? "bg-blue-600/20 text-blue-300" :
                    item.status === "completed" ? "bg-green-600/20 text-green-300" : "bg-red-600/20 text-red-300"
                  }`}>
                    {item.status}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-2">Content ID: {item.content_id}</p>
                {item.description && (
                  <p className="text-sm text-gray-300 mb-2">"{item.description}"</p>
                )}
                <div className="flex items-center space-x-4 text-xs text-gray-500">
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
                  <>
                    <button
                      onClick={() => {
                        // TODO: Implement edit queue item
                        console.log("Edit queue item:", item.id);
                      }}
                      className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => {
                        // TODO: Implement start processing
                        console.log("Start processing:", item.id);
                      }}
                      className="p-2 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                    >
                      <Zap className="w-4 h-4" />
                    </button>
                  </>
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
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900 text-white">
      <div className="container mx-auto px-6 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold mb-2">Conversation Browser</h1>
          <p className="text-gray-300">Browse, view, and queue conversations for LPE transformation</p>
        </motion.div>

        {/* Main Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-black/20 backdrop-blur-sm rounded-2xl p-6 border border-white/10"
        >
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="w-6 h-6 animate-spin mr-3" />
              <span>Loading...</span>
            </div>
          )}

          {!isLoading && currentView === "browser" && renderConversationList()}
          {!isLoading && currentView === "conversation" && renderConversationView()}
          {!isLoading && currentView === "queue" && renderQueueView()}
        </motion.div>

        {/* Queue Dialog */}
        <AnimatePresence>
          {showQueueDialog && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={() => setShowQueueDialog(false)}
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className="bg-gray-900 rounded-2xl p-6 max-w-lg w-full border border-white/10"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Add to Transformation Queue</h3>
                  <button
                    onClick={() => setShowQueueDialog(false)}
                    className="text-gray-400 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Transformation Type</label>
                    <select
                      value={queueSettings.transformationType}
                      onChange={(e) => setQueueSettings(prev => ({ ...prev, transformationType: e.target.value }))}
                      className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none"
                    >
                      <option value="humanize">Humanize</option>
                      <option value="maieutic">Maieutic Dialogue</option>
                      <option value="translate">Translation Analysis</option>
                      <option value="summarize">Summarize</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Priority</label>
                    <select
                      value={queueSettings.priority}
                      onChange={(e) => setQueueSettings(prev => ({ ...prev, priority: e.target.value }))}
                      className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none"
                    >
                      <option value="low">Low</option>
                      <option value="normal">Normal</option>
                      <option value="high">High</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Description (Optional)</label>
                    <textarea
                      value={queueSettings.description}
                      onChange={(e) => setQueueSettings(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Add notes about this transformation..."
                      className="w-full px-3 py-2 bg-black/20 border border-white/10 rounded-lg focus:border-purple-400 focus:outline-none h-20 resize-none"
                    />
                  </div>

                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      onClick={() => setShowQueueDialog(false)}
                      className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => addToQueue(
                        selectedMessages,
                        queueSettings.transformationType,
                        queueSettings.priority,
                        queueSettings.description
                      )}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
                    >
                      Add to Queue
                    </button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ConversationBrowser;