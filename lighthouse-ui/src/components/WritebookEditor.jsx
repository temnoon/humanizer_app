import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen,
  Trash2,
  Edit3,
  Save,
  Plus,
  Move3D,
  User,
  Clock,
  MessageSquare,
  Zap,
  Copy,
  Download,
  Check,
  ChevronUp,
  ChevronDown,
  FileText,
  Hash,
  Image,
  Upload,
  Globe,
  Loader2,
  ExternalLink,
  AlertCircle
} from 'lucide-react';
import { cn } from '../utils';

const WritebookEditor = () => {
  const [writebookData, setWritebookData] = useState(null);
  const [pages, setPages] = useState([]);
  const [selectedPages, setSelectedPages] = useState(new Set());
  const [isEditing, setIsEditing] = useState(false);
  const [editingPageId, setEditingPageId] = useState(null);
  const [bookTitle, setBookTitle] = useState('');
  const [savedStatus, setSavedStatus] = useState(false);
  
  // Publishing state
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishStatus, setPublishStatus] = useState(null); // 'success', 'error', null
  const [publishedUrl, setPublishedUrl] = useState(null);
  const [writebookSettings, setWritebookSettings] = useState({
    baseUrl: 'https://writebook.humanizer.com',
    apiKey: '', // User can set this in settings
    isPublic: false
  });

  // Load writebook data from localStorage or conversation export
  useEffect(() => {
    const exportedData = localStorage.getItem('writebookExportData');
    if (exportedData) {
      const data = JSON.parse(exportedData);
      setWritebookData(data);
      setPages(data.pages || []);
      setBookTitle(data.title || 'Exported Conversation');
      // Clear the export data after loading
      localStorage.removeItem('writebookExportData');
    }
  }, []);

  const deletePage = (pageId) => {
    setPages(pages.filter(page => page.id !== pageId));
    setSelectedPages(prev => {
      const newSet = new Set(prev);
      newSet.delete(pageId);
      return newSet;
    });
  };

  const deleteSelectedPages = () => {
    setPages(pages.filter(page => !selectedPages.has(page.id)));
    setSelectedPages(new Set());
  };

  const movePage = (pageId, direction) => {
    const currentIndex = pages.findIndex(page => page.id === pageId);
    if (currentIndex === -1) return;

    const newPages = [...pages];
    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    
    if (newIndex >= 0 && newIndex < pages.length) {
      [newPages[currentIndex], newPages[newIndex]] = [newPages[newIndex], newPages[currentIndex]];
      setPages(newPages);
    }
  };

  const updatePageContent = (pageId, newContent) => {
    setPages(pages.map(page => 
      page.id === pageId ? { ...page, content: newContent } : page
    ));
  };

  const addSectionBreak = (afterPageId = null) => {
    const newSection = {
      id: Date.now().toString(),
      type: 'section',
      title: 'New Section',
      created_at: new Date().toISOString()
    };

    if (afterPageId) {
      const index = pages.findIndex(page => page.id === afterPageId);
      const newPages = [...pages];
      newPages.splice(index + 1, 0, newSection);
      setPages(newPages);
    } else {
      setPages([...pages, newSection]);
    }
  };

  const togglePageSelection = (pageId) => {
    setSelectedPages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(pageId)) {
        newSet.delete(pageId);
      } else {
        newSet.add(pageId);
      }
      return newSet;
    });
  };

  const exportToWritebook = () => {
    const writebookFormat = {
      title: bookTitle,
      leaves: pages.map((page, index) => ({
        id: page.id,
        position: index + 1,
        type: page.type,
        content: page.content,
        title: page.title,
        author: page.author,
        timestamp: page.timestamp,
        original_message_id: page.original_message_id
      }))
    };

    const dataStr = JSON.stringify(writebookFormat, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `${bookTitle.replace(/\s+/g, '_')}_writebook.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();

    setSavedStatus(true);
    setTimeout(() => setSavedStatus(false), 3000);
  };

  const publishToWritebook = async () => {
    if (!bookTitle.trim() || pages.length === 0) {
      setPublishStatus('error');
      setTimeout(() => setPublishStatus(null), 5000);
      return;
    }

    setIsPublishing(true);
    setPublishStatus(null);

    try {
      // Convert pages to Writebook format
      const writebookPayload = {
        title: bookTitle,
        is_public: writebookSettings.isPublic,
        leaves: pages.map((page, index) => ({
          type: page.type === 'section' ? 'Section' : 'Page',
          content: page.type === 'section' ? page.title : page.content,
          position: index + 1,
          // Add metadata as comments if needed
          metadata: {
            original_author: page.author,
            original_timestamp: page.timestamp,
            original_message_id: page.original_message_id
          }
        })),
        source_metadata: writebookData?.metadata || {}
      };

      // Attempt to publish to your Writebook instance
      const response = await fetch(`${writebookSettings.baseUrl}/api/import_conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(writebookSettings.apiKey && { 'Authorization': `Bearer ${writebookSettings.apiKey}` })
        },
        body: JSON.stringify(writebookPayload)
      });

      if (response.ok) {
        const result = await response.json();
        setPublishedUrl(result.url || `${writebookSettings.baseUrl}/books/${result.book_id}`);
        setPublishStatus('success');
        
        // Store the published URL for future reference
        if (result.book_id) {
          localStorage.setItem(`writebook_${writebookData?.metadata?.conversation_id}`, JSON.stringify({
            book_id: result.book_id,
            url: result.url,
            published_at: new Date().toISOString()
          }));
        }
      } else {
        // If API endpoint doesn't exist yet, provide helpful instructions
        if (response.status === 404) {
          console.warn('Writebook API endpoint not found. You need to add the custom API endpoint to your Writebook installation.');
          // Fall back to opening the Writebook site with instructions
          window.open(`${writebookSettings.baseUrl}`, '_blank');
          setPublishStatus('manual');
        } else {
          throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }
      }
    } catch (error) {
      console.error('Failed to publish to Writebook:', error);
      setPublishStatus('error');
      
      // Provide fallback: open Writebook with instructions
      if (error.message.includes('fetch')) {
        // Network error - probably API endpoint doesn't exist yet
        window.open(`${writebookSettings.baseUrl}`, '_blank');
        setPublishStatus('manual');
      }
    } finally {
      setIsPublishing(false);
      
      // Clear status after delay
      setTimeout(() => {
        setPublishStatus(null);
        setPublishedUrl(null);
      }, 10000);
    }
  };

  const getPageTypeIcon = (type) => {
    switch (type) {
      case 'section': return Hash;
      case 'picture': return Image;
      default: return FileText;
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleString();
  };

  if (!writebookData) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-8 border border-gray-200 dark:border-gray-700 text-center">
          <BookOpen className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Writebook Editor
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Export a conversation from the Conversations tab to start creating your writebook.
          </p>
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              <strong>How to use:</strong> Go to the Conversations tab, find an interesting conversation, 
              and click "Export to Writebook" to start editing it here.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-blue-600" />
            <div>
              <input
                type="text"
                value={bookTitle}
                onChange={(e) => setBookTitle(e.target.value)}
                className="text-2xl font-bold text-gray-900 dark:text-white bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-400 rounded px-2 py-1"
                placeholder="Enter book title..."
              />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {pages.length} pages • Edit and organize your content
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {selectedPages.size > 0 && (
              <button
                onClick={deleteSelectedPages}
                className="flex items-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                Delete {selectedPages.size} pages
              </button>
            )}
            <button
              onClick={() => addSectionBreak()}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              Section
            </button>
            <button
              onClick={exportToWritebook}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                savedStatus 
                  ? "bg-green-600 text-white" 
                  : "bg-blue-600 hover:bg-blue-700 text-white"
              )}
            >
              {savedStatus ? (
                <>
                  <Check className="w-4 h-4" />
                  Exported!
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Export Writebook
                </>
              )}
            </button>
            <button
              onClick={publishToWritebook}
              disabled={isPublishing || !bookTitle.trim() || pages.length === 0}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                publishStatus === 'success' 
                  ? "bg-green-600 text-white" 
                  : publishStatus === 'error'
                  ? "bg-red-600 text-white"
                  : publishStatus === 'manual'
                  ? "bg-orange-600 text-white"
                  : "bg-purple-600 hover:bg-purple-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              {isPublishing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Publishing...
                </>
              ) : publishStatus === 'success' ? (
                <>
                  <Check className="w-4 h-4" />
                  Published!
                </>
              ) : publishStatus === 'error' ? (
                <>
                  <AlertCircle className="w-4 h-4" />
                  Failed
                </>
              ) : publishStatus === 'manual' ? (
                <>
                  <ExternalLink className="w-4 h-4" />
                  Manual Setup
                </>
              ) : (
                <>
                  <Globe className="w-4 h-4" />
                  Publish to Writebook
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {publishStatus && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className={cn(
            "p-4 rounded-lg border",
            publishStatus === 'success' && "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200",
            publishStatus === 'error' && "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200",
            publishStatus === 'manual' && "bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800 text-orange-800 dark:text-orange-200"
          )}
        >
          <div className="flex items-start gap-3">
            {publishStatus === 'success' && <Check className="w-5 h-5 mt-0.5 flex-shrink-0" />}
            {publishStatus === 'error' && <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />}
            {publishStatus === 'manual' && <ExternalLink className="w-5 h-5 mt-0.5 flex-shrink-0" />}
            <div className="flex-1">
              {publishStatus === 'success' && (
                <>
                  <h4 className="font-medium mb-1">Successfully Published!</h4>
                  <p className="text-sm mb-2">Your writebook has been created at writebook.humanizer.com</p>
                  {publishedUrl && (
                    <a 
                      href={publishedUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm underline hover:no-underline inline-flex items-center gap-1"
                    >
                      View Published Writebook <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </>
              )}
              {publishStatus === 'error' && (
                <>
                  <h4 className="font-medium mb-1">Publishing Failed</h4>
                  <p className="text-sm">Could not connect to writebook.humanizer.com. Make sure the API endpoint is set up.</p>
                </>
              )}
              {publishStatus === 'manual' && (
                <>
                  <h4 className="font-medium mb-1">Manual Setup Required</h4>
                  <p className="text-sm mb-2">The API endpoint doesn't exist yet. You'll need to add it to your Writebook installation.</p>
                  <details className="text-xs mt-2">
                    <summary className="cursor-pointer font-medium">Setup Instructions</summary>
                    <div className="mt-2 space-y-2 pl-4 border-l-2 border-current">
                      <p>Add this to your Writebook Rails app:</p>
                      <pre className="bg-black/10 p-2 rounded text-xs overflow-x-auto">
{`# config/routes.rb
post '/api/import_conversation', to: 'api#import_conversation'

# app/controllers/api_controller.rb
class ApiController < ApplicationController
  def import_conversation
    json_data = JSON.parse(request.body.read)
    book = Book.create!(title: json_data['title'])
    
    json_data['leaves'].each_with_index do |leaf, index|
      book.leaves.create!(
        type: leaf['type'],
        content: leaf['content'], 
        position: index + 1
      )
    end
    
    render json: { book_id: book.id }
  end
end`}
                      </pre>
                    </div>
                  </details>
                </>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Writebook Settings */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700">
        <details className="group">
          <summary className="p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-purple-600" />
                <span className="font-medium text-gray-900 dark:text-white">Writebook Settings</span>
              </div>
              <ChevronDown className="w-4 h-4 text-gray-500 transition-transform group-open:rotate-180" />
            </div>
          </summary>
          <div className="px-4 pb-4 border-t border-gray-200 dark:border-gray-700">
            <div className="space-y-4 mt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Writebook URL
                </label>
                <input
                  type="url"
                  value={writebookSettings.baseUrl}
                  onChange={(e) => setWritebookSettings(prev => ({ ...prev, baseUrl: e.target.value }))}
                  placeholder="https://writebook.humanizer.com"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:border-purple-400 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  API Key (Optional)
                </label>
                <input
                  type="password"
                  value={writebookSettings.apiKey}
                  onChange={(e) => setWritebookSettings(prev => ({ ...prev, apiKey: e.target.value }))}
                  placeholder="Optional authentication token"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:border-purple-400 focus:outline-none"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is-public"
                  checked={writebookSettings.isPublic}
                  onChange={(e) => setWritebookSettings(prev => ({ ...prev, isPublic: e.target.checked }))}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <label htmlFor="is-public" className="text-sm text-gray-700 dark:text-gray-300">
                  Publish as public writebook
                </label>
              </div>
            </div>
          </div>
        </details>
      </div>

      {/* Pages List */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold text-gray-900 dark:text-white">Book Pages</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Click to select pages for deletion, or edit individual pages
          </p>
        </div>
        
        <div className="max-h-96 overflow-y-auto">
          {pages.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No pages in this writebook
            </div>
          ) : (
            <div className="space-y-2 p-4">
              {pages.map((page, index) => {
                const PageIcon = getPageTypeIcon(page.type);
                const isSelected = selectedPages.has(page.id);
                const isEditing = editingPageId === page.id;
                
                return (
                  <motion.div
                    key={page.id}
                    layout
                    className={cn(
                      "border rounded-lg p-4 transition-all",
                      isSelected 
                        ? "border-red-300 bg-red-50 dark:bg-red-900/20" 
                        : "border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700/50"
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1 min-w-0">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => togglePageSelection(page.id)}
                          className="mt-1"
                        />
                        <PageIcon className="w-4 h-4 mt-1 text-gray-500 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
                              {page.type}
                            </span>
                            {page.author && (
                              <span className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-1">
                                <User className="w-3 h-3" />
                                {page.author}
                              </span>
                            )}
                            {page.timestamp && (
                              <span className="text-xs text-gray-500 flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {formatTimestamp(page.timestamp)}
                              </span>
                            )}
                          </div>
                          
                          {page.type === 'section' ? (
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {page.title}
                            </h4>
                          ) : isEditing ? (
                            <textarea
                              value={page.content}
                              onChange={(e) => updatePageContent(page.id, e.target.value)}
                              className="w-full h-32 p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                              onBlur={() => setEditingPageId(null)}
                              autoFocus
                            />
                          ) : (
                            <p 
                              className="text-sm text-gray-700 dark:text-gray-300 line-clamp-3 cursor-pointer"
                              onClick={() => setEditingPageId(page.id)}
                            >
                              {page.content || page.title}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-1 ml-4">
                        <button
                          onClick={() => movePage(page.id, 'up')}
                          disabled={index === 0}
                          className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-50"
                          title="Move up"
                        >
                          <ChevronUp className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => movePage(page.id, 'down')}
                          disabled={index === pages.length - 1}
                          className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-50"
                          title="Move down"
                        >
                          <ChevronDown className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => addSectionBreak(page.id)}
                          className="p-1 text-blue-600 hover:text-blue-700 dark:hover:text-blue-400"
                          title="Add section after"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => deletePage(page.id)}
                          className="p-1 text-red-600 hover:text-red-700"
                          title="Delete page"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Metadata */}
      {writebookData.metadata && (
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <h4 className="font-medium text-gray-900 dark:text-white mb-2">Source Information</h4>
          <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            {writebookData.metadata.conversation_id && (
              <p>Conversation ID: {writebookData.metadata.conversation_id}</p>
            )}
            {writebookData.metadata.participant_count && (
              <p>Participants: {writebookData.metadata.participant_count}</p>
            )}
            {writebookData.metadata.date_range && (
              <p>Date Range: {writebookData.metadata.date_range.join(' - ')}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WritebookEditor;