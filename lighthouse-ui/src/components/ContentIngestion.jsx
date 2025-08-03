import React, { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  File,
  FileText,
  Image as ImageIcon,
  Video,
  Music,
  Archive,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  Plus,
  X,
  Brain,
  Zap,
  Target,
  Eye,
  AlertCircle
} from "lucide-react";

const ContentIngestion = ({ onNavigate }) => {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [processing, setProcessing] = useState(new Set());
  const [completed, setCompleted] = useState(new Set());
  const [failed, setFailed] = useState(new Set());
  const [analysisResults, setAnalysisResults] = useState({});
  const [textInput, setTextInput] = useState("");
  const [textTitle, setTextTitle] = useState("");
  const [textTags, setTextTags] = useState("");
  const [isProcessingText, setIsProcessingText] = useState(false);
  const [textResult, setTextResult] = useState(null);
  const fileInputRef = useRef(null);

  const supportedFormats = {
    text: ['.txt', '.md', '.doc', '.docx', '.rtf'],
    spreadsheet: ['.csv', '.xlsx', '.xls'],
    image: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
    audio: ['.mp3', '.wav', '.m4a', '.aac'],
    video: ['.mp4', '.mov', '.avi', '.mkv'],
    archive: ['.zip', '.rar', '.7z', '.tar', '.gz']
  };

  const getFileIcon = (filename) => {
    const ext = filename.toLowerCase().slice(filename.lastIndexOf('.'));
    if (supportedFormats.text.includes(ext)) return FileText;
    if (supportedFormats.image.includes(ext)) return ImageIcon;
    if (supportedFormats.audio.includes(ext)) return Music;
    if (supportedFormats.video.includes(ext)) return Video;
    if (supportedFormats.archive.includes(ext)) return Archive;
    return File;
  };

  const getFileType = (filename) => {
    const ext = filename.toLowerCase().slice(filename.lastIndexOf('.'));
    for (const [type, extensions] of Object.entries(supportedFormats)) {
      if (extensions.includes(ext)) return type;
    }
    return 'unknown';
  };

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    addFiles(selectedFiles);
  };

  const addFiles = (newFiles) => {
    const fileObjects = newFiles.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      fileType: getFileType(file.name),
      status: 'pending',
      addedAt: new Date()
    }));

    setFiles(prev => [...prev, ...fileObjects]);
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    setProcessing(prev => {
      const next = new Set(prev);
      next.delete(fileId);
      return next;
    });
    setCompleted(prev => {
      const next = new Set(prev);
      next.delete(fileId);
      return next;
    });
    setFailed(prev => {
      const next = new Set(prev);
      next.delete(fileId);
      return next;
    });
  };

  const processTextInput = async () => {
    if (!textInput.trim()) return;
    
    setIsProcessingText(true);
    setTextResult(null);
    
    try {
      const tags = textTags.split(',').map(tag => tag.trim()).filter(tag => tag);
      
      const response = await fetch('http://localhost:8100/api/content/ingest/text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: textInput,
          title: textTitle || undefined,
          source: 'direct_input',
          content_type: 'text',
          tags: tags.length > 0 ? tags : undefined
        })
      });

      if (response.ok) {
        const result = await response.json();
        setTextResult(result);
        // Clear the form after successful processing
        setTextInput("");
        setTextTitle("");
        setTextTags("");
      } else {
        const error = await response.text();
        throw new Error(error);
      }
    } catch (error) {
      console.error("Text processing failed:", error);
      setTextResult({ error: error.message });
    } finally {
      setIsProcessingText(false);
    }
  };

  const processFile = async (fileObj) => {
    setProcessing(prev => new Set(prev).add(fileObj.id));
    
    try {
      const formData = new FormData();
      formData.append('file', fileObj.file);
      formData.append('content_type', fileObj.fileType);
      formData.append('source', 'web_upload');

      // Use real Enhanced Lighthouse API endpoint
      const response = await fetch('http://localhost:8100/api/content/ingest/file', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Analyze the content immediately after ingestion
      const analysisResponse = await fetch('http://localhost:8100/api/content/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_id: result.content_id,
          analysis_type: 'comprehensive'
        })
      });

      if (analysisResponse.ok) {
        const analysis = await analysisResponse.json();
        setAnalysisResults(prev => ({
          ...prev,
          [fileObj.id]: analysis
        }));
      }

      setCompleted(prev => new Set(prev).add(fileObj.id));
      setProcessing(prev => {
        const next = new Set(prev);
        next.delete(fileObj.id);
        return next;
      });

    } catch (error) {
      console.error('File processing failed:', error);
      setFailed(prev => new Set(prev).add(fileObj.id));
      setProcessing(prev => {
        const next = new Set(prev);
        next.delete(fileObj.id);
        return next;
      });
    }
  };

  const processAllFiles = () => {
    files.forEach(fileObj => {
      if (!processing.has(fileObj.id) && !completed.has(fileObj.id) && !failed.has(fileObj.id)) {
        processFile(fileObj);
      }
    });
  };

  const clearAll = () => {
    setFiles([]);
    setProcessing(new Set());
    setCompleted(new Set());
    setFailed(new Set());
    setAnalysisResults({});
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const FileItem = ({ fileObj }) => {
    const Icon = getFileIcon(fileObj.name);
    const isProcessing = processing.has(fileObj.id);
    const isCompleted = completed.has(fileObj.id);
    const isFailed = failed.has(fileObj.id);
    const analysis = analysisResults[fileObj.id];

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-border/50"
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Icon className="w-5 h-5 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-foreground truncate">{fileObj.name}</h3>
            <div className="flex items-center space-x-2 text-sm text-card-secondary">
              <span>{formatFileSize(fileObj.size)}</span>
              <span>•</span>
              <span className="capitalize">{fileObj.fileType}</span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {isProcessing && (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                <Loader2 className="w-4 h-4 text-blue-400" />
              </motion.div>
            )}
            {isCompleted && <CheckCircle className="w-4 h-4 text-green-400" />}
            {isFailed && <XCircle className="w-4 h-4 text-red-400" />}
            {!isProcessing && !isCompleted && !isFailed && <Clock className="w-4 h-4 text-card-secondary" />}
            <button
              onClick={() => removeFile(fileObj.id)}
              className="p-1 hover:bg-destructive/20 rounded transition-colors"
            >
              <X className="w-4 h-4 text-card-secondary hover:text-destructive" />
            </button>
          </div>
        </div>

        {/* Analysis Results */}
        {analysis && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="mt-4 pt-4 border-t border-border/30"
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div className="flex items-center space-x-2">
                <Brain className="w-4 h-4 text-purple-400" />
                <span className="text-card-secondary">
                  {analysis.themes?.length || 0} themes
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-yellow-400" />
                <span className="text-card-secondary">
                  Quality: {Math.round((analysis.quality_score || 0) * 100)}%
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-blue-400" />
                <span className="text-card-secondary">
                  {analysis.insights?.length || 0} insights
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Eye className="w-4 h-4 text-green-400" />
                <button
                  onClick={() => onNavigate && onNavigate('archive-explorer', { contentId: analysis.content_id })}
                  className="text-primary hover:underline"
                >
                  View in Archive
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Action Buttons */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-border/30">
          <div className="flex space-x-2">
            {!isProcessing && !isCompleted && !isFailed && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => processFile(fileObj)}
                className="px-3 py-1.5 bg-primary text-primary-foreground rounded text-sm hover:bg-primary/90 transition-colors"
              >
                Process Now
              </motion.button>
            )}
            {isCompleted && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                onClick={() => onNavigate && onNavigate('narrative-studio', { contentId: analysis?.content_id })}
                className="px-3 py-1.5 bg-green-600 text-white rounded text-sm hover:bg-green-700 transition-colors"
              >
                Transform
              </motion.button>
            )}
            {isFailed && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                onClick={() => processFile(fileObj)}
                className="px-3 py-1.5 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition-colors"
              >
                Retry
              </motion.button>
            )}
          </div>
          <span className="text-xs text-card-secondary">
            Added {fileObj.addedAt.toLocaleTimeString()}
          </span>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground mb-2">
            Content Ingestion
          </h1>
          <p className="text-card-secondary">
            Upload and process content for insight discovery
          </p>
        </div>
        <div className="flex space-x-2">
          {files.length > 0 && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              onClick={clearAll}
              className="px-4 py-2 border border-destructive text-destructive rounded-lg hover:bg-destructive/10 transition-colors"
            >
              Clear All
            </motion.button>
          )}
          <motion.button
            whileHover={{ scale: 1.05 }}
            onClick={processAllFiles}
            disabled={files.length === 0}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Process All Files
          </motion.button>
        </div>
      </div>

      {/* Direct Text Input */}
      <div className="bg-card/80 backdrop-blur-sm rounded-lg p-6 border border-border">
        <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <Brain className="w-5 h-5 mr-2 text-blue-400" />
          Direct Text Input
        </h2>
        
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Title (optional)
              </label>
              <input
                type="text"
                value={textTitle}
                onChange={(e) => setTextTitle(e.target.value)}
                placeholder="Enter a title for your content"
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Tags (comma-separated)
              </label>
              <input
                type="text"
                value={textTags}
                onChange={(e) => setTextTags(e.target.value)}
                placeholder="tag1, tag2, tag3"
                className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Content
            </label>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Enter your text content here..."
              rows={8}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg resize-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center justify-between">
            <div className="text-sm text-card-secondary">
              {textInput.length > 0 && (
                <span>{textInput.split(' ').length} words, {textInput.length} characters</span>
              )}
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={processTextInput}
              disabled={!textInput.trim() || isProcessingText}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isProcessingText ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  <span>Process Text</span>
                </>
              )}
            </motion.button>
          </div>
        </div>
        
        {/* Text Processing Result */}
        {textResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-4 bg-background/50 rounded-lg border border-border/30"
          >
            {textResult.error ? (
              <div className="flex items-center space-x-2 text-red-400">
                <AlertCircle className="w-4 h-4" />
                <span>Error: {textResult.error}</span>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-foreground">{textResult.title}</h4>
                  <span className="text-xs text-card-secondary">
                    ID: {textResult.content_id}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-card-secondary">Words:</span>
                    <div className="font-medium text-foreground">{textResult.word_count}</div>
                  </div>
                  <div>
                    <span className="text-card-secondary">Quality:</span>
                    <div className="font-medium text-foreground">{(textResult.quality_score * 100).toFixed(0)}%</div>
                  </div>
                  <div>
                    <span className="text-card-secondary">Themes:</span>
                    <div className="font-medium text-foreground">{textResult.extracted_themes.length}</div>
                  </div>
                  <div>
                    <span className="text-card-secondary">Processing:</span>
                    <div className="font-medium text-foreground">{textResult.processing_time_ms}ms</div>
                  </div>
                </div>
                
                {textResult.extracted_themes.length > 0 && (
                  <div>
                    <span className="text-sm text-card-secondary">Extracted Themes:</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {textResult.extracted_themes.map((theme, index) => (
                        <span key={index} className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs">
                          {theme}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                <div>
                  <span className="text-sm text-card-secondary">Summary:</span>
                  <p className="text-sm text-foreground mt-1">{textResult.summary}</p>
                </div>
                
                <div className="flex space-x-2">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    onClick={() => onNavigate && onNavigate('narrative-studio', { contentId: textResult.content_id })}
                    className="px-3 py-1.5 bg-green-600 text-white rounded text-sm hover:bg-green-700 transition-colors"
                  >
                    Transform
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    onClick={() => onNavigate && onNavigate('archive-explorer', { contentId: textResult.content_id })}
                    className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                  >
                    View in Archive
                  </motion.button>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Upload Area */}
      <motion.div
        className={`relative border-2 border-dashed rounded-lg p-8 transition-all ${
          isDragging 
            ? 'border-primary bg-primary/5' 
            : 'border-border/50 hover:border-border'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="text-center">
          <Upload className="w-12 h-12 text-card-secondary mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">
            Drop files here or click to upload
          </h3>
          <p className="text-card-secondary mb-4">
            Supports text, images, audio, video, spreadsheets, and archives
          </p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center space-x-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Select Files</span>
          </motion.button>
        </div>

        {/* Supported Formats */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 text-sm">
          {Object.entries(supportedFormats).map(([type, extensions]) => (
            <div key={type} className="text-center">
              <div className="font-medium text-foreground capitalize mb-1">{type}</div>
              <div className="text-card-secondary text-xs">
                {extensions.slice(0, 3).join(', ')}
                {extensions.length > 3 && ` +${extensions.length - 3}`}
              </div>
            </div>
          ))}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept={Object.values(supportedFormats).flat().join(',')}
        />
      </motion.div>

      {/* Processing Status */}
      {files.length > 0 && (
        <div className="bg-card/30 backdrop-blur-sm rounded-lg p-4 border border-border/30">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-foreground">Upload Queue</h2>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-card-secondary">{processing.size} processing</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-card-secondary">{completed.size} completed</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                <span className="text-card-secondary">{failed.size} failed</span>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <motion.div
              className="bg-primary h-2 rounded-full"
              style={{
                width: `${files.length > 0 ? ((completed.size + failed.size) / files.length) * 100 : 0}%`
              }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-foreground">Files</h2>
          <AnimatePresence>
            {files.map(fileObj => (
              <FileItem key={fileObj.id} fileObj={fileObj} />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Empty State */}
      {files.length === 0 && (
        <div className="text-center py-12">
          <AlertCircle className="w-16 h-16 text-card-secondary mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">No files uploaded yet</h3>
          <p className="text-card-secondary">
            Start by uploading some content to begin discovering insights
          </p>
        </div>
      )}
    </div>
  );
};

export default ContentIngestion;