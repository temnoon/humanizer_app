import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Copy, 
  Check, 
  ZoomIn, 
  ZoomOut, 
  Type, 
  RotateCcw, 
  BookOpen, 
  FileText,
  Edit3,
  Save,
  X,
  Maximize2,
  Minimize2,
  Archive
} from 'lucide-react';
import { cn } from '../utils';
import { saveTransformationToManager } from './TransformationManager';

const SideBySideResults = ({ 
  originalText, 
  transformedText, 
  metadata = {}, 
  onCopy, 
  copied,
  onSave
}) => {
  const [fontSize, setFontSize] = useState(16); // Base font size
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [editableTransformed, setEditableTransformed] = useState(transformedText);
  const [isEditing, setIsEditing] = useState(false);
  const [editingCopied, setEditingCopied] = useState(false);
  const [savedToManager, setSavedToManager] = useState(false);

  // Font size controls
  const increaseFontSize = () => setFontSize(prev => Math.min(prev + 2, 24));
  const decreaseFontSize = () => setFontSize(prev => Math.max(prev - 2, 12));
  const resetFontSize = () => setFontSize(16);

  // Save edited version
  const handleSave = () => {
    if (onSave) {
      onSave(editableTransformed);
    }
    setIsEditing(false);
  };

  // Copy edited version
  const handleCopyEdited = () => {
    navigator.clipboard.writeText(editableTransformed);
    setEditingCopied(true);
    setTimeout(() => setEditingCopied(false), 2000);
  };

  // Save transformation to manager
  const handleSaveToManager = () => {
    try {
      const transformationData = {
        name: `Transformation ${new Date().toLocaleTimeString()}`,
        original_text: originalText,
        transformed_text: editableTransformed,
        persona: metadata.target_persona || '',
        namespace: metadata.target_namespace || '',
        style: metadata.target_style || '',
        metadata: metadata,
        type: metadata.balancing_analysis ? 'balanced' : 'standard',
        preservation_score: metadata.preservation_score || metadata.balancing_analysis?.preservation_score || 0,
        balance_analysis: metadata.balancing_analysis || null,
        performance_metrics: metadata.performance_metrics || null
      };
      
      const savedId = saveTransformationToManager(transformationData);
      
      if (savedId) {
        setSavedToManager(true);
        setTimeout(() => setSavedToManager(false), 3000);
      }
    } catch (error) {
      console.error('Failed to save transformation:', error);
    }
  };

  // Get readable metadata for display
  const getReadableMetadata = () => {
    if (!metadata) return [];
    
    const readable = [];
    if (metadata.target_persona) readable.push({ label: 'Persona', value: metadata.target_persona });
    if (metadata.target_namespace) readable.push({ label: 'Namespace', value: metadata.target_namespace });
    if (metadata.target_style) readable.push({ label: 'Style', value: metadata.target_style });
    if (metadata.total_duration_ms) {
      readable.push({ 
        label: 'Processing Time', 
        value: `${Math.round(metadata.total_duration_ms / 1000)}s` 
      });
    }
    
    return readable;
  };

  const metadataItems = getReadableMetadata();

  const containerClasses = cn(
    "transition-all duration-300",
    isFullscreen 
      ? "fixed inset-0 z-50 bg-white dark:bg-gray-900" 
      : "rounded-2xl bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm border border-gray-200 dark:border-gray-700"
  );

  return (
    <div className={containerClasses}>
      {/* Header with controls */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <BookOpen className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Original → Transformed
          </h2>
          {metadataItems.length > 0 && (
            <div className="hidden md:flex items-center gap-4 ml-6">
              {metadataItems.slice(0, 3).map((item, idx) => (
                <div key={idx} className="text-xs">
                  <span className="text-gray-500 dark:text-gray-400">{item.label}:</span>{' '}
                  <span className="font-medium text-gray-700 dark:text-gray-300 capitalize">
                    {item.value}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {/* Save Transformation button */}
          <button
            onClick={handleSaveToManager}
            className={cn(
              "flex items-center gap-2 px-3 py-2 rounded-lg font-medium transition-all text-sm",
              savedToManager 
                ? "bg-green-600 text-white" 
                : "bg-purple-600 hover:bg-purple-700 text-white"
            )}
            title="Save transformation to manager"
          >
            {savedToManager ? (
              <>
                <Check className="w-4 h-4" />
                <span>Saved!</span>
              </>
            ) : (
              <>
                <Archive className="w-4 h-4" />
                <span>Save</span>
              </>
            )}
          </button>
          
          {/* Font size controls */}
          <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
            <button
              onClick={decreaseFontSize}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
              title="Decrease font size"
            >
              <ZoomOut className="w-3 h-3" />
            </button>
            <span className="text-xs font-mono w-8 text-center">
              {fontSize}
            </span>
            <button
              onClick={increaseFontSize}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
              title="Increase font size"
            >
              <ZoomIn className="w-3 h-3" />
            </button>
            <button
              onClick={resetFontSize}
              className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded ml-1"
              title="Reset font size"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          </div>

          {/* Fullscreen toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Main content - side by side */}
      <div className={cn(
        "flex",
        isFullscreen ? "h-[calc(100vh-73px)]" : "h-[600px]"
      )}>
        {/* Left side - Original */}
        <div className="w-1/2 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          <div className="p-4 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-gray-600 dark:text-gray-400" />
              <h3 className="font-medium text-gray-900 dark:text-white">Original</h3>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                ({originalText?.length || 0} chars)
              </span>
            </div>
          </div>
          
          <div className="flex-1 p-6 overflow-y-auto">
            <div 
              className="prose prose-gray dark:prose-invert max-w-none leading-relaxed"
              style={{ fontSize: `${fontSize}px` }}
            >
              <p className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 leading-relaxed">
                {originalText}
              </p>
            </div>
          </div>
        </div>

        {/* Right side - Transformed */}
        <div className="w-1/2 flex flex-col">
          <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Type className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                <h3 className="font-medium text-gray-900 dark:text-white">Transformed</h3>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  ({editableTransformed?.length || 0} chars)
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                {isEditing ? (
                  <>
                    <button
                      onClick={() => setIsEditing(false)}
                      className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-gray-600 dark:text-gray-400"
                      title="Cancel editing"
                    >
                      <X className="w-3 h-3" />
                    </button>
                    <button
                      onClick={handleSave}
                      className="p-1.5 hover:bg-indigo-200 dark:hover:bg-indigo-700 rounded text-indigo-600 dark:text-indigo-400"
                      title="Save changes"
                    >
                      <Save className="w-3 h-3" />
                    </button>
                    <button
                      onClick={handleCopyEdited}
                      className="p-1.5 hover:bg-indigo-200 dark:hover:bg-indigo-700 rounded text-indigo-600 dark:text-indigo-400"
                      title="Copy edited text"
                    >
                      {editingCopied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => setIsEditing(true)}
                      className="p-1.5 hover:bg-indigo-200 dark:hover:bg-indigo-700 rounded text-indigo-600 dark:text-indigo-400"
                      title="Edit transformed text"
                    >
                      <Edit3 className="w-3 h-3" />
                    </button>
                    <button
                      onClick={onCopy}
                      className="p-1.5 hover:bg-indigo-200 dark:hover:bg-indigo-700 rounded text-indigo-600 dark:text-indigo-400"
                      title="Copy transformed text"
                    >
                      {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex-1 p-6 overflow-y-auto">
            {isEditing ? (
              <textarea
                value={editableTransformed}
                onChange={(e) => setEditableTransformed(e.target.value)}
                className="w-full h-full resize-none border-none bg-transparent text-gray-800 dark:text-gray-200 leading-relaxed focus:outline-none"
                style={{ fontSize: `${fontSize}px` }}
                placeholder="Edit your transformed text here..."
              />
            ) : (
              <div 
                className="prose prose-gray dark:prose-invert max-w-none leading-relaxed"
                style={{ fontSize: `${fontSize}px` }}
              >
                <p className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 leading-relaxed">
                  {editableTransformed}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer with metadata */}
      {metadataItems.length > 0 && (
        <div className="p-4 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-wrap gap-4 text-xs text-gray-600 dark:text-gray-400">
            {metadataItems.map((item, idx) => (
              <div key={idx}>
                <span className="font-medium">{item.label}:</span>{' '}
                <span className="capitalize">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SideBySideResults;