import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Archive,
  Search,
  Filter,
  Download,
  Upload,
  RefreshCw,
  Eye,
  Edit3,
  Trash2,
  Copy,
  Save,
  Clock,
  User,
  BarChart3,
  FileText,
  Calendar,
  Tag,
  Plus,
  X,
  Check,
  AlertTriangle,
  Star,
  StarOff,
  FolderPlus,
  Folder,
  ChevronDown,
  ChevronRight,
  GitBranch,
  Target,
  Brain
} from "lucide-react";
import { cn } from "../utils";

const TransformationManager = () => {
  // State management
  const [savedTransformations, setSavedTransformations] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTransformation, setSelectedTransformation] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sortBy, setSortBy] = useState("created_at"); // created_at, name, type, preservation_score
  const [sortOrder, setSortOrder] = useState("desc");
  const [filterType, setFilterType] = useState("all"); // all, balanced, standard
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState("all");
  const [showCreateCollection, setShowCreateCollection] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState("");

  // Load saved transformations on mount
  useEffect(() => {
    loadSavedTransformations();
    loadCollections();
  }, []);

  const loadSavedTransformations = async () => {
    setIsLoading(true);
    try {
      // Get transformations from localStorage for now
      // TODO: Replace with API call to backend
      const saved = JSON.parse(localStorage.getItem('savedTransformations') || '[]');
      setSavedTransformations(saved);
    } catch (error) {
      console.error("Failed to load saved transformations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCollections = async () => {
    try {
      const saved = JSON.parse(localStorage.getItem('transformationCollections') || '[]');
      setCollections(saved);
    } catch (error) {
      console.error("Failed to load collections:", error);
    }
  };

  const saveTransformation = (transformationData) => {
    const newTransformation = {
      id: Date.now().toString(),
      name: transformationData.name || `Transformation ${Date.now()}`,
      type: transformationData.type || 'standard',
      created_at: new Date().toISOString(),
      original_text: transformationData.original_text,
      transformed_text: transformationData.transformed_text,
      persona: transformationData.persona,
      namespace: transformationData.namespace,
      style: transformationData.style,
      steps: transformationData.steps || [],
      metadata: transformationData.metadata || {},
      balance_analysis: transformationData.balance_analysis || null,
      performance_metrics: transformationData.performance_metrics || null,
      preservation_score: transformationData.preservation_score || 0,
      collection_id: transformationData.collection_id || null,
      tags: transformationData.tags || [],
      starred: false
    };

    const updated = [...savedTransformations, newTransformation];
    setSavedTransformations(updated);
    localStorage.setItem('savedTransformations', JSON.stringify(updated));
    
    return newTransformation.id;
  };

  const deleteTransformation = (id) => {
    const updated = savedTransformations.filter(t => t.id !== id);
    setSavedTransformations(updated);
    localStorage.setItem('savedTransformations', JSON.stringify(updated));
    
    if (selectedTransformation?.id === id) {
      setSelectedTransformation(null);
      setShowDetails(false);
    }
  };

  const toggleStar = (id) => {
    const updated = savedTransformations.map(t => 
      t.id === id ? { ...t, starred: !t.starred } : t
    );
    setSavedTransformations(updated);
    localStorage.setItem('savedTransformations', JSON.stringify(updated));
  };

  const createCollection = () => {
    if (!newCollectionName.trim()) return;
    
    const newCollection = {
      id: Date.now().toString(),
      name: newCollectionName.trim(),
      created_at: new Date().toISOString(),
      color: 'blue' // TODO: Add color picker
    };
    
    const updated = [...collections, newCollection];
    setCollections(updated);
    localStorage.setItem('transformationCollections', JSON.stringify(updated));
    setNewCollectionName("");
    setShowCreateCollection(false);
  };

  const addToCollection = (transformationId, collectionId) => {
    const updated = savedTransformations.map(t => 
      t.id === transformationId ? { ...t, collection_id: collectionId } : t
    );
    setSavedTransformations(updated);
    localStorage.setItem('savedTransformations', JSON.stringify(updated));
  };

  const exportTransformations = () => {
    const dataStr = JSON.stringify(savedTransformations, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `transformations_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  const importTransformations = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const imported = JSON.parse(e.target.result);
        const updated = [...savedTransformations, ...imported];
        setSavedTransformations(updated);
        localStorage.setItem('savedTransformations', JSON.stringify(updated));
        alert(`Imported ${imported.length} transformations`);
      } catch (error) {
        alert('Failed to import transformations: Invalid file format');
      }
    };
    reader.readAsText(file);
    event.target.value = '';
  };

  // Filter and sort transformations
  const filteredTransformations = savedTransformations
    .filter(t => {
      // Search filter
      const matchesSearch = !searchQuery || 
        t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.original_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.transformed_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      
      // Type filter
      const matchesType = filterType === 'all' || t.type === filterType;
      
      // Collection filter
      const matchesCollection = selectedCollection === 'all' || 
        t.collection_id === selectedCollection ||
        (selectedCollection === 'starred' && t.starred) ||
        (selectedCollection === 'unorganized' && !t.collection_id);
      
      return matchesSearch && matchesType && matchesCollection;
    })
    .sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];
      
      if (sortBy === 'created_at') {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      }
      
      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1;
      } else {
        return aVal < bVal ? 1 : -1;
      }
    });

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Archive className="w-6 h-6 text-purple-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Transformation Manager
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {savedTransformations.length} saved transformations • Manage, organize, and reuse your work
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowCreateCollection(true)}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors"
            >
              <FolderPlus className="w-4 h-4" />
              Collection
            </button>
            <button
              onClick={exportTransformations}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <label className="flex items-center gap-2 px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg text-sm font-medium transition-colors cursor-pointer">
              <Upload className="w-4 h-4" />
              Import
              <input
                type="file"
                accept=".json"
                onChange={importTransformations}
                className="hidden"
              />
            </label>
            <button
              onClick={loadSavedTransformations}
              className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {/* Search and Filters */}
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search transformations..."
              className="w-full pl-10 pr-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-purple-400 focus:outline-none"
            />
          </div>
          
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-purple-400 focus:outline-none"
          >
            <option value="all">All Types</option>
            <option value="balanced">Balanced</option>
            <option value="standard">Standard</option>
          </select>
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:border-purple-400 focus:outline-none"
          >
            <option value="created_at">Date Created</option>
            <option value="name">Name</option>
            <option value="preservation_score">Preservation Score</option>
          </select>
          
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="p-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
            title={sortOrder === 'asc' ? 'Sort Descending' : 'Sort Ascending'}
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Collections Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Collections</h3>
            
            <div className="space-y-1">
              {/* Built-in collections */}
              <button
                onClick={() => setSelectedCollection('all')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg transition-colors text-sm",
                  selectedCollection === 'all' 
                    ? "bg-purple-600 text-white" 
                    : "hover:bg-gray-100 dark:hover:bg-gray-700"
                )}
              >
                <Folder className="w-4 h-4 inline mr-2" />
                All ({savedTransformations.length})
              </button>
              
              <button
                onClick={() => setSelectedCollection('starred')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg transition-colors text-sm",
                  selectedCollection === 'starred' 
                    ? "bg-purple-600 text-white" 
                    : "hover:bg-gray-100 dark:hover:bg-gray-700"
                )}
              >
                <Star className="w-4 h-4 inline mr-2" />
                Starred ({savedTransformations.filter(t => t.starred).length})
              </button>
              
              <button
                onClick={() => setSelectedCollection('unorganized')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg transition-colors text-sm",
                  selectedCollection === 'unorganized' 
                    ? "bg-purple-600 text-white" 
                    : "hover:bg-gray-100 dark:hover:bg-gray-700"
                )}
              >
                <FileText className="w-4 h-4 inline mr-2" />
                Unorganized ({savedTransformations.filter(t => !t.collection_id).length})
              </button>
              
              {/* Custom collections */}
              {collections.map(collection => (
                <button
                  key={collection.id}
                  onClick={() => setSelectedCollection(collection.id)}
                  className={cn(
                    "w-full text-left px-3 py-2 rounded-lg transition-colors text-sm",
                    selectedCollection === collection.id 
                      ? "bg-purple-600 text-white" 
                      : "hover:bg-gray-100 dark:hover:bg-gray-700"
                  )}
                >
                  <Folder className="w-4 h-4 inline mr-2" />
                  {collection.name} ({savedTransformations.filter(t => t.collection_id === collection.id).length})
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Transformations List */}
        <div className="lg:col-span-3">
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                Transformations ({filteredTransformations.length})
              </h3>
            </div>
            
            {isLoading ? (
              <div className="text-center py-8">
                <RefreshCw className="w-8 h-8 mx-auto animate-spin text-gray-400 mb-2" />
                <p className="text-gray-500">Loading transformations...</p>
              </div>
            ) : filteredTransformations.length === 0 ? (
              <div className="text-center py-8">
                <Archive className="w-8 h-8 mx-auto text-gray-400 mb-2" />
                <p className="text-gray-500">No transformations found</p>
                <p className="text-sm text-gray-400">Create a transformation to get started</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {filteredTransformations.map((transformation) => (
                  <motion.div
                    key={transformation.id}
                    layout
                    className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-medium text-gray-900 dark:text-white truncate">
                            {transformation.name}
                          </h4>
                          {transformation.type === 'balanced' && (
                            <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded text-xs">
                              Balanced
                            </span>
                          )}
                          {transformation.starred && (
                            <Star className="w-4 h-4 text-yellow-500 fill-current" />
                          )}
                        </div>
                        
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          <div className="flex items-center gap-4">
                            <span>
                              <User className="w-3 h-3 inline mr-1" />
                              {transformation.persona}
                            </span>
                            <span>
                              <Target className="w-3 h-3 inline mr-1" />
                              {transformation.namespace}
                            </span>
                            <span>
                              <Calendar className="w-3 h-3 inline mr-1" />
                              {new Date(transformation.created_at).toLocaleDateString()}
                            </span>
                            {transformation.preservation_score > 0 && (
                              <span>
                                <BarChart3 className="w-3 h-3 inline mr-1" />
                                {(transformation.preservation_score * 100).toFixed(1)}%
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2">
                          {transformation.original_text.substring(0, 150)}...
                        </p>
                        
                        {transformation.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {transformation.tags.slice(0, 3).map((tag, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-1 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded text-xs"
                              >
                                {tag}
                              </span>
                            ))}
                            {transformation.tags.length > 3 && (
                              <span className="text-xs text-gray-500">+{transformation.tags.length - 3} more</span>
                            )}
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-1 ml-4">
                        <button
                          onClick={() => toggleStar(transformation.id)}
                          className="p-1 text-yellow-600 hover:bg-yellow-100 dark:hover:bg-yellow-900/30 rounded transition-colors"
                          title={transformation.starred ? "Remove from starred" : "Add to starred"}
                        >
                          {transformation.starred ? (
                            <Star className="w-4 h-4 fill-current" />
                          ) : (
                            <StarOff className="w-4 h-4" />
                          )}
                        </button>
                        
                        <button
                          onClick={() => {
                            setSelectedTransformation(transformation);
                            setShowDetails(true);
                          }}
                          className="p-1 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded transition-colors"
                          title="View details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        
                        <button
                          onClick={() => navigator.clipboard.writeText(transformation.transformed_text)}
                          className="p-1 text-green-600 hover:bg-green-100 dark:hover:bg-green-900/30 rounded transition-colors"
                          title="Copy transformed text"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                        
                        <button
                          onClick={() => deleteTransformation(transformation.id)}
                          className="p-1 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Collection Modal */}
      {showCreateCollection && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Create Collection
            </h3>
            
            <input
              type="text"
              value={newCollectionName}
              onChange={(e) => setNewCollectionName(e.target.value)}
              placeholder="Collection name..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-4"
              onKeyDown={(e) => {
                if (e.key === 'Enter') createCollection();
                if (e.key === 'Escape') setShowCreateCollection(false);
              }}
              autoFocus
            />
            
            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setShowCreateCollection(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={createCollection}
                disabled={!newCollectionName.trim()}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium"
              >
                Create
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Transformation Details Modal */}
      {showDetails && selectedTransformation && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                {selectedTransformation.name}
              </h3>
              <button
                onClick={() => setShowDetails(false)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {/* Details content would go here */}
            <div className="space-y-6">
              {/* Original vs Transformed */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Original</h4>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 max-h-48 overflow-y-auto">
                    <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {selectedTransformation.original_text}
                    </p>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Transformed</h4>
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 max-h-48 overflow-y-auto">
                    <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {selectedTransformation.transformed_text}
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Steps if available */}
              {selectedTransformation.steps && selectedTransformation.steps.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                    Transformation Steps ({selectedTransformation.steps.length})
                  </h4>
                  <div className="space-y-3">
                    {selectedTransformation.steps.map((step, index) => (
                      <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-900 dark:text-white">
                            {step.name}
                          </span>
                          {step.preservation_score && (
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                              Preservation: {(step.preservation_score * 100).toFixed(1)}%
                            </span>
                          )}
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600 dark:text-gray-400">Input:</span>
                            <p className="text-gray-800 dark:text-gray-200 mt-1">
                              {step.input_snapshot || step.input || 'N/A'}
                            </p>
                          </div>
                          <div>
                            <span className="text-gray-600 dark:text-gray-400">Output:</span>
                            <p className="text-gray-800 dark:text-gray-200 mt-1">
                              {step.output_snapshot || step.output || 'N/A'}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

// Export function to save a transformation from other components
export const saveTransformationToManager = (transformationData) => {
  const existing = JSON.parse(localStorage.getItem('savedTransformations') || '[]');
  const newTransformation = {
    id: Date.now().toString(),
    name: transformationData.name || `Transformation ${new Date().toLocaleTimeString()}`,
    type: transformationData.type || 'standard',
    created_at: new Date().toISOString(),
    original_text: transformationData.original_text || '',
    transformed_text: transformationData.transformed_text || '',
    persona: transformationData.persona || '',
    namespace: transformationData.namespace || '',
    style: transformationData.style || '',
    steps: transformationData.steps || [],
    metadata: transformationData.metadata || {},
    balance_analysis: transformationData.balance_analysis || null,
    performance_metrics: transformationData.performance_metrics || null,
    preservation_score: transformationData.preservation_score || 0,
    collection_id: null,
    tags: transformationData.tags || [],
    starred: false
  };

  const updated = [...existing, newTransformation];
  localStorage.setItem('savedTransformations', JSON.stringify(updated));
  
  return newTransformation.id;
};

export default TransformationManager;