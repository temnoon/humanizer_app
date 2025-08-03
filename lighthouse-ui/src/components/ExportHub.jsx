import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Download,
  Upload,
  FileText,
  BookOpen,
  MessageCircle,
  Share2,
  Archive,
  ExternalLink,
  Settings,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  Copy,
  Eye,
  Filter,
  Search,
  Calendar,
  Tag,
  Star,
  Zap,
  Database,
  Globe,
  File,
  Image,
  Video,
  Music,
  Code,
  Hash,
  Users,
  Layers,
  Target,
  Workflow
} from "lucide-react";

const ExportHub = ({ onNavigate }) => {
  const [selectedBooks, setSelectedBooks] = useState([]);
  const [availableBooks, setAvailableBooks] = useState([]);
  const [availableContent, setAvailableContent] = useState([]);
  const [exportHistory, setExportHistory] = useState([]);
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState("joplin");
  const [exportOptions, setExportOptions] = useState({
    includeImages: true,
    includeMetadata: true,
    preserveFormatting: true,
    generateToc: true,
    compressOutput: false
  });
  const [activeExportType, setActiveExportType] = useState("books"); // books, conversations, insights, custom
  const [searchTerm, setSearchTerm] = useState("");
  const [qualityFilter, setQualityFilter] = useState(0.5);

  useEffect(() => {
    fetchAvailableBooks();
    fetchAvailableContent();
    fetchExportHistory();
  }, []);

  const fetchAvailableBooks = async () => {
    try {
      const response = await fetch('http://localhost:8100/api/books/list');
      if (response.ok) {
        const data = await response.json();
        setAvailableBooks(data.books || []);
      }
    } catch (error) {
      console.error('Failed to fetch books:', error);
      // Fallback with sample data
      setAvailableBooks([
        {
          id: "book_1",
          title: "Consciousness and Computing",
          chapters: 8,
          words: 12500,
          quality_score: 0.85,
          created_at: "2025-08-01T10:00:00Z",
          tags: ["consciousness", "ai", "philosophy"]
        },
        {
          id: "book_2", 
          title: "Quantum Narratives",
          chapters: 6,
          words: 9800,
          quality_score: 0.78,
          created_at: "2025-08-01T15:30:00Z",
          tags: ["quantum", "storytelling", "physics"]
        }
      ]);
    }
  };

  const fetchAvailableContent = async () => {
    try {
      const response = await fetch('http://localhost:8100/api/archive/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: "",
          limit: 50,
          min_quality: qualityFilter
        })
      });
      if (response.ok) {
        const data = await response.json();
        setAvailableContent(data.results || []);
      }
    } catch (error) {
      console.error('Failed to fetch content:', error);
      // Fallback with sample data
      setAvailableContent([
        {
          id: "conv_1",
          title: "Discussion on AI Ethics",
          type: "conversation",
          quality_score: 0.82,
          word_count: 2500,
          created_at: "2025-08-01T09:15:00Z",
          tags: ["ethics", "ai", "discussion"]
        },
        {
          id: "insight_1",
          title: "Emergent Properties in Complex Systems",
          type: "insight",
          quality_score: 0.91,
          word_count: 800,
          created_at: "2025-08-01T14:20:00Z",
          tags: ["complexity", "emergence", "systems"]
        }
      ]);
    }
  };

  const fetchExportHistory = async () => {
    // Placeholder for export history from API
    setExportHistory([
      {
        id: "export_1",
        format: "joplin",
        content_type: "book",
        title: "Consciousness and Computing",
        status: "completed",
        created_at: "2025-08-01T16:45:00Z",
        file_size: "2.3 MB",
        download_url: "/exports/consciousness_computing.jex"
      },
      {
        id: "export_2",
        format: "discourse",
        content_type: "conversations",
        title: "AI Ethics Discussions (5 conversations)",
        status: "completed", 
        created_at: "2025-08-01T12:30:00Z",
        file_size: "1.8 MB",
        download_url: "/exports/ai_ethics_discourse.json"
      }
    ]);
  };

  const exportToJoplin = async (contentIds) => {
    setIsExporting(true);
    try {
      const response = await fetch('http://localhost:8100/api/export/joplin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_ids: contentIds,
          options: exportOptions
        })
      });

      if (response.ok) {
        const result = await response.json();
        // Add to export history
        const newExport = {
          id: `export_${Date.now()}`,
          format: "joplin",
          content_type: activeExportType,
          title: `Export ${new Date().toLocaleString()}`,
          status: "completed",
          created_at: new Date().toISOString(),
          file_size: result.file_size || "Unknown",
          download_url: result.download_url
        };
        setExportHistory([newExport, ...exportHistory]);
        
        // Trigger download
        if (result.download_url) {
          const a = document.createElement('a');
          a.href = result.download_url;
          a.download = result.filename || 'export.jex';
          a.click();
        }
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Joplin export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const exportToDiscourse = async (contentIds) => {
    setIsExporting(true);
    try {
      const response = await fetch('http://localhost:8100/api/export/discourse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_ids: contentIds,
          options: exportOptions
        })
      });

      if (response.ok) {
        const result = await response.json();
        // Handle Discourse export result
        console.log('Discourse export completed:', result);
        alert(`Exported ${contentIds.length} items to Discourse format`);
      }
    } catch (error) {
      console.error('Discourse export failed:', error);
      alert('Discourse export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const exportToWritebook = async (contentIds) => {
    setIsExporting(true);
    try {
      const response = await fetch('http://localhost:8100/api/export/writebook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_ids: contentIds,
          options: exportOptions
        })
      });

      if (response.ok) {
        const result = await response.json();
        // Handle Writebook export result
        console.log('Writebook export completed:', result);
        alert(`Exported ${contentIds.length} items to Writebook format`);
      }
    } catch (error) {
      console.error('Writebook export failed:', error);
      alert('Writebook export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleExport = () => {
    const selectedIds = activeExportType === "books" ? selectedBooks : 
                       availableContent.filter(item => selectedBooks.includes(item.id)).map(item => item.id);
    
    if (selectedIds.length === 0) {
      alert("Please select content to export");
      return;
    }

    switch (exportFormat) {
      case "joplin":
        exportToJoplin(selectedIds);
        break;
      case "discourse":
        exportToDiscourse(selectedIds);
        break;
      case "writebook":
        exportToWritebook(selectedIds);
        break;
      default:
        alert("Please select an export format");
    }
  };

  const filteredBooks = availableBooks.filter(book => 
    book.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
    book.quality_score >= qualityFilter
  );

  const filteredContent = availableContent.filter(item =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
    item.quality_score >= qualityFilter
  );

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-400" />;
      case 'processing': return <Loader2 className="w-4 h-4 animate-spin text-blue-400" />;
      default: return <Clock className="w-4 h-4 text-card-secondary" />;
    }
  };

  const getFormatIcon = (format) => {
    switch (format) {
      case 'joplin': return <BookOpen className="w-5 h-5 text-blue-400" />;
      case 'discourse': return <MessageCircle className="w-5 h-5 text-green-400" />;
      case 'writebook': return <FileText className="w-5 h-5 text-purple-400" />;
      case 'pdf': return <File className="w-5 h-5 text-red-400" />;
      default: return <Archive className="w-5 h-5 text-card-secondary" />;
    }
  };

  const ExportFormatCard = ({ format, title, description, icon: Icon, available = true }) => (
    <motion.div
      whileHover={{ scale: available ? 1.02 : 1 }}
      onClick={() => available && setExportFormat(format)}
      className={`p-4 rounded-lg border transition-all cursor-pointer ${
        exportFormat === format
          ? "border-primary bg-primary/10"
          : available
          ? "border-border/30 hover:border-primary/50 bg-card/30"
          : "border-border/20 bg-card/10 opacity-50 cursor-not-allowed"
      }`}
    >
      <div className="flex items-center space-x-3">
        <Icon className={`w-6 h-6 ${
          exportFormat === format ? "text-primary" : "text-card-secondary"
        }`} />
        <div>
          <h3 className="font-medium text-foreground">{title}</h3>
          <p className="text-sm text-card-secondary">{description}</p>
          {!available && (
            <span className="text-xs text-yellow-400">Coming Soon</span>
          )}
        </div>
      </div>
    </motion.div>
  );

  const ContentCard = ({ item, isSelected, onToggle }) => (
    <motion.div
      whileHover={{ scale: 1.01 }}
      onClick={() => onToggle(item.id)}
      className={`p-4 rounded-lg border cursor-pointer transition-all ${
        isSelected
          ? "border-primary bg-primary/10"
          : "border-border/30 hover:border-primary/50 bg-card/30"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-medium text-foreground mb-1">{item.title}</h3>
          <div className="flex items-center space-x-4 text-sm text-card-secondary">
            <span className="capitalize">{item.type || "book"}</span>
            <span>{item.chapters ? `${item.chapters} chapters` : `${item.word_count} words`}</span>
            <span>Quality: {(item.quality_score * 100).toFixed(0)}%</span>
          </div>
          {item.tags && (
            <div className="flex flex-wrap gap-1 mt-2">
              {item.tags.slice(0, 3).map((tag, index) => (
                <span key={index} className="px-2 py-1 bg-primary/20 text-primary rounded-full text-xs">
                  {tag}
                </span>
              ))}
              {item.tags.length > 3 && (
                <span className="px-2 py-1 bg-card/50 text-card-secondary rounded-full text-xs">
                  +{item.tags.length - 3}
                </span>
              )}
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <Star className={`w-4 h-4 ${item.quality_score > 0.8 ? "text-yellow-400" : "text-card-secondary"}`} />
          {isSelected && <CheckCircle className="w-4 h-4 text-primary" />}
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground mb-2 flex items-center">
            <Download className="w-6 h-6 mr-3 text-green-400" />
            Export Hub
          </h1>
          <p className="text-card-secondary">
            Export your content to Joplin, Discourse, Writebook and other formats
          </p>
        </div>
        
        <div className="flex space-x-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            onClick={() => setSelectedBooks([])}
            className="px-4 py-2 border border-border text-card-secondary rounded-lg hover:bg-card/50 transition-colors"
          >
            Clear Selection
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            onClick={handleExport}
            disabled={selectedBooks.length === 0 || isExporting}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isExporting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Exporting...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Export ({selectedBooks.length})</span>
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* Content Type Selection */}
      <div className="flex space-x-1 p-1 bg-card/30 rounded-lg border border-border/30">
        {[
          { id: "books", label: "Books", icon: BookOpen, desc: "Generated books from insights" },
          { id: "conversations", label: "Conversations", icon: MessageCircle, desc: "Archived conversations" },
          { id: "insights", label: "Insights", icon: Zap, desc: "Extracted insights and gems" },
          { id: "custom", label: "Custom", icon: Layers, desc: "Custom content selection" }
        ].map((type) => {
          const Icon = type.icon;
          return (
            <motion.button
              key={type.id}
              whileHover={{ scale: 1.02 }}
              onClick={() => setActiveExportType(type.id)}
              className={`flex-1 flex items-center justify-center space-x-2 px-4 py-3 rounded-lg transition-all ${
                activeExportType === type.id
                  ? "bg-primary text-primary-foreground shadow-lg"
                  : "text-card-secondary hover:text-foreground hover:bg-card/50"
              }`}
              title={type.desc}
            >
              <Icon className="w-4 h-4" />
              <span className="font-medium">{type.label}</span>
            </motion.button>
          );
        })}
      </div>

      {/* Export Format Selection */}
      <div className="bg-card/30 backdrop-blur-sm rounded-lg p-6 border border-border/30">
        <h3 className="text-lg font-semibold text-foreground mb-4">Export Format</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ExportFormatCard
            format="joplin"
            title="Joplin Notes"
            description="Export as .jex file for Joplin import"
            icon={BookOpen}
            available={true}
          />
          <ExportFormatCard
            format="discourse"
            title="Discourse Forum"
            description="Export as Discourse-compatible JSON"
            icon={MessageCircle}
            available={true}
          />
          <ExportFormatCard
            format="writebook"
            title="Writebook"
            description="Export as Writebook-compatible format"
            icon={FileText}
            available={true}
          />
        </div>
      </div>

      {/* Export Options */}
      {exportFormat && (
        <div className="bg-card/30 backdrop-blur-sm rounded-lg p-6 border border-border/30">
          <h3 className="text-lg font-semibold text-foreground mb-4">Export Options</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(exportOptions).map(([key, value]) => (
              <label key={key} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={value}
                  onChange={(e) => setExportOptions({
                    ...exportOptions,
                    [key]: e.target.checked
                  })}
                  className="rounded border-border"
                />
                <span className="text-sm text-foreground capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-card/30 backdrop-blur-sm rounded-lg p-4 border border-border/30">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-card-secondary" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search content..."
                className="w-full pl-10 pr-4 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-card-secondary" />
            <span className="text-sm text-card-secondary">Quality:</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={qualityFilter}
              onChange={(e) => setQualityFilter(parseFloat(e.target.value))}
              className="w-20"
            />
            <span className="text-sm text-foreground w-8">{(qualityFilter * 100).toFixed(0)}%</span>
          </div>
        </div>
      </div>

      {/* Content Selection */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-foreground">
            Select {activeExportType === "books" ? "Books" : "Content"} to Export
          </h3>
          <div className="flex space-x-2">
            <button
              onClick={() => {
                const items = activeExportType === "books" ? filteredBooks : filteredContent;
                setSelectedBooks(items.map(item => item.id));
              }}
              className="text-sm text-primary hover:underline"
            >
              Select All
            </button>
            <button
              onClick={() => setSelectedBooks([])}
              className="text-sm text-card-secondary hover:underline"
            >
              Clear All
            </button>
          </div>
        </div>

        <div className="grid gap-4">
          {(activeExportType === "books" ? filteredBooks : filteredContent).map(item => (
            <ContentCard
              key={item.id}
              item={item}
              isSelected={selectedBooks.includes(item.id)}
              onToggle={(id) => {
                setSelectedBooks(prev =>
                  prev.includes(id)
                    ? prev.filter(i => i !== id)
                    : [...prev, id]
                );
              }}
            />
          ))}
        </div>
      </div>

      {/* Export History */}
      <div className="bg-card/20 backdrop-blur-sm rounded-lg p-6 border border-border/20">
        <h3 className="text-lg font-semibold text-foreground mb-4">Export History</h3>
        <div className="space-y-3">
          {exportHistory.map(exportItem => (
            <div key={exportItem.id} className="flex items-center justify-between p-3 bg-background/50 rounded-lg">
              <div className="flex items-center space-x-3">
                {getFormatIcon(exportItem.format)}
                <div>
                  <div className="font-medium text-foreground">{exportItem.title}</div>
                  <div className="text-sm text-card-secondary">
                    {new Date(exportItem.created_at).toLocaleString()} • {exportItem.file_size}
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(exportItem.status)}
                {exportItem.download_url && exportItem.status === 'completed' && (
                  <button
                    onClick={() => window.open(exportItem.download_url, '_blank')}
                    className="p-2 hover:bg-card rounded-lg transition-colors"
                    title="Download"
                  >
                    <Download className="w-4 h-4 text-card-secondary" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ExportHub;