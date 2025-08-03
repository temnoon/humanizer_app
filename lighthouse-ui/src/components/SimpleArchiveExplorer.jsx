import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  MessageSquare,
  ArrowLeft,
  Calendar,
  Hash,
  User,
  Zap,
  Clock,
  FileText,
  Star,
  Filter,
  ChevronRight,
  Copy,
  ExternalLink,
  MoreVertical,
  X,
  Plus
} from "lucide-react";

const SimpleArchiveExplorer = ({ onNavigate }) => {
  // Tabbed interface state
  const [tabs, setTabs] = useState([
    { id: 'search', type: 'search', title: 'Archive Search', searchQuery: '', conversations: [] }
  ]);
  const [activeTabId, setActiveTabId] = useState('search');
  
  // Current tab data
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState("text"); // "text" or "semantic"
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [error, setError] = useState(null);

  const API_BASE = "http://localhost:8100/api";

  // Get current tab
  const currentTab = tabs.find(tab => tab.id === activeTabId) || tabs[0];
  const conversations = currentTab.type === 'search' ? currentTab.conversations : [];

  // Load conversations on mount
  useEffect(() => {
    console.log("SimpleArchiveExplorer mounted, loading conversations...");
    if (currentTab.type === 'search') {
      loadConversations();
    }
  }, [currentPage, activeTabId]);

  // Search when search type changes (but not when query changes)
  useEffect(() => {
    if (searchQuery.trim()) {
      performSearch();
    }
  }, [searchType]);

  // Tab management functions
  const createConversationTab = (conversation) => {
    const newTab = {
      id: `conv-${conversation.id}`,
      type: 'conversation',
      title: conversation.title || `Conversation ${conversation.id}`,
      conversation: conversation,
      messages: []
    };
    
    setTabs(prevTabs => [...prevTabs, newTab]);
    setActiveTabId(newTab.id);
    return newTab;
  };

  const closeTab = (tabId) => {
    if (tabId === 'search') return; // Don't close the search tab
    
    setTabs(prevTabs => {
      const newTabs = prevTabs.filter(tab => tab.id !== tabId);
      if (activeTabId === tabId) {
        // Switch to the search tab if we're closing the active tab
        setActiveTabId(newTabs[0]?.id || 'search');
      }
      return newTabs;
    });
  };

  const switchTab = (tabId) => {
    setActiveTabId(tabId);
  };

  const loadConversations = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${API_BASE}/conversations?page=${currentPage}&limit=20&sort_by=created&order=desc`
      );
      if (response.ok) {
        const data = await response.json();
        // Update the search tab with conversations
        setTabs(prevTabs => 
          prevTabs.map(tab => 
            tab.id === 'search' 
              ? { ...tab, conversations: data.conversations || [] }
              : tab
          )
        );
        setTotalPages(data.pagination?.pages || 1);
      } else {
        throw new Error(`Failed to load conversations: ${response.status}`);
      }
    } catch (error) {
      console.error("Failed to load conversations:", error);
      setError(error.message);
      // Clear conversations on error
      setTabs(prevTabs => 
        prevTabs.map(tab => 
          tab.id === 'search' 
            ? { ...tab, conversations: [] }
            : tab
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const performSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    try {
      // Use the correct conversation search endpoint
      const formData = new FormData();
      formData.append('query', searchQuery);
      formData.append('limit', '50'); // Search more results
      
      const response = await fetch(`${API_BASE}/conversations/search`, {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        // Update the search tab with search results
        setTabs(prevTabs => 
          prevTabs.map(tab => 
            tab.id === 'search' 
              ? { ...tab, conversations: data.conversations || [], searchQuery: searchQuery }
              : tab
          )
        );
        console.log(`Found ${data.total_results} search results for "${searchQuery}"`);
      } else {
        throw new Error(`Search failed: ${response.status}`);
      }
    } catch (error) {
      console.error("Search failed:", error);
      setError(`Search failed: ${error.message}`);
      // Clear conversations on error
      setTabs(prevTabs => 
        prevTabs.map(tab => 
          tab.id === 'search' 
            ? { ...tab, conversations: [] }
            : tab
        )
      );
    } finally {
      setIsSearching(false);
    }
  };

  const openConversation = async (conversation) => {
    // Check if this conversation is already open in a tab
    const existingTab = tabs.find(tab => tab.type === 'conversation' && tab.conversation?.id === conversation.id);
    
    if (existingTab) {
      // Just switch to the existing tab
      setActiveTabId(existingTab.id);
      return;
    }

    // Create a new tab for this conversation
    const newTab = createConversationTab(conversation);
    
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/conversations/${conversation.id}/messages`);
      if (response.ok) {
        const data = await response.json();
        // Update the tab with messages
        setTabs(prevTabs => 
          prevTabs.map(tab => 
            tab.id === newTab.id 
              ? { ...tab, messages: data.messages || [], conversation: { ...conversation, ...data.conversation } }
              : tab
          )
        );
      }
    } catch (error) {
      console.error("Failed to load messages:", error);
      setError(`Failed to load conversation: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getMessagePreview = (content) => {
    if (!content) return "No content";
    const text = typeof content === 'string' ? content : content.parts?.[0]?.text || "No content";
    return text.substring(0, 120) + (text.length > 120 ? "..." : "");
  };

  const copyMessage = (content) => {
    const text = typeof content === 'string' ? content : content.parts?.[0]?.text || "";
    navigator.clipboard.writeText(text);
  };

  const handleSearchKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (searchQuery.trim()) {
        performSearch();
      } else {
        loadConversations();
      }
    }
  };

  const getConversationTitle = (conversation) => {
    // Try multiple title fields
    return conversation.title || 
           conversation.name || 
           conversation.subject ||
           conversation.conversation_title ||
           `Conversation ${conversation.id}` ||
           "Untitled Conversation";
  };

  // Tab bar component
  const TabBar = () => (
    <div className="flex bg-card/30 border-b border-border/30">
      {tabs.map((tab) => (
        <div key={tab.id} className="flex items-center">
          <button
            onClick={() => switchTab(tab.id)}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTabId === tab.id
                ? "border-primary text-primary bg-primary/10"
                : "border-transparent text-card-secondary hover:text-foreground hover:bg-card/50"
            }`}
          >
            <div className="flex items-center space-x-2">
              {tab.type === 'search' ? (
                <Search className="w-4 h-4" />
              ) : (
                <MessageSquare className="w-4 h-4" />
              )}
              <span className="max-w-32 truncate">{tab.title}</span>
            </div>
          </button>
          
          {tab.id !== 'search' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                closeTab(tab.id);
              }}
              className="p-1 ml-1 hover:bg-card/50 rounded transition-colors"
              title="Close tab"
            >
              <X className="w-3 h-3 text-card-secondary" />
            </button>
          )}
        </div>
      ))}
    </div>
  );

  // Error display
  if (error) {
    return (
      <div className="h-full flex flex-col bg-background">
        <TabBar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="w-8 h-8 text-red-400" />
            </div>
            <h2 className="text-xl font-semibold text-foreground mb-2">Archive Error</h2>
            <p className="text-card-secondary mb-4">{error}</p>
            <button 
              onClick={() => {
                setError(null);
                if (currentTab.type === 'search') {
                  loadConversations();
                }
              }}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Search tab view
  if (currentTab.type === 'search') {
    return (
      <div className="h-full flex flex-col bg-background">
        <TabBar />
        {/* Header with search */}
        <div className="border-b border-border/30 bg-card/20 backdrop-blur-sm">
          <div className="p-6">
            <div className="flex items-center space-x-3 mb-4">
              <MessageSquare className="w-6 h-6 text-primary" />
              <h1 className="text-2xl font-bold text-foreground">Archive Explorer</h1>
            </div>
            
            {/* Search bar */}
            <div className="flex space-x-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-card-secondary" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleSearchKeyPress}
                  placeholder="Search conversations... (Press Enter to search)"
                  className="w-full pl-10 pr-16 py-3 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
                {searchQuery && (
                  <button
                    onClick={() => {
                      setSearchQuery("");
                      loadConversations();
                    }}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-muted rounded transition-colors"
                    title="Clear search"
                  >
                    <X className="w-4 h-4 text-card-secondary" />
                  </button>
                )}
              </div>
              
              {/* Search type toggle */}
              <div className="flex bg-background border border-border rounded-lg p-1">
                <button
                  onClick={() => setSearchType("text")}
                  className={`px-4 py-2 rounded text-sm font-medium transition-all ${
                    searchType === "text"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-card-secondary hover:text-foreground"
                  }`}
                >
                  <FileText className="w-4 h-4 mr-2 inline" />
                  Text
                </button>
                <button
                  onClick={() => setSearchType("semantic")}
                  className={`px-4 py-2 rounded text-sm font-medium transition-all ${
                    searchType === "semantic"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-card-secondary hover:text-foreground"
                  }`}
                >
                  <Zap className="w-4 h-4 mr-2 inline" />
                  Semantic
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading || isSearching ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
              <span className="ml-3 text-card-secondary">
                {isSearching ? "Searching..." : "Loading conversations..."}
              </span>
            </div>
          ) : (
            <div className="space-y-3">
              {conversations.map((conversation) => (
                <motion.div
                  key={conversation.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ scale: 1.01 }}
                  onClick={() => openConversation(conversation)}
                  className="bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-border/30 hover:border-primary/50 cursor-pointer transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-foreground text-lg mb-2 line-clamp-2">
                        {getConversationTitle(conversation)}
                      </h3>
                      
                      <div className="flex items-center space-x-4 text-sm text-card-secondary mb-3">
                        <div className="flex items-center space-x-1">
                          <MessageSquare className="w-3 h-3" />
                          <span>{conversation.messages || conversation.message_count || 0} messages</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{formatDate(conversation.created || conversation.timestamp)}</span>
                        </div>
                        {conversation.source && (
                          <div className="flex items-center space-x-1">
                            <Hash className="w-3 h-3" />
                            <span>{conversation.source}</span>
                          </div>
                        )}
                      </div>
                      
                      {conversation.preview && (
                        <p className="text-card-secondary text-sm line-clamp-2">
                          {conversation.preview}
                        </p>
                      )}
                    </div>
                    
                    <ChevronRight className="w-5 h-5 text-card-secondary ml-4 flex-shrink-0" />
                  </div>
                </motion.div>
              ))}
              
              {conversations.length === 0 && !isLoading && !isSearching && (
                <div className="text-center py-12">
                  <MessageSquare className="w-16 h-16 text-card-secondary mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    {searchQuery ? "No conversations found" : "No conversations available"}
                  </h3>
                  <p className="text-card-secondary">
                    {searchQuery 
                      ? "Try adjusting your search query or search type"
                      : "Import some conversation archives to get started"
                    }
                  </p>
                </div>
              )}
            </div>
          )}
          
          {/* Pagination */}
          {!searchQuery && totalPages > 1 && (
            <div className="flex items-center justify-center space-x-2 mt-8">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-border rounded-lg hover:bg-card/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="px-4 py-2 text-sm text-card-secondary">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 border border-border rounded-lg hover:bg-card/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Conversation tab view
  const conversationMessages = currentTab.messages || [];
  
  return (
    <div className="h-full flex flex-col bg-background">
      <TabBar />
      {/* Header with conversation info */}
      <div className="border-b border-border/30 bg-card/20 backdrop-blur-sm">
        <div className="p-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1 min-w-0">
              <h1 className="text-xl font-bold text-foreground line-clamp-2">
                {currentTab.conversation?.title || currentTab.title}
              </h1>
              <div className="flex items-center space-x-4 text-sm text-card-secondary mt-1">
                <div className="flex items-center space-x-1">
                  <MessageSquare className="w-3 h-3" />
                  <span>{conversationMessages.length} messages</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Calendar className="w-3 h-3" />
                  <span>{formatDate(currentTab.conversation?.created || currentTab.conversation?.timestamp)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            <span className="ml-3 text-card-secondary">Loading messages...</span>
          </div>
        ) : (
          <div className="space-y-6 max-w-4xl mx-auto">
            {conversationMessages.map((message, index) => (
              <motion.div
                key={message.id || index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] ${
                  message.role === 'user' 
                    ? 'bg-primary/20 text-foreground' 
                    : 'bg-card/50 text-foreground'
                } rounded-lg p-4 border border-border/30`}>
                  
                  {/* Message header */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${
                        message.role === 'user' ? 'bg-primary' : 'bg-blue-400'
                      }`} />
                      <span className="text-sm font-medium text-card-secondary capitalize">
                        {message.role || 'Unknown'}
                      </span>
                      {message.timestamp && (
                        <span className="text-xs text-card-secondary">
                          {formatDate(message.timestamp)}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => copyMessage(message.content)}
                        className="p-1 hover:bg-muted rounded transition-colors"
                        title="Copy message"
                      >
                        <Copy className="w-3 h-3 text-card-secondary" />
                      </button>
                      <button
                        className="p-1 hover:bg-muted rounded transition-colors"
                        title="More options"
                      >
                        <MoreVertical className="w-3 h-3 text-card-secondary" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Message content */}
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    {typeof message.content === 'string' ? (
                      <div className="whitespace-pre-wrap">{message.content}</div>
                    ) : message.content?.parts?.[0]?.text ? (
                      <div className="whitespace-pre-wrap">{message.content.parts[0].text}</div>
                    ) : (
                      <div className="text-card-secondary italic">No content available</div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
            
            {conversationMessages.length === 0 && !isLoading && (
              <div className="text-center py-12">
                <MessageSquare className="w-16 h-16 text-card-secondary mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2">No messages found</h3>
                <p className="text-card-secondary">This conversation appears to be empty</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleArchiveExplorer;