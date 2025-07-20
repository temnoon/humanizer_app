import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Layers,
  Plus,
  Search,
  Save,
  Edit3,
  Trash2,
  Eye,
  Zap,
  Sparkles,
  Users,
  Globe,
  Palette,
  ArrowRight,
  Loader2,
  ChevronDown,
  ChevronRight,
  Tag,
  Hash,
  Type,
  MessageSquare,
  Download,
  Upload,
  Copy,
  Check,
  X,
  BookOpen,
  Target,
  Brain,
  Languages,
  Wand2,
  Beaker,
  FileText,
  GitBranch,
  Microscope
} from "lucide-react";
import { useAttributes } from "../contexts/AttributeContext";

const AttributeStudio = () => {
  const {
    attributes,
    addAttribute,
    updateAttribute,
    deleteAttribute,
    searchAttributes,
    getAttributesByType,
    exportAttributes,
    importAttributes
  } = useAttributes();

  const [inputText, setInputText] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [extractedAttributes, setExtractedAttributes] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [editingAttribute, setEditingAttribute] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedAttribute, setSelectedAttribute] = useState(null);
  const [showUsageModal, setShowUsageModal] = useState(false);
  const [showAdvancedPanel, setShowAdvancedPanel] = useState(false);

  // Advanced attribute generation state
  const [advancedConfig, setAdvancedConfig] = useState({
    targetNamespace: "",
    negativeScope: ["Earth", "human", "America", "Europe", "society"],
    includeNoeticAnalysis: true,
    sophisticationLevel: 3
  });
  const [isAdvancedProcessing, setIsAdvancedProcessing] = useState(false);
  const [batchJobs, setBatchJobs] = useState([]);
  const [showBatchModal, setShowBatchModal] = useState(false);

  // Linguistic transformation state
  const [linguisticMode, setLinguisticMode] = useState('basic'); // 'basic' or 'linguistic'
  const [manifestData, setManifestData] = useState(null);
  const [isInferringManifest, setIsInferringManifest] = useState(false);
  const [examples, setExamples] = useState({
    original: [],
    transformed: []
  });
  const [showManifestModal, setShowManifestModal] = useState(false);
  const [showPhonotacticsModal, setShowPhonotacticsModal] = useState(false);
  const [phonotacticsData, setPhonotacticsData] = useState(null);
  const [generatedNames, setGeneratedNames] = useState([]);
  const [showQuickExtractModal, setShowQuickExtractModal] = useState(false);
  const [quickExtractType, setQuickExtractType] = useState('persona');
  const [quickExtractName, setQuickExtractName] = useState('');

  // Quick Extract function
  const handleQuickExtract = async () => {
    if (!inputText.trim() || !quickExtractName.trim()) return;
    
    setIsAnalyzing(true);
    
    try {
      // Create a targeted attribute based on the selected type
      const extractedContent = await extractSpecificAttribute(inputText, quickExtractType);
      
      const newAttribute = {
        name: quickExtractName,
        type: quickExtractType,
        description: `${quickExtractType.charAt(0).toUpperCase() + quickExtractType.slice(1)} extracted from text`,
        content: extractedContent,
        tags: [`quick-extract`, quickExtractType]
      };
      
      await addAttribute(newAttribute);
      
      // Reset form
      setQuickExtractName('');
      setShowQuickExtractModal(false);
      
    } catch (error) {
      console.error('Failed to extract attribute:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Helper function to extract specific attribute type
  const extractSpecificAttribute = async (text, type) => {
    try {
      const response = await fetch(`http://127.0.0.1:8100/api/linguistic/inference/${type}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, include_stylometrics: true })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (type === 'persona') {
          return JSON.stringify(data.persona, null, 2);
        } else if (type === 'style') {
          return JSON.stringify(data.style, null, 2);
        } else {
          // For namespace or other types, use general analysis
          const analysisResponse = await fetch('http://127.0.0.1:8100/api/linguistic/analysis/stylometrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, include_stylometrics: true })
          });
          
          if (analysisResponse.ok) {
            const analysisData = await analysisResponse.json();
            return JSON.stringify(analysisData.analysis, null, 2);
          }
        }
      }
      
      // Fallback to basic text analysis
      return await analyzeText(text, type);
      
    } catch (error) {
      console.error('API extraction failed, using fallback:', error);
      return await analyzeText(text, type);
    }
  };

  // New attribute form
  const [newAttribute, setNewAttribute] = useState({
    name: "",
    type: "persona",
    description: "",
    content: "",
    tags: []
  });

  // Linguistic transformation functions
  const inferManifestFromExamples = async () => {
    if (examples.original.length === 0 || examples.transformed.length === 0) return;
    
    setIsInferringManifest(true);
    
    try {
      const response = await fetch('http://127.0.0.1:8100/api/linguistic/manifests/create-from-examples', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_texts: examples.original,
          transformed_texts: examples.transformed,
          manifest_id: `manifest_${Date.now()}`,
          description: `Inferred from ${examples.transformed.length} examples`
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setManifestData(data.manifest);
        setShowManifestModal(true);
      }
    } catch (error) {
      console.error('Failed to infer manifest:', error);
    } finally {
      setIsInferringManifest(false);
    }
  };

  const analyzePhonotactics = async (names) => {
    try {
      const response = await fetch('http://127.0.0.1:8100/api/linguistic/phonotactics/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ names })
      });
      
      if (response.ok) {
        const data = await response.json();
        setPhonotacticsData(data);
        setShowPhonotacticsModal(true);
      }
    } catch (error) {
      console.error('Failed to analyze phonotactics:', error);
    }
  };

  const generateNamesFromManifest = async (manifestId, count = 10) => {
    try {
      const response = await fetch(`http://127.0.0.1:8100/api/linguistic/manifests/${manifestId}/generate-names`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ manifest_id: manifestId, count })
      });
      
      if (response.ok) {
        const data = await response.json();
        setGeneratedNames(data.generated_names);
      }
    } catch (error) {
      console.error('Failed to generate names:', error);
    }
  };

  const analyzeTextStylometrics = async (text) => {
    try {
      const response = await fetch('http://127.0.0.1:8100/api/linguistic/analysis/stylometrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, include_stylometrics: true })
      });
      
      if (response.ok) {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.error('Failed to analyze stylometrics:', error);
      return null;
    }
  };

  const analyzeText = async () => {
    if (!inputText.trim()) return;
    
    setIsAnalyzing(true);
    setExtractedAttributes([]);
    
    try {
      if (linguisticMode === 'linguistic') {
        // Use the new sophisticated linguistic analysis
        const stylometricData = await analyzeTextStylometrics(inputText);
        
        if (stylometricData) {
          const attributes = [];
          
          // Create sophisticated attributes from analysis
          if (stylometricData.inferred_persona) {
            attributes.push({
              id: "temp_persona_" + Date.now(),
              type: "persona",
              name: "Inferred Persona",
              content: JSON.stringify(stylometricData.inferred_persona, null, 2),
              description: `Persona with ${Object.keys(stylometricData.inferred_persona.pronoun_usage).length} pronoun patterns`,
              isEditing: false,
              source: "linguistic_analysis"
            });
          }
          
          if (stylometricData.inferred_style) {
            attributes.push({
              id: "temp_style_" + Date.now(),
              type: "style",
              name: "Inferred Style",
              content: JSON.stringify(stylometricData.inferred_style, null, 2),
              description: `Style with ${stylometricData.inferred_style.avg_sentence_length.toFixed(1)} avg sentence length, formality ${stylometricData.inferred_style.formality_score.toFixed(2)}`,
              isEditing: false,
              source: "linguistic_analysis"
            });
          }
          
          setExtractedAttributes(attributes);
        }
      } else {
        // Use the original basic analysis
        const response = await fetch("/lamish/extract-attributes", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ narrative: inputText })
        });
      
      if (response.ok) {
        const data = await response.json();
        const attributes = [];
        
        // Convert backend response to editable format
        if (data.persona) {
          attributes.push({
            id: "temp_persona_" + Date.now(),
            type: "persona",
            name: data.persona.name || "Extracted Persona",
            description: data.persona.description || "Persona extracted from text analysis",
            content: data.persona.characteristics ? data.persona.characteristics.join(", ") : "",
            tags: data.persona.characteristics || [],
            confidence: 0.85,
            isTemporary: true,
            sourceText: inputText.substring(0, 150) + "..."
          });
        }
        
        if (data.namespace) {
          attributes.push({
            id: "temp_namespace_" + Date.now(),
            type: "namespace",
            name: data.namespace.name || "Extracted Namespace",
            description: data.namespace.description || "Namespace extracted from text analysis",
            content: data.namespace.characteristics ? data.namespace.characteristics.join(", ") : "",
            tags: data.namespace.characteristics || [],
            confidence: 0.78,
            isTemporary: true,
            sourceText: inputText.substring(0, 150) + "..."
          });
        }
        
        if (data.style) {
          attributes.push({
            id: "temp_style_" + Date.now(),
            type: "style",
            name: data.style.name || "Extracted Style",
            description: data.style.description || "Style extracted from text analysis",
            content: data.style.characteristics ? data.style.characteristics.join(", ") : "",
            tags: data.style.characteristics || [],
            confidence: 0.82,
            isTemporary: true,
            sourceText: inputText.substring(0, 150) + "..."
          });
        }
        
        setExtractedAttributes(attributes);
      } else {
        // Fallback with smart analysis
        const mockAnalysis = generateSmartAnalysis(inputText);
        setExtractedAttributes(mockAnalysis);
      }
      }
    } catch (error) {
      console.error("Analysis failed:", error);
      const mockAnalysis = generateSmartAnalysis(inputText);
      setExtractedAttributes(mockAnalysis);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const generateSmartAnalysis = (text) => {
    const words = text.toLowerCase().split(/\s+/);
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const attributes = [];
    
    // Smart persona extraction
    const personaIndicators = ["i", "me", "my", "myself", "think", "believe", "feel", "wonder", "hope", "dream"];
    const hasPersonaMarkers = personaIndicators.some(word => words.includes(word));
    
    if (hasPersonaMarkers || text.includes("person") || text.includes("character")) {
      const personaName = text.includes("scientist") ? "Analytical Researcher" :
                         text.includes("artist") ? "Creative Visionary" :
                         text.includes("teacher") ? "Knowledgeable Educator" :
                         text.includes("writer") ? "Narrative Craftsperson" :
                         hasPersonaMarkers ? "Reflective Individual" : "Thoughtful Observer";
      
      attributes.push({
        id: "temp_persona_" + Date.now(),
        type: "persona",
        name: personaName,
        description: `A persona characterized by ${hasPersonaMarkers ? "personal reflection and" : ""} thoughtful engagement`,
        content: `This persona approaches situations with careful consideration, ${hasPersonaMarkers ? "drawing from personal experience and" : ""} seeking to understand deeper meanings and implications.`,
        tags: hasPersonaMarkers ? ["personal", "reflective", "thoughtful"] : ["observant", "analytical", "considerate"],
        confidence: 0.85,
        isTemporary: true,
        sourceText: text.substring(0, 150) + "..."
      });
    }
    
    // Smart namespace extraction
    const namespaceIndicators = ["world", "reality", "universe", "realm", "dimension", "space", "place", "environment"];
    const hasNamespaceMarkers = namespaceIndicators.some(word => words.includes(word));
    const isSciFi = words.some(w => ["technology", "future", "space", "robot", "ai", "digital"].includes(w));
    const isFantasy = words.some(w => ["magic", "dragon", "spell", "kingdom", "quest", "wizard"].includes(w));
    
    if (hasNamespaceMarkers || isSciFi || isFantasy) {
      const namespaceName = isSciFi ? "Technological Future" :
                           isFantasy ? "Mystical Realm" :
                           hasNamespaceMarkers ? "Conceptual Reality" : "Thoughtful Universe";
      
      attributes.push({
        id: "temp_namespace_" + Date.now(),
        type: "namespace",
        name: namespaceName,
        description: `A ${isSciFi ? "technologically advanced" : isFantasy ? "magically infused" : "conceptually rich"} universe`,
        content: `A reality where ${isSciFi ? "technological innovation drives progress" : isFantasy ? "magical forces shape existence" : "abstract concepts manifest as tangible experiences"} and ideas have real consequence.`,
        tags: isSciFi ? ["technology", "future", "innovation"] : isFantasy ? ["magic", "mystical", "enchanted"] : ["conceptual", "thoughtful", "experiential"],
        confidence: 0.72,
        isTemporary: true,
        sourceText: text.substring(0, 150) + "..."
      });
    }
    
    // Smart style extraction
    const isAnalytical = words.some(w => ["analyze", "examine", "consider", "evaluate", "assess"].includes(w));
    const isPoetic = sentences.some(s => s.length < 50 && s.includes(",")) || text.includes("like") || text.includes("as if");
    const isNarrative = words.some(w => ["story", "tale", "once", "began", "happened", "journey"].includes(w));
    
    if (words.length > 15) {
      const styleName = isAnalytical ? "Analytical Expression" :
                       isPoetic ? "Lyrical Communication" :
                       isNarrative ? "Narrative Flow" : "Clear Communication";
      
      attributes.push({
        id: "temp_style_" + Date.now(),
        type: "style",
        name: styleName,
        description: `${isAnalytical ? "Systematic and methodical" : isPoetic ? "Expressive and metaphorical" : isNarrative ? "Story-driven and engaging" : "Direct and accessible"} communication style`,
        content: `A style that ${isAnalytical ? "breaks down complex ideas into logical components" : isPoetic ? "uses imagery and rhythm to convey meaning" : isNarrative ? "weaves information into compelling stories" : "presents information clearly and effectively"}.`,
        tags: isAnalytical ? ["analytical", "systematic", "methodical"] : isPoetic ? ["lyrical", "expressive", "metaphorical"] : isNarrative ? ["narrative", "engaging", "story-driven"] : ["clear", "direct", "accessible"],
        confidence: 0.78,
        isTemporary: true,
        sourceText: text.substring(0, 150) + "..."
      });
    }
    
    return attributes;
  };

  const startEditingAttribute = (attribute) => {
    setEditingAttribute({
      ...attribute,
      tempName: attribute.name,
      tempDescription: attribute.description,
      tempContent: attribute.content,
      tempTags: [...attribute.tags]
    });
  };

  const saveEditedAttribute = () => {
    if (!editingAttribute) return;
    
    const finalAttribute = {
      name: editingAttribute.tempName,
      type: editingAttribute.type,
      description: editingAttribute.tempDescription,
      content: editingAttribute.tempContent,
      tags: editingAttribute.tempTags,
      source: 'analyzed'
    };

    // Remove from extracted and add to persistent storage
    setExtractedAttributes(prev => prev.filter(a => a.id !== editingAttribute.id));
    addAttribute(finalAttribute);
    setEditingAttribute(null);
  };

  const quickSaveAttribute = (attribute) => {
    const finalAttribute = {
      name: attribute.name,
      type: attribute.type,
      description: attribute.description,
      content: attribute.content,
      tags: attribute.tags,
      source: 'analyzed'
    };

    setExtractedAttributes(prev => prev.filter(a => a.id !== attribute.id));
    addAttribute(finalAttribute);
  };

  const createNewAttribute = () => {
    if (!newAttribute.name.trim()) return;
    
    addAttribute({
      ...newAttribute,
      tags: newAttribute.tags.filter(tag => tag.trim().length > 0),
      source: 'manual'
    });
    
    setNewAttribute({
      name: "",
      type: "persona",
      description: "",
      content: "",
      tags: []
    });
    setShowCreateForm(false);
  };

  // Advanced attribute generation functions
  const generateAdvancedAttributes = async () => {
    if (!inputText.trim()) return;
    
    setIsAdvancedProcessing(true);
    setExtractedAttributes([]);
    
    try {
      const response = await fetch("/api/advanced-attributes/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: inputText,
          target_namespace: advancedConfig.targetNamespace || null,
          negative_scope: advancedConfig.negativeScope,
          include_noetic_analysis: advancedConfig.includeNoeticAnalysis,
          sophistication_level: advancedConfig.sophisticationLevel
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        const convertedAttributes = data.attributes.map(attr => ({
          id: "temp_adv_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9),
          name: attr.name,
          type: attr.type,
          description: attr.description,
          content: attr.content,
          tags: attr.filtered_concepts ? Array.from(attr.filtered_concepts) : [],
          confidence: attr.confidence_score,
          isTemporary: true,
          isAdvanced: true,
          sourceText: inputText.substring(0, 150) + "...",
          proxyMappings: attr.proxy_mappings || {},
          noeticAnalysis: attr.noetic_analysis || null,
          sophisticationLevel: advancedConfig.sophisticationLevel
        }));
        
        setExtractedAttributes(convertedAttributes);
      } else {
        throw new Error("Advanced generation failed");
      }
    } catch (error) {
      console.error("Advanced attribute generation failed:", error);
      // Fall back to regular analysis
      const mockAnalysis = generateSmartAnalysis(inputText);
      setExtractedAttributes(mockAnalysis);
    } finally {
      setIsAdvancedProcessing(false);
    }
  };

  const startBatchContentScraping = async () => {
    try {
      const response = await fetch("/api/advanced-attributes/batch-process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          negative_scope: advancedConfig.negativeScope,
          target_namespace: advancedConfig.targetNamespace || "Filtered Reality",
          max_content_pieces: 20,
          quality_threshold: 0.7
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setBatchJobs(prev => [...prev, {
          id: data.job_id,
          status: data.status,
          startedAt: new Date().toISOString(),
          sources: data.sources
        }]);
        setShowBatchModal(true);
        
        // Poll for job status
        pollBatchJob(data.job_id);
      }
    } catch (error) {
      console.error("Failed to start batch processing:", error);
    }
  };

  const pollBatchJob = async (jobId) => {
    const poll = async () => {
      try {
        const response = await fetch(`/api/advanced-attributes/batch-status/${jobId}`);
        if (response.ok) {
          const status = await response.json();
          setBatchJobs(prev => prev.map(job => 
            job.id === jobId ? { ...job, ...status } : job
          ));
          
          if (status.status === "completed") {
            // Fetch results and add to library
            const resultsResponse = await fetch(`/api/advanced-attributes/batch-results/${jobId}`);
            if (resultsResponse.ok) {
              const results = await resultsResponse.json();
              results.attributes?.forEach(attr => {
                addAttribute({
                  name: attr.name,
                  type: attr.type,
                  description: attr.description,
                  content: attr.content,
                  tags: attr.filtered_concepts || [],
                  source: 'batch_scraped',
                  advancedMetadata: {
                    proxyMappings: attr.proxy_mappings,
                    confidenceScore: attr.confidence_score,
                    sourceMetadata: attr.source_metadata
                  }
                });
              });
            }
          } else if (status.status === "processing") {
            // Continue polling
            setTimeout(poll, 3000);
          }
        }
      } catch (error) {
        console.error("Error polling batch job:", error);
      }
    };
    
    setTimeout(poll, 1000);
  };

  const addNegativeScopeItem = (item) => {
    if (item.trim() && !advancedConfig.negativeScope.includes(item.trim())) {
      setAdvancedConfig(prev => ({
        ...prev,
        negativeScope: [...prev.negativeScope, item.trim()]
      }));
    }
  };

  const removeNegativeScopeItem = (item) => {
    setAdvancedConfig(prev => ({
      ...prev,
      negativeScope: prev.negativeScope.filter(i => i !== item)
    }));
  };

  const handleFileImport = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    importAttributes(file)
      .then(count => {
        alert(`Successfully imported ${count} attributes!`);
      })
      .catch(error => {
        alert(`Import failed: ${error.message}`);
      });
    
    event.target.value = '';
  };

  const addTag = (tags, newTag) => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      return [...tags, newTag.trim()];
    }
    return tags;
  };

  const removeTag = (tags, tagToRemove) => {
    return tags.filter(tag => tag !== tagToRemove);
  };

  const getAttributeIcon = (type) => {
    switch (type) {
      case "persona": return Users;
      case "namespace": return Globe;
      case "style": return Palette;
      default: return Tag;
    }
  };

  const getAttributeColor = (type) => {
    switch (type) {
      case "persona": return "blue";
      case "namespace": return "green";
      case "style": return "purple";
      default: return "gray";
    }
  };

  const getUsageExamples = (type) => {
    switch (type) {
      case "persona":
        return [
          "Transform tab: Use as target persona for narrative transformation",
          "Maieutic tab: Use as dialogue partner for Socratic questioning",
          "Batch tab: Apply to multiple narratives for consistent voice"
        ];
      case "namespace":
        return [
          "Transform tab: Use as target universe for narrative projection",
          "Translation tab: Preserve namespace-specific concepts during translation",
          "Vision tab: Generate images that fit the namespace aesthetic"
        ];
      case "style":
        return [
          "Transform tab: Apply as target style for narrative rewriting",
          "Batch tab: Ensure consistent style across multiple documents",
          "API Console: Use in custom transformation requests"
        ];
      default:
        return ["Use in various transformation contexts"];
    }
  };

  const filteredAttributes = searchQuery.trim() 
    ? searchAttributes(searchQuery)
    : attributes;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Layers className="w-6 h-6 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Attribute Studio
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {attributes.length} saved attributes • Extract, name, save, and use across all tabs
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowCreateForm(true)}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create
            </button>
            <button
              onClick={exportAttributes}
              className="flex items-center gap-2 px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg text-sm font-medium transition-colors"
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
                onChange={handleFileImport}
                className="hidden"
              />
            </label>
          </div>
        </div>
        
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">💡 How to Use Attributes</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
            <div className="flex items-start gap-2">
              <Users className="w-4 h-4 text-blue-600 mt-0.5" />
              <div>
                <div className="font-medium text-blue-800 dark:text-blue-200">Personas</div>
                <div className="text-blue-700 dark:text-blue-300">Use in Transform for voice/perspective</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Globe className="w-4 h-4 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium text-green-800 dark:text-green-200">Namespaces</div>
                <div className="text-green-700 dark:text-green-300">Use in Transform for universe/context</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Palette className="w-4 h-4 text-purple-600 mt-0.5" />
              <div>
                <div className="font-medium text-purple-800 dark:text-purple-200">Styles</div>
                <div className="text-purple-700 dark:text-purple-300">Use in Transform for tone/format</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mode Switcher */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Analysis Mode:</span>
            <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
              <button
                onClick={() => setLinguisticMode('basic')}
                className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                  linguisticMode === 'basic'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <Target className="w-4 h-4 inline mr-1" />
                Basic
              </button>
              <button
                onClick={() => setLinguisticMode('linguistic')}
                className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                  linguisticMode === 'linguistic'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <Microscope className="w-4 h-4 inline mr-1" />
                Linguistic
              </button>
            </div>
          </div>
          
          {linguisticMode === 'linguistic' && (
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowManifestModal(true)}
                className="flex items-center gap-1 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors"
              >
                <Beaker className="w-4 h-4" />
                Manifests
              </button>
              <button
                onClick={() => setShowPhonotacticsModal(true)}
                className="flex items-center gap-1 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors"
              >
                <Languages className="w-4 h-4" />
                Phonotactics
              </button>
            </div>
          )}
        </div>
        
        {linguisticMode === 'linguistic' && (
          <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-start gap-2">
              <GitBranch className="w-4 h-4 text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Linguistic Mode:</strong> Advanced analysis using phonotactic patterns, stylometric features, and manifest inference. 
                Create JSON manifests with quantified parameters for namespace, persona, and style attributes.
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Analysis Panel */}
        <div className="space-y-6">
          {/* Text Analysis */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Analyze & Extract
              </h3>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {inputText.length}/5000 characters
              </div>
            </div>

            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter narrative text to analyze for personas, namespaces, and styles...

Example: 'As a curious scientist exploring the quantum realm, I discovered that reality operates on poetic principles rather than pure logic. The universe speaks in metaphors.'

This would extract:
• Persona: Curious Scientist
• Namespace: Quantum Realm  
• Style: Poetic Scientific"
              className="w-full h-40 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              maxLength={5000}
            />

            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                AI will identify personas, namespaces, and styles from your text
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowAdvancedPanel(!showAdvancedPanel)}
                  className={`inline-flex items-center gap-2 px-3 py-2 ${showAdvancedPanel ? 'bg-purple-600 hover:bg-purple-700' : 'bg-gray-600 hover:bg-gray-700'} text-white rounded-lg text-sm font-medium transition-colors`}
                >
                  <Brain className="w-4 h-4" />
                  Advanced
                </button>
                <button
                  onClick={showAdvancedPanel ? generateAdvancedAttributes : analyzeText}
                  disabled={!inputText.trim() || isAnalyzing || isAdvancedProcessing}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
                >
                  {(isAnalyzing || isAdvancedProcessing) ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      {showAdvancedPanel ? 'Processing...' : 'Analyzing...'}
                    </>
                  ) : (
                    <>
                      {showAdvancedPanel ? <Wand2 className="w-4 h-4" /> : <Zap className="w-4 h-4" />}
                      {showAdvancedPanel ? 'Advanced Generate' : 'Analyze Text'}
                    </>
                  )}
                </button>
                
                {/* Quick Extract Button */}
                <button
                  onClick={() => setShowQuickExtractModal(true)}
                  disabled={!inputText.trim()}
                  className="inline-flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
                  title="Extract a specific named attribute from this text"
                >
                  <Target className="w-4 h-4" />
                  Extract
                </button>
              </div>
            </div>
          </div>

          {/* Advanced Configuration Panel */}
          {showAdvancedPanel && (
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-purple-200 dark:border-purple-700">
              <div className="flex items-center gap-3 mb-4">
                <Brain className="w-5 h-5 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Advanced Attribute Generation
                </h3>
              </div>
              
              <div className="space-y-4">
                {/* Target Namespace */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Target Namespace (Optional)
                  </label>
                  <input
                    value={advancedConfig.targetNamespace}
                    onChange={(e) => setAdvancedConfig(prev => ({...prev, targetNamespace: e.target.value}))}
                    placeholder="e.g., Zephyrian Domain, Crystalline Reality..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                  />
                </div>
                
                {/* Negative Scoping */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Negative Scope (Concepts to Filter Out)
                  </label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {advancedConfig.negativeScope.map((item, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 rounded"
                      >
                        {item}
                        <button
                          onClick={() => removeNegativeScopeItem(item)}
                          className="hover:text-red-600 dark:hover:text-red-400"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <input
                    placeholder="Add concept to filter (e.g., Earth, human, society)"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        addNegativeScopeItem(e.target.value);
                        e.target.value = '';
                      }
                    }}
                  />
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Press Enter to add. These concepts will be replaced with proxy names.
                  </div>
                </div>
                
                {/* Configuration Options */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Sophistication Level
                    </label>
                    <select
                      value={advancedConfig.sophisticationLevel}
                      onChange={(e) => setAdvancedConfig(prev => ({...prev, sophisticationLevel: parseInt(e.target.value)}))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                    >
                      <option value={1}>Basic (Simple attributes)</option>
                      <option value={2}>Moderate (Enhanced details)</option>
                      <option value={3}>Advanced (Rich semantics)</option>
                      <option value={4}>Expert (Complex relationships)</option>
                      <option value={5}>Master (Maximum sophistication)</option>
                    </select>
                  </div>
                  
                  <div className="flex items-center">
                    <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                      <input
                        type="checkbox"
                        checked={advancedConfig.includeNoeticAnalysis}
                        onChange={(e) => setAdvancedConfig(prev => ({...prev, includeNoeticAnalysis: e.target.checked}))}
                        className="rounded border-gray-300 dark:border-gray-600"
                      />
                      Include Noetic Analysis
                    </label>
                  </div>
                </div>
                
                {/* Batch Processing */}
                <div className="border-t border-gray-200 dark:border-gray-600 pt-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      Batch Content Scraping
                    </h4>
                    <button
                      onClick={startBatchContentScraping}
                      className="inline-flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                      <Languages className="w-4 h-4" />
                      Start Batch Job
                    </button>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Scrape high-quality content from philosophical essays, academic papers, and thoughtful blogs to generate filtered attributes.
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Extracted Attributes */}
          {extractedAttributes.length > 0 && (
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Extracted Attributes ({extractedAttributes.length})
              </h3>
              <div className="space-y-4">
                {extractedAttributes.map((attr) => {
                  const Icon = getAttributeIcon(attr.type);
                  const color = getAttributeColor(attr.type);
                  const isEditing = editingAttribute?.id === attr.id;
                  
                  return (
                    <motion.div
                      key={attr.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 bg-white dark:bg-gray-800"
                    >
                      {isEditing ? (
                        <div className="space-y-3">
                          <div className="flex items-center gap-3 mb-3">
                            <Icon className={`w-5 h-5 text-${color}-600`} />
                            <input
                              value={editingAttribute.tempName}
                              onChange={(e) => setEditingAttribute(prev => ({...prev, tempName: e.target.value}))}
                              className="flex-1 px-3 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                              placeholder="Attribute name..."
                            />
                          </div>
                          
                          <textarea
                            value={editingAttribute.tempDescription}
                            onChange={(e) => setEditingAttribute(prev => ({...prev, tempDescription: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                            rows={2}
                            placeholder="Brief description..."
                          />
                          
                          <textarea
                            value={editingAttribute.tempContent}
                            onChange={(e) => setEditingAttribute(prev => ({...prev, tempContent: e.target.value}))}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                            rows={3}
                            placeholder="Detailed content/characteristics..."
                          />
                          
                          <div className="flex items-center justify-between">
                            <div className="flex flex-wrap gap-1">
                              {editingAttribute.tempTags.map((tag, idx) => (
                                <span
                                  key={idx}
                                  className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                                >
                                  {tag}
                                  <button
                                    onClick={() => setEditingAttribute(prev => ({
                                      ...prev,
                                      tempTags: prev.tempTags.filter((_, i) => i !== idx)
                                    }))}
                                    className="hover:text-red-500"
                                  >
                                    <X className="w-3 h-3" />
                                  </button>
                                </span>
                              ))}
                              <input
                                className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded border-none outline-none"
                                placeholder="Add tag..."
                                onKeyPress={(e) => {
                                  if (e.key === 'Enter') {
                                    const newTag = e.target.value.trim();
                                    if (newTag && !editingAttribute.tempTags.includes(newTag)) {
                                      setEditingAttribute(prev => ({
                                        ...prev,
                                        tempTags: [...prev.tempTags, newTag]
                                      }));
                                      e.target.value = '';
                                    }
                                  }
                                }}
                              />
                            </div>
                            
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => setEditingAttribute(null)}
                                className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                              >
                                <X className="w-4 h-4" />
                              </button>
                              <button
                                onClick={saveEditedAttribute}
                                className="flex items-center gap-1 px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm"
                              >
                                <Save className="w-3 h-3" />
                                Save
                              </button>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-3">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-3">
                              <Icon className={`w-5 h-5 text-${color}-600`} />
                              <div>
                                <div className="flex items-center gap-2">
                                  <h4 className="font-medium text-gray-900 dark:text-white">
                                    {attr.name}
                                  </h4>
                                  {attr.isAdvanced && (
                                    <span className="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 rounded">
                                      Advanced
                                    </span>
                                  )}
                                  {attr.sophisticationLevel && (
                                    <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded">
                                      Level {attr.sophisticationLevel}
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  {attr.description}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {attr.confidence && (
                                <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded">
                                  {Math.round(attr.confidence * 100)}% confident
                                </span>
                              )}
                              <button
                                onClick={() => startEditingAttribute(attr)}
                                className="p-1 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded transition-colors"
                                title="Edit before saving"
                              >
                                <Edit3 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => quickSaveAttribute(attr)}
                                className="p-1 text-green-600 hover:bg-green-100 dark:hover:bg-green-900/30 rounded transition-colors"
                                title="Save as-is"
                              >
                                <Save className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                          
                          <div className="text-sm text-gray-700 dark:text-gray-300">
                            {attr.content}
                          </div>
                          
                          {/* Proxy Mappings */}
                          {attr.proxyMappings && Object.keys(attr.proxyMappings).length > 0 && (
                            <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3">
                              <h5 className="font-medium text-orange-900 dark:text-orange-100 mb-2 text-sm">
                                🔄 Proxy Mappings (Filtered Concepts)
                              </h5>
                              <div className="space-y-1">
                                {Object.entries(attr.proxyMappings).map(([original, proxy], idx) => (
                                  <div key={idx} className="text-xs flex items-center gap-2">
                                    <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 rounded">
                                      {original}
                                    </span>
                                    <ArrowRight className="w-3 h-3 text-gray-500" />
                                    <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded">
                                      {proxy}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* Noetic Analysis */}
                          {attr.noeticAnalysis && (
                            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                              <h5 className="font-medium text-blue-900 dark:text-blue-100 mb-2 text-sm">
                                🧠 Consciousness Analysis
                              </h5>
                              <div className="grid grid-cols-2 gap-2 text-xs">
                                <div>
                                  <span className="text-blue-800 dark:text-blue-200">Coherence:</span>
                                  <span className="ml-1 font-mono">{(attr.noeticAnalysis.consciousness_coherence || 0).toFixed(2)}</span>
                                </div>
                                <div>
                                  <span className="text-blue-800 dark:text-blue-200">Clarity:</span>
                                  <span className="ml-1 font-mono">{(attr.noeticAnalysis.intentional_clarity || 0).toFixed(2)}</span>
                                </div>
                                <div className="col-span-2">
                                  <span className="text-blue-800 dark:text-blue-200">Patterns:</span>
                                  <span className="ml-1 font-mono">{attr.noeticAnalysis.pattern_count || 0}</span>
                                </div>
                              </div>
                            </div>
                          )}
                          
                          {attr.tags && attr.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {attr.tags.map((tag, idx) => (
                                <span
                                  key={idx}
                                  className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Attribute Library */}
        <div className="space-y-6">
          {/* Search */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search your attribute library..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          {/* Attribute Stats */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Library Overview</h3>
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Users className="w-4 h-4 text-blue-600" />
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {getAttributesByType('persona').length}
                  </span>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Personas</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Globe className="w-4 h-4 text-green-600" />
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {getAttributesByType('namespace').length}
                  </span>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Namespaces</div>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Palette className="w-4 h-4 text-purple-600" />
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {getAttributesByType('style').length}
                  </span>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Styles</div>
              </div>
            </div>
          </div>

          {/* Saved Attributes */}
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-4 border border-gray-200 dark:border-gray-700 max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Saved Attributes
              </h3>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {filteredAttributes.length} shown
              </span>
            </div>

            <div className="space-y-2">
              {filteredAttributes.map((attr) => {
                const Icon = getAttributeIcon(attr.type);
                const color = getAttributeColor(attr.type);
                
                return (
                  <div key={attr.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <Icon className={`w-4 h-4 text-${color}-600 flex-shrink-0`} />
                        <div className="min-w-0 flex-1">
                          <div className="font-medium text-gray-900 dark:text-white truncate">
                            {attr.name}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {attr.type} • Used {attr.usageCount || 0}x
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-1 flex-shrink-0">
                        <button
                          onClick={() => {
                            setSelectedAttribute(attr);
                            setShowUsageModal(true);
                          }}
                          className="p-1 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded transition-colors"
                          title="View usage info"
                        >
                          <Eye className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => deleteAttribute(attr.id)}
                          className="p-1 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
                      {attr.description}
                    </div>
                    
                    {attr.tags && attr.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {attr.tags.slice(0, 3).map((tag, idx) => (
                          <span
                            key={idx}
                            className="text-xs px-1 py-0.5 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                        {attr.tags.length > 3 && (
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            +{attr.tags.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
              
              {filteredAttributes.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  {searchQuery ? "No attributes match your search" : "No attributes yet. Analyze some text to get started!"}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Create New Attribute Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Create New Attribute
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Name
                </label>
                <input
                  value={newAttribute.name}
                  onChange={(e) => setNewAttribute(prev => ({...prev, name: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="My Custom Attribute"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Type
                </label>
                <select
                  value={newAttribute.type}
                  onChange={(e) => setNewAttribute(prev => ({...prev, type: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="persona">Persona</option>
                  <option value="namespace">Namespace</option>
                  <option value="style">Style</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  value={newAttribute.description}
                  onChange={(e) => setNewAttribute(prev => ({...prev, description: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                  rows={2}
                  placeholder="Brief description..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Content
                </label>
                <textarea
                  value={newAttribute.content}
                  onChange={(e) => setNewAttribute(prev => ({...prev, content: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                  rows={3}
                  placeholder="Detailed content and characteristics..."
                />
              </div>
            </div>
            
            <div className="flex items-center justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={createNewAttribute}
                disabled={!newAttribute.name.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium"
              >
                Create Attribute
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Usage Info Modal */}
      {showUsageModal && selectedAttribute && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-lg mx-4"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                How to Use This Attribute
              </h3>
              <button
                onClick={() => setShowUsageModal(false)}
                className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                {React.createElement(getAttributeIcon(selectedAttribute.type), { 
                  className: `w-5 h-5 text-${getAttributeColor(selectedAttribute.type)}-600` 
                })}
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {selectedAttribute.name}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {selectedAttribute.description}
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  Usage Examples:
                </h4>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  {getUsageExamples(selectedAttribute.type).map((example, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <ArrowRight className="w-4 h-4 mt-0.5 text-blue-500 flex-shrink-0" />
                      <span>{example}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-600">
                Created: {selectedAttribute.created ? new Date(selectedAttribute.created).toLocaleDateString() : 'Unknown'} • 
                Used: {selectedAttribute.usageCount || 0} times
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Batch Job Monitoring Modal */}
      {showBatchModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-2xl mx-4 max-h-96 overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Batch Content Processing Jobs
              </h3>
              <button
                onClick={() => setShowBatchModal(false)}
                className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              {batchJobs.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No batch jobs running
                </div>
              ) : (
                batchJobs.map((job) => (
                  <div key={job.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="font-medium text-gray-900 dark:text-white">
                          Job {job.id}
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${
                          job.status === 'completed' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' :
                          job.status === 'processing' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200' :
                          job.status === 'failed' ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200' :
                          'bg-gray-100 dark:bg-gray-900/30 text-gray-800 dark:text-gray-200'
                        }`}>
                          {job.status}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(job.startedAt).toLocaleTimeString()}
                      </div>
                    </div>
                    
                    {job.status === 'processing' && job.progress_percentage !== undefined && (
                      <div className="mb-2">
                        <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                          <span>Progress</span>
                          <span>{job.progress_percentage}%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${job.progress_percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                    
                    {job.sources && (
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        <span className="font-medium">Sources: </span>
                        {job.sources.join(', ')}
                      </div>
                    )}
                    
                    {job.sources_processed !== undefined && (
                      <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Processed: {job.sources_processed}/{job.total_sources} sources
                        {job.attributes_generated > 0 && (
                          <span className="ml-2">• Generated: {job.attributes_generated} attributes</span>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
              
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded">
                💡 Tip: Batch jobs automatically add generated attributes to your library when complete. 
                Jobs scrape high-quality content and apply negative scoping to create filtered attributes.
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Linguistic Transformation Manifest Modal */}
      {showManifestModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Beaker className="w-6 h-6 text-purple-600" />
                <h2 className="text-xl font-semibold">Linguistic Transformation Manifests</h2>
              </div>
              <button
                onClick={() => setShowManifestModal(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Example Input Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Original Text Examples</label>
                  <textarea
                    placeholder="Enter original text examples (one per line)..."
                    className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm resize-none"
                    onChange={(e) => setExamples(prev => ({
                      ...prev, 
                      original: e.target.value.split('\n').filter(line => line.trim())
                    }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Transformed Text Examples</label>
                  <textarea
                    placeholder="Enter transformed text examples (one per line)..."
                    className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm resize-none"
                    onChange={(e) => setExamples(prev => ({
                      ...prev, 
                      transformed: e.target.value.split('\n').filter(line => line.trim())
                    }))}
                  />
                </div>
              </div>

              <div className="flex items-center gap-4">
                <button
                  onClick={inferManifestFromExamples}
                  disabled={isInferringManifest || examples.original.length === 0 || examples.transformed.length === 0}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
                >
                  {isInferringManifest ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Inferring...
                    </>
                  ) : (
                    <>
                      <Brain className="w-4 h-4" />
                      Infer Manifest
                    </>
                  )}
                </button>
                
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {examples.original.length} original • {examples.transformed.length} transformed
                </div>
              </div>

              {/* Manifest Display */}
              {manifestData && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Generated Manifest</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Namespace */}
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                      <div className="flex items-center gap-2 mb-3">
                        <Globe className="w-5 h-5 text-green-600" />
                        <h4 className="font-semibold text-green-800 dark:text-green-200">Namespace</h4>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div><strong>ID:</strong> {manifestData.namespace?.id}</div>
                        <div><strong>Pattern:</strong> <code className="text-xs bg-white dark:bg-gray-800 px-1 rounded">{manifestData.namespace?.phonotactic_pattern}</code></div>
                        <div><strong>Lexicon:</strong> {manifestData.namespace?.lexicon_seed?.length || 0} terms</div>
                        <div><strong>Policy:</strong> {manifestData.namespace?.mapping_policy}</div>
                      </div>
                    </div>

                    {/* Persona */}
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                      <div className="flex items-center gap-2 mb-3">
                        <Users className="w-5 h-5 text-blue-600" />
                        <h4 className="font-semibold text-blue-800 dark:text-blue-200">Persona</h4>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div><strong>Label:</strong> {manifestData.persona?.label}</div>
                        <div><strong>Perspective:</strong> {manifestData.persona?.perspective}</div>
                        <div><strong>Register:</strong> {manifestData.persona?.register}</div>
                        <div><strong>Pronouns:</strong> {Object.keys(manifestData.persona?.pronoun_usage || {}).length} patterns</div>
                      </div>
                    </div>

                    {/* Style */}
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                      <div className="flex items-center gap-2 mb-3">
                        <Palette className="w-5 h-5 text-purple-600" />
                        <h4 className="font-semibold text-purple-800 dark:text-purple-200">Style</h4>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div><strong>Avg Length:</strong> {manifestData.style?.avg_sentence_length?.toFixed(1)} words</div>
                        <div><strong>Formality:</strong> {manifestData.style?.formality_score?.toFixed(2)}</div>
                        <div><strong>Devices:</strong> {manifestData.style?.rhetorical_devices?.length || 0}</div>
                        <div><strong>Punctuation:</strong> {manifestData.style?.punctuation_density?.toFixed(3)}</div>
                      </div>
                    </div>
                  </div>

                  {/* JSON Export */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">JSON Manifest</span>
                      <button
                        onClick={() => navigator.clipboard.writeText(JSON.stringify(manifestData, null, 2))}
                        className="flex items-center gap-1 px-2 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm"
                      >
                        <Copy className="w-3 h-3" />
                        Copy
                      </button>
                    </div>
                    <pre className="text-xs bg-white dark:bg-gray-900 p-3 rounded border overflow-x-auto">
                      {JSON.stringify(manifestData, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}

      {/* Phonotactics Analysis Modal */}
      {showPhonotacticsModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Languages className="w-6 h-6 text-indigo-600" />
                <h2 className="text-xl font-semibold">Phonotactic Pattern Analysis</h2>
              </div>
              <button
                onClick={() => setShowPhonotacticsModal(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Name Input */}
              <div>
                <label className="block text-sm font-medium mb-2">Names to Analyze</label>
                <textarea
                  placeholder="Enter names (one per line) e.g.:
Threlvax
Zyne  
Quell
Narth"
                  className="w-full h-32 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm resize-none"
                  onChange={(e) => {
                    const names = e.target.value.split('\n').filter(line => line.trim());
                    if (names.length > 0) {
                      analyzePhonotactics(names);
                    }
                  }}
                />
              </div>

              {/* Analysis Results */}
              {phonotacticsData && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Analysis Results</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                      <h4 className="font-semibold text-indigo-800 dark:text-indigo-200 mb-3">Phonotactic Pattern</h4>
                      <code className="block text-sm bg-white dark:bg-gray-800 p-2 rounded border">
                        {phonotacticsData.phonotactic_pattern || "No pattern detected"}
                      </code>
                      <div className="mt-2 text-sm text-indigo-700 dark:text-indigo-300">
                        Complexity: {phonotacticsData.pattern_analysis?.pattern_complexity || 0}
                      </div>
                    </div>

                    <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                      <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-3">Generated Examples</h4>
                      <div className="space-y-1">
                        {phonotacticsData.example_generated_names?.map((name, idx) => (
                          <div key={idx} className="text-sm font-mono bg-white dark:bg-gray-800 px-2 py-1 rounded">
                            {name}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Phoneme Frequencies */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border">
                    <h4 className="font-semibold mb-3">Phoneme Frequencies</h4>
                    <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
                      {Object.entries(phonotacticsData.phoneme_frequencies || {})
                        .sort(([,a], [,b]) => b - a)
                        .slice(0, 16)
                        .map(([phoneme, freq]) => (
                          <div key={phoneme} className="text-center p-2 bg-white dark:bg-gray-700 rounded">
                            <div className="font-mono text-lg">{phoneme}</div>
                            <div className="text-xs text-gray-600 dark:text-gray-400">
                              {(freq * 100).toFixed(1)}%
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}

      {/* Quick Extract Modal */}
      {showQuickExtractModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Target className="w-6 h-6 text-green-600" />
                <h2 className="text-xl font-semibold">Quick Extract Attribute</h2>
              </div>
              <button
                onClick={() => setShowQuickExtractModal(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Attribute Type</label>
                <select
                  value={quickExtractType}
                  onChange={(e) => setQuickExtractType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                >
                  <option value="persona">Persona - Character voice and perspective</option>
                  <option value="style">Style - Writing patterns and structure</option>
                  <option value="namespace">Namespace - Semantic context and references</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Attribute Name</label>
                <input
                  type="text"
                  value={quickExtractName}
                  onChange={(e) => setQuickExtractName(e.target.value)}
                  placeholder="e.g., 'Academic Researcher', 'Victorian Poetry', 'Sci-Fi Universe'"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleQuickExtract();
                    }
                  }}
                />
              </div>

              <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  <strong>Extract {quickExtractType}</strong> from your current text and save it as "{quickExtractName || 'New Attribute'}" for use in other tabs.
                </p>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => setShowQuickExtractModal(false)}
                  className="flex-1 px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  onClick={handleQuickExtract}
                  disabled={!quickExtractName.trim() || !inputText.trim() || isAnalyzing}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium inline-flex items-center justify-center gap-2"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Extracting...
                    </>
                  ) : (
                    <>
                      <Target className="w-4 h-4" />
                      Extract & Save
                    </>
                  )}
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default AttributeStudio;