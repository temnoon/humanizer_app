import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FolderOpen,
  Upload,
  Settings,
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  XCircle,
  Clock,
  FileText,
  Folder,
  HardDrive,
  Search,
  Filter,
  Download,
  Eye,
  Trash2,
  Plus,
  Minus,
  BarChart3,
  Activity,
  Layers,
  Hash,
  Calendar,
  User,
  Database,
  ChevronRight,
  ChevronDown,
  Info,
  Zap,
  Target,
  Cpu,
  Archive
} from "lucide-react";

const FilesystemIngestion = ({ onNavigate }) => {
  const [folderPermissions, setFolderPermissions] = useState([]);
  const [selectedFolders, setSelectedFolders] = useState([]);
  const [scanResults, setScanResults] = useState({});
  const [ingestionJobs, setIngestionJobs] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState("folders"); // folders, scan, ingest, jobs, documents
  const [isLoading, setIsLoading] = useState(false);
  const [currentJob, setCurrentJob] = useState(null);
  const [ingestionSettings, setIngestionSettings] = useState({
    file_types: ["txt", "md", "py", "js", "json", "yaml", "xml", "pdf", "odt"],
    chunk_size: 1000,
    overlap_size: 200,
    generate_summaries: true,
    max_summary_levels: 3,
    force_reprocess: false
  });
  const [folderInput, setFolderInput] = useState("");
  const [selectedDocument, setSelectedDocument] = useState(null);

  const API_BASE = "http://localhost:8100/api/filesystem";

  useEffect(() => {
    loadFolderPermissions();
    loadRecentJobs();
    loadDocuments();
  }, []);

  useEffect(() => {
    if (currentJob && currentJob.status === "processing") {
      const interval = setInterval(() => {
        checkJobStatus(currentJob.id);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [currentJob]);

  const loadFolderPermissions = async () => {
    try {
      const response = await fetch(`${API_BASE}/permissions/folders`);
      if (response.ok) {
        const data = await response.json();
        setFolderPermissions(data);
      }
    } catch (error) {
      console.error("Failed to load folder permissions:", error);
    }
  };

  const loadRecentJobs = async () => {
    try {
      const response = await fetch(`${API_BASE}/jobs?limit=10`);
      if (response.ok) {
        const data = await response.json();
        setIngestionJobs(data);
      }
    } catch (error) {
      console.error("Failed to load jobs:", error);
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${API_BASE}/documents?limit=50`);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error("Failed to load documents:", error);
    }
  };

  const addFolderPermission = async () => {
    if (!folderInput.trim()) return;

    try {
      const response = await fetch(`${API_BASE}/permissions/folder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          folder_path: folderInput.trim(),
          is_accessible: true,
          access_level: "read"
        })
      });

      if (response.ok) {
        await loadFolderPermissions();
        setFolderInput("");
      } else {
        const error = await response.json();
        alert(`Failed to add folder: ${error.detail}`);
      }
    } catch (error) {
      console.error("Failed to add folder permission:", error);
      alert("Failed to add folder permission");
    }
  };

  const scanFolder = async (folderPath) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          folder_path: folderPath,
          file_types: ingestionSettings.file_types
        })
      });

      if (response.ok) {
        const data = await response.json();
        setScanResults(prev => ({ ...prev, [folderPath]: data }));
      } else {
        const error = await response.json();
        alert(`Failed to scan folder: ${error.detail}`);
      }
    } catch (error) {
      console.error("Failed to scan folder:", error);
      alert("Failed to scan folder");
    } finally {
      setIsLoading(false);
    }
  };

  const startIngestion = async () => {
    if (selectedFolders.length === 0) {
      alert("Please select at least one folder to ingest");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          folder_paths: selectedFolders,
          ...ingestionSettings
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentJob({ id: data.job_id, status: "processing" });
        setActiveTab("jobs");
        await loadRecentJobs();
      } else {
        const error = await response.json();
        alert(`Failed to start ingestion: ${error.detail}`);
      }
    } catch (error) {
      console.error("Failed to start ingestion:", error);
      alert("Failed to start ingestion");
    } finally {
      setIsLoading(false);
    }
  };

  const checkJobStatus = async (jobId) => {
    try {
      const response = await fetch(`${API_BASE}/jobs/${jobId}`);
      if (response.ok) {
        const data = await response.json();
        setCurrentJob(data);
        
        if (data.status === "completed" || data.status === "failed") {
          await loadRecentJobs();
          await loadDocuments();
          if (data.status === "completed") {
            setActiveTab("documents");
          }
        }
      }
    } catch (error) {
      console.error("Failed to check job status:", error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "completed": return <CheckCircle className="w-4 h-4 text-green-400" />;
      case "failed": return <XCircle className="w-4 h-4 text-red-400" />;
      case "processing": return <Clock className="w-4 h-4 text-blue-400 animate-spin" />;
      default: return <Clock className="w-4 h-4 text-card-secondary" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const FolderPermissionCard = ({ permission }) => {
    const scanResult = scanResults[permission.folder_path];
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-border/30"
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary/20 rounded-lg">
              <Folder className="w-5 h-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-foreground truncate">
                {permission.folder_path.split('/').pop() || permission.folder_path}
              </h3>
              <p className="text-xs text-card-secondary truncate">
                {permission.folder_path}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedFolders.includes(permission.folder_path)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedFolders(prev => [...prev, permission.folder_path]);
                  } else {
                    setSelectedFolders(prev => prev.filter(p => p !== permission.folder_path));
                  }
                }}
                className="rounded border-border"
              />
              <span className="text-sm text-foreground">Select</span>
            </label>
          </div>
        </div>

        {scanResult && (
          <div className="bg-background/50 rounded-lg p-3 mb-3">
            <div className="grid grid-cols-3 gap-3 text-sm">
              <div className="text-center">
                <div className="text-xs text-card-secondary">Files</div>
                <div className="font-semibold text-foreground">{scanResult.processable_files}</div>
              </div>
              <div className="text-center">
                <div className="text-xs text-card-secondary">Size</div>
                <div className="font-semibold text-foreground">{formatFileSize(scanResult.total_size)}</div>
              </div>
              <div className="text-center">
                <div className="text-xs text-card-secondary">Types</div>
                <div className="font-semibold text-foreground">{Object.keys(scanResult.file_types).length}</div>
              </div>
            </div>
          </div>
        )}

        <div className="flex items-center space-x-2">
          <button
            onClick={() => scanFolder(permission.folder_path)}
            disabled={isLoading}
            className="flex-1 px-3 py-2 bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors text-sm"
          >
            <Search className="w-4 h-4 mr-2 inline" />
            {scanResult ? "Re-scan" : "Scan"}
          </button>
          
          {scanResult && (
            <button
              onClick={() => setActiveTab("scan")}
              className="px-3 py-2 border border-border text-card-secondary rounded-lg hover:bg-card/50 transition-colors text-sm"
            >
              <Eye className="w-4 h-4" />
            </button>
          )}
        </div>
      </motion.div>
    );
  };

  const JobCard = ({ job }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-border/30"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-3">
          {getStatusIcon(job.status)}
          <div>
            <h3 className="font-semibold text-foreground capitalize">{job.job_type}</h3>
            <p className="text-xs text-card-secondary">
              {job.folder_path && job.folder_path.split('/').pop()}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-sm font-semibold text-foreground">
            {job.processed_files || 0}/{job.total_files || 0}
          </div>
          <div className="text-xs text-card-secondary">files</div>
        </div>
      </div>

      {job.status === "processing" && (
        <div className="mb-3">
          <div className="flex items-center justify-between text-sm mb-1">
            <span className="text-card-secondary">Progress</span>
            <span className="text-foreground">{(job.progress || 0).toFixed(1)}%</span>
          </div>
          <div className="w-full bg-background rounded-full h-2">
            <motion.div
              className="bg-primary h-2 rounded-full"
              style={{ width: `${job.progress || 0}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      )}

      {job.error_message && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-2 mb-3">
          <p className="text-xs text-red-400">{job.error_message}</p>
        </div>
      )}

      <div className="text-xs text-card-secondary">
        Started: {job.started_at ? new Date(job.started_at).toLocaleString() : "Not started"}
      </div>
    </motion.div>
  );

  const DocumentCard = ({ document }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.01 }}
      onClick={() => setSelectedDocument(document)}
      className="bg-card/50 backdrop-blur-sm rounded-lg p-4 border border-border/30 hover:border-primary/50 cursor-pointer transition-all"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <div className="p-2 bg-blue-500/20 rounded-lg">
            <FileText className="w-4 h-4 text-blue-400" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-foreground truncate">{document.title}</h3>
            <p className="text-xs text-card-secondary truncate">{document.file_path}</p>
          </div>
        </div>
        
        <div className="text-right ml-3">
          <div className="text-sm font-semibold text-foreground">
            {document.total_chunks || 0}
          </div>
          <div className="text-xs text-card-secondary">chunks</div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-xs">
        <div className="text-center">
          <div className="text-card-secondary">Size</div>
          <div className="font-medium text-foreground">{formatFileSize(document.file_size)}</div>
        </div>
        <div className="text-center">
          <div className="text-card-secondary">Type</div>
          <div className="font-medium text-foreground uppercase">{document.file_type}</div>
        </div>
        <div className="text-center">
          <div className="text-card-secondary">Quality</div>
          <div className="font-medium text-foreground">
            {document.avg_quality_score ? (document.avg_quality_score * 100).toFixed(0) + '%' : 'N/A'}
          </div>
        </div>
        <div className="text-center">
          <div className="text-card-secondary">Levels</div>
          <div className="font-medium text-foreground">{document.max_summary_level || 0}</div>
        </div>
      </div>

      <div className="text-xs text-card-secondary mt-2">
        Modified: {new Date(document.file_modified_at).toLocaleDateString()}
      </div>
    </motion.div>
  );

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-indigo-900/20">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-border/30">
        <div>
          <h1 className="text-2xl font-bold text-foreground mb-2 flex items-center">
            <HardDrive className="w-6 h-6 mr-3 text-blue-400" />
            Filesystem Ingestion
          </h1>
          <p className="text-card-secondary">
            Import documents from your filesystem with hierarchical embeddings
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            onClick={() => {
              loadFolderPermissions();
              loadRecentJobs();
              loadDocuments();
            }}
            className="px-4 py-2 border border-border text-card-secondary rounded-lg hover:bg-card/50 transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </motion.button>
          
          {selectedFolders.length > 0 && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              onClick={startIngestion}
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Starting...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Ingest {selectedFolders.length} Folder{selectedFolders.length > 1 ? 's' : ''}</span>
                </>
              )}
            </motion.button>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex items-center space-x-1 p-4 border-b border-border/20">
        {[
          { id: "folders", label: "Folders", icon: Folder },
          { id: "scan", label: "Scan Results", icon: Search },
          { id: "jobs", label: "Jobs", icon: Activity },
          { id: "documents", label: "Documents", icon: Database },
          { id: "settings", label: "Settings", icon: Settings }
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                activeTab === tab.id
                  ? "bg-primary text-primary-foreground"
                  : "text-card-secondary hover:text-foreground hover:bg-card/50"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === "folders" && (
          <div className="space-y-6">
            {/* Add Folder */}
            <div className="bg-card/30 backdrop-blur-sm rounded-lg p-6 border border-border/20">
              <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
                <Plus className="w-5 h-5 mr-2 text-green-400" />
                Add Folder Permission
              </h3>
              
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={folderInput}
                  onChange={(e) => setFolderInput(e.target.value)}
                  placeholder="/path/to/your/documents"
                  className="flex-1 px-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
                />
                <button
                  onClick={addFolderPermission}
                  disabled={!folderInput.trim()}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  Add Folder
                </button>
              </div>
              
              <p className="text-xs text-card-secondary mt-2">
                Enter the absolute path to a folder you want to make available for document ingestion.
              </p>
            </div>

            {/* Folder List */}
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-4">
                Available Folders ({folderPermissions.length})
              </h3>
              
              {folderPermissions.length === 0 ? (
                <div className="text-center py-12">
                  <Folder className="w-16 h-16 text-card-secondary mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-foreground mb-2">No folders configured</h3>
                  <p className="text-card-secondary">Add folder permissions to get started with document ingestion</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {folderPermissions.map((permission) => (
                    <FolderPermissionCard key={permission.folder_path} permission={permission} />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "scan" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-foreground">Scan Results</h3>
            
            {Object.keys(scanResults).length === 0 ? (
              <div className="text-center py-12">
                <Search className="w-16 h-16 text-card-secondary mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2">No scan results</h3>
                <p className="text-card-secondary">Scan folders to see their contents before ingestion</p>
              </div>
            ) : (
              Object.entries(scanResults).map(([folderPath, result]) => (
                <div key={folderPath} className="bg-card/30 backdrop-blur-sm rounded-lg p-6 border border-border/20">
                  <h4 className="text-lg font-semibold text-foreground mb-4">{folderPath}</h4>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-primary">{result.processable_files}</div>
                      <div className="text-sm text-card-secondary">Processable Files</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-400">{formatFileSize(result.total_size)}</div>
                      <div className="text-sm text-card-secondary">Total Size</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">{Object.keys(result.file_types).length}</div>
                      <div className="text-sm text-card-secondary">File Types</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-400">{result.preview_files.length}</div>
                      <div className="text-sm text-card-secondary">Preview Files</div>
                    </div>
                  </div>

                  {result.preview_files.length > 0 && (
                    <div>
                      <h5 className="font-semibold text-foreground mb-3">Preview Files</h5>
                      <div className="space-y-2">
                        {result.preview_files.slice(0, 5).map((file, index) => (
                          <div key={index} className="bg-background/50 rounded-lg p-3 text-sm">
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-foreground">{file.title}</span>
                              <span className="text-card-secondary">{formatFileSize(file.file_size)}</span>
                            </div>
                            <div className="text-xs text-card-secondary mt-1 truncate">{file.file_path}</div>
                            {file.content_preview && (
                              <div className="text-xs text-card-secondary mt-2 bg-background/50 rounded p-2">
                                {file.content_preview.substring(0, 100)}...
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "jobs" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-foreground">Processing Jobs</h3>
            
            {currentJob && currentJob.status === "processing" && (
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                  <span className="text-blue-400 font-semibold">Active Job in Progress</span>
                </div>
                <JobCard job={currentJob} />
              </div>
            )}
            
            {ingestionJobs.length === 0 ? (
              <div className="text-center py-12">
                <Activity className="w-16 h-16 text-card-secondary mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2">No jobs yet</h3>
                <p className="text-card-secondary">Start an ingestion job to see progress here</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {ingestionJobs.map((job) => (
                  <JobCard key={job.id} job={job} />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "documents" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-foreground">Ingested Documents ({documents.length})</h3>
            
            {documents.length === 0 ? (
              <div className="text-center py-12">
                <Database className="w-16 h-16 text-card-secondary mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-foreground mb-2">No documents ingested</h3>
                <p className="text-card-secondary">Complete an ingestion job to see documents here</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {documents.map((document) => (
                  <DocumentCard key={document.id} document={document} />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "settings" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-foreground">Ingestion Settings</h3>
            
            <div className="bg-card/30 backdrop-blur-sm rounded-lg p-6 border border-border/20">
              <div className="space-y-6">
                {/* File Types */}
                <div>
                  <h4 className="font-semibold text-foreground mb-3">File Types to Process</h4>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
                    {["txt", "md", "py", "js", "json", "yaml", "xml", "html", "css", "sql", "pdf", "odt"].map((type) => (
                      <label key={type} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={ingestionSettings.file_types.includes(type)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setIngestionSettings(prev => ({
                                ...prev,
                                file_types: [...prev.file_types, type]
                              }));
                            } else {
                              setIngestionSettings(prev => ({
                                ...prev,
                                file_types: prev.file_types.filter(t => t !== type)
                              }));
                            }
                          }}
                          className="rounded border-border"
                        />
                        <span className="text-sm text-foreground uppercase">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Chunking Settings */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Chunk Size: {ingestionSettings.chunk_size}
                    </label>
                    <input
                      type="range"
                      min="500"
                      max="2000"
                      step="100"
                      value={ingestionSettings.chunk_size}
                      onChange={(e) => setIngestionSettings(prev => ({
                        ...prev,
                        chunk_size: parseInt(e.target.value)
                      }))}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Overlap Size: {ingestionSettings.overlap_size}
                    </label>
                    <input
                      type="range"
                      min="50"
                      max="500"
                      step="50"
                      value={ingestionSettings.overlap_size}
                      onChange={(e) => setIngestionSettings(prev => ({
                        ...prev,
                        overlap_size: parseInt(e.target.value)
                      }))}
                      className="w-full"
                    />
                  </div>
                </div>

                {/* Summary Settings */}
                <div className="space-y-4">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={ingestionSettings.generate_summaries}
                      onChange={(e) => setIngestionSettings(prev => ({
                        ...prev,
                        generate_summaries: e.target.checked
                      }))}
                      className="rounded border-border"
                    />
                    <span className="text-sm font-medium text-foreground">Generate Hierarchical Summaries</span>
                  </label>
                  
                  {ingestionSettings.generate_summaries && (
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-2">
                        Max Summary Levels: {ingestionSettings.max_summary_levels}
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="5"
                        step="1"
                        value={ingestionSettings.max_summary_levels}
                        onChange={(e) => setIngestionSettings(prev => ({
                          ...prev,
                          max_summary_levels: parseInt(e.target.value)
                        }))}
                        className="w-full"
                      />
                    </div>
                  )}
                </div>

                {/* Processing Options */}
                <div>
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={ingestionSettings.force_reprocess}
                      onChange={(e) => setIngestionSettings(prev => ({
                        ...prev,
                        force_reprocess: e.target.checked
                      }))}
                      className="rounded border-border"
                    />
                    <span className="text-sm font-medium text-foreground">Force Reprocess Existing Files</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FilesystemIngestion;