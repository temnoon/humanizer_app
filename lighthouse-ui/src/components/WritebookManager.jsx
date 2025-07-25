import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BookOpen,
  Search,
  Plus,
  Edit3,
  Trash2,
  Calendar,
  User,
  FileText,
  Hash,
  Image,
  Download,
  Upload,
  ExternalLink,
  Filter,
  Grid3X3,
  List,
  Clock,
  Tag,
  Star,
  MoreVertical,
  Copy,
  Archive,
  Share2,
  ArrowLeft
} from 'lucide-react';
import { cn } from '../utils';
import AdvancedMarkdownEditor from './AdvancedMarkdownEditor';

const WritebookManager = ({ onNavigateToEditor }) => {
  const [writebooks, setWritebooks] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedWritebook, setSelectedWritebook] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [sortBy, setSortBy] = useState('modified'); // 'modified', 'created', 'title', 'size'
  const [filterBy, setFilterBy] = useState('all'); // 'all', 'local', 'published', 'drafts'
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingWritebook, setEditingWritebook] = useState(null);

  // Load writebooks from localStorage
  useEffect(() => {
    loadWritebooks();
  }, []);

  const loadWritebooks = () => {
    const stored = [];
    
    // Get all localStorage keys that look like writebooks
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && (key.startsWith('writebook_') || key.includes('_writebook'))) {
        try {
          const data = JSON.parse(localStorage.getItem(key));
          if (data && (data.title || data.leaves || data.pages)) {
            stored.push({
              id: key,
              ...data,
              lastModified: data.lastModified || new Date().toISOString(),
              created: data.created || new Date().toISOString(),
              isLocal: !data.published_url,
              size: JSON.stringify(data).length
            });
          }
        } catch (error) {
          console.warn('Failed to parse writebook data for key:', key);
        }
      }
    }

    // CRITICAL: Remove duplicates based on content similarity
    const deduplicated = [];
    const seenContentHashes = new Set();
    
    stored.forEach(writebook => {
      // Create a simple content hash based on pages and title
      const contentHash = JSON.stringify({
        pages: writebook.pages || writebook.leaves || [],
        pageCount: (writebook.pages || writebook.leaves || []).length
      });
      
      if (!seenContentHashes.has(contentHash)) {
        seenContentHashes.add(contentHash);
        deduplicated.push(writebook);
      } else {
        // This is a duplicate - find the original and keep the one with the better title
        const existingIndex = deduplicated.findIndex(existing => {
          const existingHash = JSON.stringify({
            pages: existing.pages || existing.leaves || [],
            pageCount: (existing.pages || existing.leaves || []).length
          });
          return existingHash === contentHash;
        });
        
        if (existingIndex >= 0) {
          const existing = deduplicated[existingIndex];
          // Keep the one with a more meaningful title (not "Exported Conversation")
          if (existing.title === 'Exported Conversation' && writebook.title !== 'Exported Conversation') {
            // Remove the old localStorage entry
            localStorage.removeItem(existing.id);
            // Replace with the better titled one
            deduplicated[existingIndex] = writebook;
          } else {
            // Remove this duplicate entry
            localStorage.removeItem(writebook.id);
          }
        }
      }
    });

    // Also load published writebooks from the new storage location
    try {
      const publishedBooks = JSON.parse(localStorage.getItem('published_writebooks') || '[]');
      publishedBooks.forEach(book => {
        deduplicated.push({
          id: book.id,
          title: book.title,
          content: book.content,
          pages: book.content?.leaves || [],
          lastModified: book.updated_at,
          created: book.published_at,
          isLocal: book.status === 'local_published',
          isPublished: book.status === 'local_published',
          size: JSON.stringify(book).length,
          status: book.status,
          pages_count: book.pages_count,
          word_count: book.word_count,
          source: book.source
        });
      });
    } catch (error) {
      console.warn('Failed to load published writebooks:', error);
    }

    // Sort writebooks
    deduplicated.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return (a.title || 'Untitled').localeCompare(b.title || 'Untitled');
        case 'created':
          return new Date(b.created) - new Date(a.created);
        case 'size':
          return b.size - a.size;
        case 'modified':
        default:
          return new Date(b.lastModified) - new Date(a.lastModified);
      }
    });

    setWritebooks(deduplicated);
  };

  const filteredWritebooks = writebooks.filter(wb => {
    const matchesSearch = !searchTerm || 
      (wb.title && wb.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (wb.content && wb.content.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesFilter = filterBy === 'all' || 
      (filterBy === 'local' && wb.isLocal) ||
      (filterBy === 'published' && !wb.isLocal) ||
      (filterBy === 'drafts' && (!wb.pages || wb.pages.length === 0));
    
    return matchesSearch && matchesFilter;
  });

  const createNewWritebook = () => {
    const newWritebook = {
      id: `writebook_${Date.now()}`,
      title: 'New Writebook',
      created: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      pages: [{
        id: 'page_1',
        type: 'page',
        content: '# Welcome to your new writebook\n\nStart writing here...',
        created_at: new Date().toISOString()
      }],
      isLocal: true,
      size: 0
    };

    localStorage.setItem(newWritebook.id, JSON.stringify(newWritebook));
    loadWritebooks();
    openWritebook(newWritebook);
  };

  const openWritebook = (writebook) => {
    if (onNavigateToEditor) {
      // Store the writebook data for the editor
      localStorage.setItem('writebookExportData', JSON.stringify(writebook));
      onNavigateToEditor();
    }
  };

  const deleteWritebook = (writebookId) => {
    if (confirm('Are you sure you want to delete this writebook?')) {
      localStorage.removeItem(writebookId);
      loadWritebooks();
    }
  };

  const duplicateWritebook = (writebook) => {
    const copy = {
      ...writebook,
      id: `writebook_${Date.now()}`,
      title: `${writebook.title} (Copy)`,
      created: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      published_url: null,
      isLocal: true
    };

    localStorage.setItem(copy.id, JSON.stringify(copy));
    loadWritebooks();
  };

  const exportWritebook = (writebook) => {
    const dataStr = JSON.stringify(writebook, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `${writebook.title.replace(/\s+/g, '_')}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const importWritebook = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target.result);
        const writebook = {
          ...imported,
          id: `writebook_${Date.now()}`,
          imported: true,
          lastModified: new Date().toISOString()
        };

        localStorage.setItem(writebook.id, JSON.stringify(writebook));
        loadWritebooks();
      } catch (error) {
        alert('Failed to import writebook: Invalid JSON format');
      }
    };
    reader.readAsText(file);
    event.target.value = ''; // Reset file input
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
    return Math.round(bytes / (1024 * 1024)) + ' MB';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getWritebookStats = (writebook) => {
    const pages = writebook.pages || writebook.leaves || [];
    const sections = pages.filter(p => p.type === 'section' || p.type === 'Section').length;
    const textPages = pages.filter(p => p.type === 'page' || p.type === 'Page' || !p.type).length;
    const images = pages.filter(p => p.type === 'picture' || p.type === 'image' || p.type === 'Picture').length;
    
    // Debug logging for troubleshooting
    if (pages.length === 0 && writebook.title) {
      console.log(`Debug: ${writebook.title} has 0 pages:`, {
        writebook_pages: writebook.pages,
        writebook_leaves: writebook.leaves,
        writebook_content: writebook.content,
        pages_count: writebook.pages_count
      });
    }
    
    return { pages: pages.length, sections, textPages, images };
  };

  if (editingWritebook) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        {/* Header */}
        <div className="bg-white/10 backdrop-blur-sm border-b border-white/20">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setEditingWritebook(null)}
                  className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Back to Manager
                </button>
                
                <div className="flex items-center gap-3">
                  <BookOpen className="w-6 h-6 text-blue-400" />
                  <div>
                    <input
                      type="text"
                      value={editingWritebook.title}
                      onChange={(e) => {
                        const updated = {
                          ...editingWritebook,
                          title: e.target.value,
                          lastModified: new Date().toISOString()
                        };
                        localStorage.setItem(editingWritebook.id, JSON.stringify(updated));
                        setEditingWritebook(updated);
                        loadWritebooks();
                      }}
                      className="text-xl font-bold text-white bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-400 rounded px-2 py-1 min-w-0"
                      placeholder="Enter book title..."
                    />
                    <p className="text-sm text-gray-300">
                      Quick Edit Mode
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Full-Screen Editor */}
        <div className="max-w-7xl mx-auto p-6">
          <div className="h-[calc(100vh-12rem)]">
            <AdvancedMarkdownEditor
              content={editingWritebook.pages?.[0]?.content || ''}
              title={editingWritebook.title}
              onChange={(newContent) => {
                const updated = {
                  ...editingWritebook,
                  pages: editingWritebook.pages?.length > 0 ? [{
                    ...editingWritebook.pages[0],
                    content: newContent,
                    lastModified: new Date().toISOString()
                  }] : [{
                    id: 'page_1',
                    type: 'page',
                    content: newContent,
                    created_at: new Date().toISOString(),
                    lastModified: new Date().toISOString()
                  }],
                  lastModified: new Date().toISOString()
                };
                localStorage.setItem(editingWritebook.id, JSON.stringify(updated));
                setEditingWritebook(updated);
                loadWritebooks();
              }}
              autoSave={true}
              className="h-full"
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Writebook Manager
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Manage your writebooks, create new ones, and publish to writebook.humanizer.com
            </p>
          </div>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg cursor-pointer transition-colors">
              <Upload className="w-4 h-4" />
              Import
              <input
                type="file"
                accept=".json"
                onChange={importWritebook}
                className="hidden"
              />
            </label>
            <button
              onClick={createNewWritebook}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Writebook
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search writebooks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:border-blue-400 focus:outline-none"
            />
          </div>
          
          <select
            value={filterBy}
            onChange={(e) => setFilterBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:border-blue-400 focus:outline-none"
          >
            <option value="all">All Writebooks</option>
            <option value="local">Local Only</option>
            <option value="published">Published</option>
            <option value="drafts">Drafts</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:border-blue-400 focus:outline-none"
          >
            <option value="modified">Last Modified</option>
            <option value="created">Date Created</option>
            <option value="title">Title</option>
            <option value="size">Size</option>
          </select>

          <div className="flex items-center border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                "p-2 transition-colors",
                viewMode === 'grid' 
                  ? "bg-blue-600 text-white" 
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
              )}
            >
              <Grid3X3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                "p-2 transition-colors",
                viewMode === 'list' 
                  ? "bg-blue-600 text-white" 
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
              )}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Writebooks</p>
              <p className="text-xl font-semibold text-gray-900 dark:text-white">{writebooks.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <Edit3 className="w-5 h-5 text-green-600" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Local Drafts</p>
              <p className="text-xl font-semibold text-gray-900 dark:text-white">
                {writebooks.filter(w => w.isLocal).length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <ExternalLink className="w-5 h-5 text-purple-600" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Published</p>
              <p className="text-xl font-semibold text-gray-900 dark:text-white">
                {writebooks.filter(w => !w.isLocal).length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-orange-600" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Pages</p>
              <p className="text-xl font-semibold text-gray-900 dark:text-white">
                {writebooks.reduce((sum, w) => sum + (w.pages?.length || 0), 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Writebooks Grid/List */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700">
        {filteredWritebooks.length === 0 ? (
          <div className="p-8 text-center">
            <BookOpen className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {searchTerm ? 'No matching writebooks' : 'No writebooks yet'}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {searchTerm 
                ? 'Try adjusting your search or filters'
                : 'Create your first writebook to get started'
              }
            </p>
            {!searchTerm && (
              <button
                onClick={createNewWritebook}
                className="flex items-center gap-2 mx-auto px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
                Create Writebook
              </button>
            )}
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
            {filteredWritebooks.map((writebook) => {
              const stats = getWritebookStats(writebook);
              return (
                <motion.div
                  key={writebook.id}
                  layout
                  className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      <h3 
                        className="font-medium text-gray-900 dark:text-white truncate cursor-pointer hover:text-blue-600"
                        onClick={() => openWritebook(writebook)}
                      >
                        {writebook.title || 'Untitled'}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        {writebook.isLocal ? (
                          <span className="text-xs bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400 px-2 py-1 rounded">
                            Local
                          </span>
                        ) : (
                          <span className="text-xs bg-purple-100 dark:bg-purple-900/20 text-purple-800 dark:text-purple-400 px-2 py-1 rounded">
                            Published
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => setEditingWritebook(writebook)}
                        className="p-1 text-gray-500 hover:text-blue-600"
                        title="Quick edit"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => duplicateWritebook(writebook)}
                        className="p-1 text-gray-500 hover:text-green-600"
                        title="Duplicate"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => exportWritebook(writebook)}
                        className="p-1 text-gray-500 hover:text-orange-600"
                        title="Export"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteWritebook(writebook.id)}
                        className="p-1 text-gray-500 hover:text-red-600"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400 mb-3">
                    <div className="flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      {stats.pages} pages
                    </div>
                    <div className="flex items-center gap-1">
                      <Hash className="w-3 h-3" />
                      {stats.sections} sections
                    </div>
                  </div>

                  <div className="text-xs text-gray-500 space-y-1">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Modified {formatDate(writebook.lastModified)}
                    </div>
                    <div>Size: {formatFileSize(writebook.size)}</div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {filteredWritebooks.map((writebook) => {
              const stats = getWritebookStats(writebook);
              return (
                <div key={writebook.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1 min-w-0">
                      <BookOpen className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <h3 
                          className="font-medium text-gray-900 dark:text-white truncate cursor-pointer hover:text-blue-600"
                          onClick={() => openWritebook(writebook)}
                        >
                          {writebook.title || 'Untitled'}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                          <span>{stats.pages} pages</span>
                          <span>{stats.sections} sections</span>
                          <span>{formatFileSize(writebook.size)}</span>
                          <span>Modified {formatDate(writebook.lastModified)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {writebook.isLocal ? (
                        <span className="text-xs bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400 px-2 py-1 rounded">
                          Local
                        </span>
                      ) : (
                        <span className="text-xs bg-purple-100 dark:bg-purple-900/20 text-purple-800 dark:text-purple-400 px-2 py-1 rounded">
                          Published
                        </span>
                      )}
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => setEditingWritebook(writebook)}
                          className="p-1 text-gray-500 hover:text-blue-600"
                          title="Quick edit"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openWritebook(writebook)}
                          className="p-1 text-gray-500 hover:text-green-600"
                          title="Open in full editor"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => exportWritebook(writebook)}
                          className="p-1 text-gray-500 hover:text-orange-600"
                          title="Export"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => deleteWritebook(writebook.id)}
                          className="p-1 text-gray-500 hover:text-red-600"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default WritebookManager;