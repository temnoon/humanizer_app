import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  Eye,
  Edit3,
  Type,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  Save,
  FileText,
  Code,
  AlignLeft,
  Bold,
  Italic,
  Link,
  List,
  Hash,
  Quote,
  Code2,
  RotateCcw,
  Check,
  AlertCircle
} from 'lucide-react';
import { cn } from '../utils';
import MarkdownRenderer from './MarkdownRenderer';

const AdvancedMarkdownEditor = ({ 
  content = '', 
  onChange, 
  onSave,
  title = 'Untitled Page',
  className = '',
  autoSave = true,
  autoSaveDelay = 2000
}) => {
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [fontSize, setFontSize] = useState(14);
  
  // Font size limits
  const MIN_FONT_SIZE = 8;
  const MAX_FONT_SIZE = 32;
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [localContent, setLocalContent] = useState(content);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null); // 'saving', 'saved', 'error'
  const [cursorPosition, setCursorPosition] = useState(0);
  
  const textareaRef = useRef(null);
  const autoSaveTimeoutRef = useRef(null);

  // Auto-save functionality
  useEffect(() => {
    if (autoSave && hasUnsavedChanges) {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
      
      autoSaveTimeoutRef.current = setTimeout(() => {
        handleSave();
      }, autoSaveDelay);
    }

    return () => {
      if (autoSaveTimeoutRef.current) {
        clearTimeout(autoSaveTimeoutRef.current);
      }
    };
  }, [localContent, autoSave, autoSaveDelay, hasUnsavedChanges]);

  // Update local content when prop changes
  useEffect(() => {
    setLocalContent(content);
    setHasUnsavedChanges(false);
  }, [content]);

  const handleContentChange = (newContent) => {
    setLocalContent(newContent);
    setHasUnsavedChanges(true);
    if (onChange) {
      onChange(newContent);
    }
  };

  const handleSave = async () => {    
    setSaveStatus('saving');
    try {
      if (onSave) {
        await onSave(localContent);
      }
      setHasUnsavedChanges(false);
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus(null), 2000);
    } catch (error) {
      console.error('Failed to save:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const insertText = (before, after = '', placeholder = '') => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = localContent.substring(start, end);
    const textToInsert = selectedText || placeholder;
    
    const newContent = 
      localContent.substring(0, start) + 
      before + textToInsert + after + 
      localContent.substring(end);
    
    handleContentChange(newContent);
    
    // Set cursor position after insertion
    setTimeout(() => {
      const newCursorPos = start + before.length + textToInsert.length + (after ? 0 : after.length);
      textarea.setSelectionRange(newCursorPos, newCursorPos);
      textarea.focus();
    }, 0);
  };

  const formatActions = [
    { icon: Bold, action: () => insertText('**', '**', 'bold text'), title: 'Bold' },
    { icon: Italic, action: () => insertText('*', '*', 'italic text'), title: 'Italic' },
    { icon: Link, action: () => insertText('[', '](url)', 'link text'), title: 'Link' },
    { icon: Hash, action: () => insertText('# ', '', 'Heading'), title: 'Heading' },
    { icon: List, action: () => insertText('- ', '', 'List item'), title: 'List' },
    { icon: Quote, action: () => insertText('> ', '', 'Quote'), title: 'Quote' },
    { icon: Code2, action: () => insertText('`', '`', 'code'), title: 'Inline Code' },
    { icon: Code, action: () => insertText('```\n', '\n```', 'code block'), title: 'Code Block' }
  ];

  const laTexExamples = [
    { label: 'Inline Math', text: '$x = y + z$' },
    { label: 'Block Math', text: '$$\\int_{0}^{\\infty} e^{-x} dx = 1$$' },
    { label: 'Fraction', text: '$\\frac{a}{b}$' },
    { label: 'Sum', text: '$\\sum_{i=1}^{n} x_i$' },
    { label: 'Matrix', text: '$\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$' }
  ];

  const editorStyle = {
    fontSize: `${fontSize}px`,
    lineHeight: 1.6,
    fontFamily: 'Monaco, Consolas, "Liberation Mono", "Courier New", monospace'
  };

  return (
    <>
      <style>{`
        .markdown-preview-container {
          font-size: var(--base-font-size);
        }
        .markdown-preview-container h1 {
          font-size: calc(2.25rem * var(--font-scale));
        }
        .markdown-preview-container h2 {
          font-size: calc(1.875rem * var(--font-scale));
        }
        .markdown-preview-container h3 {
          font-size: calc(1.5rem * var(--font-scale));
        }
        .markdown-preview-container h4 {
          font-size: calc(1.25rem * var(--font-scale));
        }
        .markdown-preview-container h5 {
          font-size: calc(1.125rem * var(--font-scale));
        }
        .markdown-preview-container h6 {
          font-size: calc(1rem * var(--font-scale));
        }
        .markdown-preview-container p,
        .markdown-preview-container li,
        .markdown-preview-container td,
        .markdown-preview-container th {
          font-size: var(--base-font-size);
        }
        .markdown-preview-container code {
          font-size: calc(0.875rem * var(--font-scale));
        }
        .markdown-preview-container pre code {
          font-size: calc(0.875rem * var(--font-scale));
        }
        .markdown-preview-container blockquote {
          font-size: var(--base-font-size);
        }
      `}</style>
      <div className={cn(
        "bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col",
        isFullscreen && "fixed inset-0 z-50",
        className
      )}>
      {/* Toolbar */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-3 flex items-center justify-between bg-gray-50 dark:bg-gray-900">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 mr-4">
            <button
              onClick={() => setIsPreviewMode(false)}
              className={cn(
                "px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
                !isPreviewMode 
                  ? "bg-blue-600 text-white" 
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
              )}
            >
              <Edit3 className="w-4 h-4 inline mr-1" />
              Edit
            </button>
            <button
              onClick={() => setIsPreviewMode(true)}
              className={cn(
                "px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
                isPreviewMode 
                  ? "bg-blue-600 text-white" 
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
              )}
            >
              <Eye className="w-4 h-4 inline mr-1" />
              Preview
            </button>
          </div>

          {!isPreviewMode && (
            <div className="flex items-center gap-1">
              {formatActions.map((action, index) => (
                <button
                  key={index}
                  onClick={action.action}
                  title={action.title}
                  className="p-1.5 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
                >
                  <action.icon className="w-4 h-4" />
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Font Size Controls */}
          <div className="flex items-center gap-1 mr-2">
            <button
              onClick={() => setFontSize(Math.max(MIN_FONT_SIZE, fontSize - 2))}
              disabled={fontSize <= MIN_FONT_SIZE}
              className={cn(
                "p-1 transition-colors",
                fontSize <= MIN_FONT_SIZE
                  ? "text-gray-300 dark:text-gray-600 cursor-not-allowed"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
              )}
              title={fontSize <= MIN_FONT_SIZE ? `Minimum size (${MIN_FONT_SIZE}px)` : "Decrease font size"}
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className={cn(
              "text-sm min-w-[4rem] text-center px-2 py-1 rounded",
              fontSize <= MIN_FONT_SIZE || fontSize >= MAX_FONT_SIZE
                ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200"
                : "text-gray-600 dark:text-gray-400"
            )}>
              {fontSize}px{fontSize <= MIN_FONT_SIZE ? " (min)" : fontSize >= MAX_FONT_SIZE ? " (max)" : ""}
            </span>
            <button
              onClick={() => setFontSize(Math.min(MAX_FONT_SIZE, fontSize + 2))}
              disabled={fontSize >= MAX_FONT_SIZE}
              className={cn(
                "p-1 transition-colors",
                fontSize >= MAX_FONT_SIZE
                  ? "text-gray-300 dark:text-gray-600 cursor-not-allowed"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
              )}
              title={fontSize >= MAX_FONT_SIZE ? `Maximum size (${MAX_FONT_SIZE}px)` : "Increase font size"}
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>

          {/* Save Status */}
          {saveStatus && (
            <div className="flex items-center gap-1 text-sm">
              {saveStatus === 'saving' && (
                <>
                  <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  <span className="text-blue-600">Saving...</span>
                </>
              )}
              {saveStatus === 'saved' && (
                <>
                  <Check className="w-4 h-4 text-green-600" />
                  <span className="text-green-600">Saved</span>
                </>
              )}
              {saveStatus === 'error' && (
                <>
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  <span className="text-red-600">Error</span>
                </>
              )}
            </div>
          )}

          {/* Manual Save Button */}
          <button
            onClick={handleSave}
            disabled={saveStatus === 'saving'}
            className={cn(
              "flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
              saveStatus === 'saving'
                ? "bg-gray-400 text-white cursor-not-allowed"
                : hasUnsavedChanges
                ? "bg-blue-600 hover:bg-blue-700 text-white"
                : "bg-green-600 hover:bg-green-700 text-white"
            )}
          >
            <Save className="w-4 h-4" />
            Save
          </button>

          {/* Fullscreen Toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
            title={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* LaTeX Quick Insert Bar (Edit Mode Only) */}
      {!isPreviewMode && (
        <div className="border-b border-gray-200 dark:border-gray-700 p-2 bg-gray-50 dark:bg-gray-900">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400 mr-2">LaTeX:</span>
            {laTexExamples.map((example, index) => (
              <button
                key={index}
                onClick={() => insertText(example.text)}
                className="px-2 py-1 text-xs bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                title={`Insert ${example.label}`}
              >
                {example.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Editor/Preview Content */}
      <div className={cn(
        "relative flex-1",
        !isFullscreen && !className.includes('h-full') && "h-96"
      )}>
        {isPreviewMode ? (
          <div 
            className="absolute inset-0 p-4 markdown-preview-container"
            style={{ 
              fontSize: `${fontSize}px`,
              '--base-font-size': `${fontSize}px`,
              '--font-scale': fontSize / 14,
              overflow: 'auto',
              WebkitOverflowScrolling: 'touch',
              scrollbarWidth: 'thin'
            }}
            tabIndex={0}
            role="region"
            aria-label="Markdown preview"
          >
            <MarkdownRenderer content={localContent} />
          </div>
        ) : (
          <textarea
            ref={textareaRef}
            value={localContent}
            onChange={(e) => handleContentChange(e.target.value)}
            className="absolute inset-0 p-4 border-none resize-none focus:outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            style={{
              ...editorStyle,
              overflow: 'auto',
              WebkitOverflowScrolling: 'touch'
            }}
            placeholder="Start writing your content here... Use LaTeX like $x = y + z$ for inline math or $$\int f(x) dx$$ for block math."
            spellCheck="true"
          />
        )}
      </div>

      {/* Status Bar */}
      <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-2 bg-gray-50 dark:bg-gray-900 text-xs text-gray-600 dark:text-gray-400 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span>{localContent.length} characters</span>
          <span>{localContent.split('\n').length} lines</span>
          <span>{localContent.trim().split(/\s+/).filter(word => word.length > 0).length} words</span>
        </div>
        <div className="flex items-center gap-2">
          {hasUnsavedChanges && (
            <span className="text-orange-600 dark:text-orange-400">Unsaved changes</span>
          )}
          <span>Mode: {isPreviewMode ? 'Preview' : 'Edit'}</span>
        </div>
      </div>
    </div>
    </>
  );
};

export default AdvancedMarkdownEditor;