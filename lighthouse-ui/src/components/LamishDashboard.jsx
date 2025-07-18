import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Settings,
  Database,
  Brain,
  Users,
  Globe,
  Palette,
  Plus,
  Edit3,
  Trash2,
  Download,
  Upload,
  BarChart3,
  Activity,
  Search,
  Filter,
  Save,
  X,
  Check,
  AlertTriangle,
  TrendingUp,
  Layers,
  Loader2,
  Play
} from "lucide-react";

const LamishDashboard = () => {
  const [activeSection, setActiveSection] = useState("overview");
  const [concepts, setConcepts] = useState({ personas: [], namespaces: [], styles: [] });
  const [meanings, setMeanings] = useState([]);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [editingConcept, setEditingConcept] = useState(null);
  const [newConcept, setNewConcept] = useState({ type: "persona", name: "", description: "", characteristics: [] });
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState("all");
  const [narrativeText, setNarrativeText] = useState("");
  const [extractedAttributes, setExtractedAttributes] = useState(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [selectedStep, setSelectedStep] = useState("deconstruct");
  const [selectedAttributes, setSelectedAttributes] = useState({
    persona: "philosopher",
    namespace: "lamish-galaxy", 
    style: "poetic"
  });
  const [inspectorPrompts, setInspectorPrompts] = useState({});
  const [isLoadingPrompts, setIsLoadingPrompts] = useState(false);
  const [liveLogs, setLiveLogs] = useState([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [testNarrative, setTestNarrative] = useState("");
  const [isTestRunning, setIsTestRunning] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      // Load concepts, meanings, and stats
      // These endpoints need to be implemented
      const [conceptsRes, meaningsRes, statsRes] = await Promise.all([
        fetch("/api/lamish/concepts").catch(() => ({ ok: false })),
        fetch("/api/lamish/meanings").catch(() => ({ ok: false })),
        fetch("/api/lamish/stats").catch(() => ({ ok: false }))
      ]);

      // Fallback data for now
      setConcepts({
        personas: [
          { id: "1", name: "philosopher", description: "Contemplative thinker seeking deeper truths", usage_count: 15, quality_score: 0.85 },
          { id: "2", name: "storyteller", description: "Narrative craftsperson weaving tales", usage_count: 23, quality_score: 0.92 },
          { id: "3", name: "scientist", description: "Empirical observer documenting phenomena", usage_count: 8, quality_score: 0.78 }
        ],
        namespaces: [
          { id: "4", name: "lamish-galaxy", description: "Science fiction universe with frequency-based technology", usage_count: 18, quality_score: 0.88 },
          { id: "5", name: "corporate-dystopia", description: "Near-future world dominated by corporate control", usage_count: 12, quality_score: 0.82 },
          { id: "6", name: "medieval-realm", description: "Fantasy world of knights and magic", usage_count: 9, quality_score: 0.75 }
        ],
        styles: [
          { id: "7", name: "poetic", description: "Lyrical language with rhythm and metaphor", usage_count: 20, quality_score: 0.90 },
          { id: "8", name: "formal", description: "Structured, precise language", usage_count: 14, quality_score: 0.83 },
          { id: "9", name: "casual", description: "Relaxed, conversational tone", usage_count: 11, quality_score: 0.79 }
        ]
      });

      setMeanings([
        { id: "1", preview: "Call me Ishmael. Some years ago...", dimensions: 768, created: "2024-01-15" },
        { id: "2", preview: "It was the best of times...", dimensions: 768, created: "2024-01-14" },
        { id: "3", preview: "In the beginning was the Word...", dimensions: 768, created: "2024-01-13" }
      ]);

      setStats({
        total_concepts: 9,
        total_meanings: 3,
        most_used_persona: "storyteller",
        most_used_namespace: "lamish-galaxy",
        most_used_style: "poetic",
        avg_quality_score: 0.82
      });

    } catch (error) {
      console.error("Failed to load dashboard data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveConcept = async (concept) => {
    try {
      const method = concept.id ? "PUT" : "POST";
      const url = concept.id ? `/api/lamish/concepts/${concept.id}` : "/api/lamish/concepts";
      
      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(concept)
      });

      if (response.ok) {
        await loadDashboardData(); // Reload data
        setEditingConcept(null);
        setNewConcept({ type: "persona", name: "", description: "", characteristics: [] });
      }
    } catch (error) {
      console.error("Failed to save concept:", error);
    }
  };

  const handleDeleteConcept = async (conceptId) => {
    if (confirm("Are you sure you want to delete this concept?")) {
      try {
        await fetch(`/api/lamish/concepts/${conceptId}`, { method: "DELETE" });
        await loadDashboardData();
      } catch (error) {
        console.error("Failed to delete concept:", error);
      }
    }
  };

  const handleExtractAttributes = async () => {
    if (!narrativeText.trim()) return;
    
    setIsExtracting(true);
    try {
      const response = await fetch("/api/lamish/extract-attributes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ narrative: narrativeText })
      });
      
      if (response.ok) {
        const data = await response.json();
        setExtractedAttributes(data);
      } else {
        console.error("Failed to extract attributes");
      }
    } catch (error) {
      console.error("Failed to extract attributes:", error);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleSaveExtracted = async (type, attributeData) => {
    try {
      const conceptData = {
        type: type === 'namespace' ? 'namespace' : type === 'style' ? 'style' : 'persona',
        name: attributeData.name,
        description: attributeData.description,
        characteristics: attributeData.characteristics || [],
        examples: attributeData.examples || []
      };
      
      const response = await fetch("/api/lamish/concepts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(conceptData)
      });
      
      if (response.ok) {
        await loadDashboardData();
        alert(`${type.charAt(0).toUpperCase() + type.slice(1)} saved successfully!`);
      } else {
        console.error(`Failed to save ${type}`);
      }
    } catch (error) {
      console.error(`Failed to save ${type}:`, error);
    }
  };

  const loadPromptPreview = async () => {
    setIsLoadingPrompts(true);
    try {
      const response = await fetch("/api/lamish/inspect-prompts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(selectedAttributes)
      });
      
      if (response.ok) {
        const promptData = await response.json();
        setInspectorPrompts(promptData);
      } else {
        console.error("Failed to load prompts");
      }
    } catch (error) {
      console.error("Failed to load prompts:", error);
    } finally {
      setIsLoadingPrompts(false);
    }
  };

  const savePromptChanges = async (stepId) => {
    try {
      const response = await fetch("/api/lamish/save-prompts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          step: stepId,
          prompts: inspectorPrompts[stepId]
        })
      });
      
      if (response.ok) {
        alert("Prompt changes saved successfully!");
      } else {
        console.error("Failed to save prompt changes");
      }
    } catch (error) {
      console.error("Failed to save prompt changes:", error);
    }
  };

  const addLogEntry = (level, message, step = null, duration = null) => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = { level, message, step, duration, timestamp };
    setLiveLogs(prev => [...prev, logEntry]);
  };

  const runTestPipeline = async () => {
    if (!testNarrative.trim()) return;
    
    setIsTestRunning(true);
    setIsMonitoring(true);
    setLiveLogs([]);
    
    addLogEntry('info', `Starting pipeline test with ${selectedAttributes.persona}/${selectedAttributes.namespace}/${selectedAttributes.style}`);
    
    try {
      // Generate a unique transform ID for this test
      const transformId = `test-${Date.now()}`;
      
      // Connect to WebSocket for real-time updates
      const ws = new WebSocket(`ws://localhost:8100/ws/transform/${transformId}`);
      
      ws.onopen = () => {
        addLogEntry('success', 'Connected to live monitoring WebSocket');
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'progress') {
            const { step, status, data: stepData } = data;
            
            if (status === 'started') {
              addLogEntry('info', `Starting step: ${stepData.step_name}`, step);
              if (stepData.input_preview) {
                addLogEntry('debug', `Input preview: ${stepData.input_preview}...`, step);
              }
            } else if (status === 'completed') {
              addLogEntry('success', `Completed step: ${stepData.step_name}`, step, stepData.duration_ms);
              if (stepData.output_preview) {
                addLogEntry('debug', `Output preview: ${stepData.output_preview}...`, step);
              }
            } else if (status === 'error') {
              addLogEntry('error', `Error in step: ${stepData.error}`, step);
            }
          }
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };
      
      ws.onclose = () => {
        addLogEntry('info', 'WebSocket connection closed');
        setIsMonitoring(false);
      };
      
      ws.onerror = (error) => {
        addLogEntry('warning', 'WebSocket connection error - continuing without live updates');
      };
      
      // Start the actual transformation
      addLogEntry('info', 'Sending transformation request to API...');
      
      const response = await fetch("/api/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          narrative: testNarrative,
          target_persona: selectedAttributes.persona,
          target_namespace: selectedAttributes.namespace,
          target_style: selectedAttributes.style,
          show_steps: true,
          transform_id: transformId
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        addLogEntry('success', `Pipeline completed successfully in ${result.total_duration_ms}ms`);
        addLogEntry('info', `Generated ${result.steps?.length || 0} transformation steps`);
        
        // Close WebSocket after a short delay to catch any final messages
        setTimeout(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.close();
          }
        }, 2000);
      } else {
        addLogEntry('error', `API request failed: ${response.status} ${response.statusText}`);
        ws.close();
      }
      
    } catch (error) {
      addLogEntry('error', `Pipeline test failed: ${error.message}`);
      setIsMonitoring(false);
    } finally {
      setIsTestRunning(false);
    }
  };

  const sections = [
    { id: "overview", label: "Overview", icon: BarChart3 },
    { id: "extract", label: "Extract Attributes", icon: TrendingUp },
    { id: "inspector", label: "Pipeline Inspector", icon: Activity },
    { id: "pipeline", label: "Pipeline Flow", icon: Layers },
    { id: "personas", label: "Personas", icon: Users },
    { id: "namespaces", label: "Namespaces", icon: Globe },
    { id: "styles", label: "Styles", icon: Palette },
    { id: "meanings", label: "Embeddings", icon: Brain },
    { id: "config", label: "Configuration", icon: Settings }
  ];

  const filteredConcepts = (type) => {
    const conceptList = concepts[type] || [];
    return conceptList.filter(concept =>
      concept.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      concept.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  const ConceptEditor = ({ concept, onSave, onCancel }) => {
    const [editData, setEditData] = useState(concept || { ...newConcept });

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      >
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            {concept ? "Edit" : "Add"} {editData.type}
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Type</label>
              <select
                value={editData.type}
                onChange={(e) => setEditData({ ...editData, type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="persona">Persona</option>
                <option value="namespace">Namespace</option>
                <option value="style">Style</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Name</label>
              <input
                type="text"
                value={editData.name}
                onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Enter name..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
              <textarea
                value={editData.description}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-20 resize-none"
                placeholder="Enter description..."
              />
            </div>
          </div>
          
          <div className="flex gap-3 mt-6">
            <button
              onClick={() => onSave(editData)}
              disabled={!editData.name.trim() || !editData.description.trim()}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
            >
              Save
            </button>
            <button
              onClick={onCancel}
              className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Dashboard Header */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Database className="w-6 h-6 text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Lamish Knowledge Dashboard
            </h1>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <Activity className="w-4 h-4" />
            System Active
          </div>
        </div>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Manage your knowledge base, configure projection tools, and monitor lamish meaning embeddings
        </p>
      </div>

      {/* Navigation */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700">
        <div className="flex overflow-x-auto">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`flex items-center gap-2 px-6 py-4 whitespace-nowrap border-b-2 transition-colors ${
                  activeSection === section.id
                    ? "border-indigo-500 text-indigo-600 dark:text-indigo-400"
                    : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                }`}
              >
                <Icon className="w-4 h-4" />
                {section.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeSection === "pipeline" && (
          <motion.div
            key="pipeline"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Pipeline Flow Visualization */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3 mb-6">
                <Layers className="w-6 h-6 text-indigo-600" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  5-Step LPE Pipeline Flow
                </h2>
              </div>
              
              <div className="space-y-6">
                {/* Step 1: Deconstruct */}
                <div className="relative">
                  <div className="flex items-start gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                        1
                      </div>
                      <div className="w-0.5 h-16 bg-gray-300 dark:bg-gray-600 mt-2"></div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        Deconstructing Narrative
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        Extract core narrative elements: WHO, WHAT, WHY, HOW, OUTCOME
                      </p>
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
                        <div className="text-sm text-gray-700 dark:text-gray-300">
                          <strong>Input:</strong> Raw narrative text<br/>
                          <strong>Output:</strong> Structured story elements<br/>
                          <strong>Attributes Used:</strong> None (pure extraction)
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Step 2: Map */}
                <div className="relative">
                  <div className="flex items-start gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                        2
                      </div>
                      <div className="w-0.5 h-16 bg-gray-300 dark:bg-gray-600 mt-2"></div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        Mapping to Namespace
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        Translate elements to target universe while preserving story structure
                      </p>
                      <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-800">
                        <div className="text-sm text-gray-700 dark:text-gray-300">
                          <strong>Input:</strong> Structured elements<br/>
                          <strong>Output:</strong> Namespace-mapped elements<br/>
                          <strong>Attributes Used:</strong> <span className="text-green-600 dark:text-green-400 font-semibold">NAMESPACE</span> (determines target universe)
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Step 3: Reconstruct */}
                <div className="relative">
                  <div className="flex items-start gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                        3
                      </div>
                      <div className="w-0.5 h-16 bg-gray-300 dark:bg-gray-600 mt-2"></div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        Reconstructing Allegory
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        Rebuild narrative with mapped elements from persona's perspective
                      </p>
                      <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-200 dark:border-purple-800">
                        <div className="text-sm text-gray-700 dark:text-gray-300">
                          <strong>Input:</strong> Mapped elements<br/>
                          <strong>Output:</strong> Reconstructed narrative<br/>
                          <strong>Attributes Used:</strong> <span className="text-purple-600 dark:text-purple-400 font-semibold">PERSONA</span> (determines narrative voice)
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Step 4: Stylize */}
                <div className="relative">
                  <div className="flex items-start gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                        4
                      </div>
                      <div className="w-0.5 h-16 bg-gray-300 dark:bg-gray-600 mt-2"></div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        Applying Style
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        Adjust tone and voice while keeping story content unchanged
                      </p>
                      <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-3 border border-orange-200 dark:border-orange-800">
                        <div className="text-sm text-gray-700 dark:text-gray-300">
                          <strong>Input:</strong> Reconstructed narrative<br/>
                          <strong>Output:</strong> Styled narrative<br/>
                          <strong>Attributes Used:</strong> <span className="text-orange-600 dark:text-orange-400 font-semibold">STYLE</span> (determines linguistic expression)
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Step 5: Reflect */}
                <div className="relative">
                  <div className="flex items-start gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center font-semibold text-sm">
                        5
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        Generating Reflection
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 mb-3">
                        Generate meta-commentary on how the transformation illuminates the original
                      </p>
                      <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-200 dark:border-red-800">
                        <div className="text-sm text-gray-700 dark:text-gray-300">
                          <strong>Input:</strong> Styled narrative<br/>
                          <strong>Output:</strong> Final projection + reflection<br/>
                          <strong>Attributes Used:</strong> <span className="text-red-600 dark:text-red-400 font-semibold">ALL THREE</span> (inform meta-commentary)
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Attribute Flow Summary */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                How Attributes Shape the Pipeline
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Globe className="w-5 h-5 text-green-600" />
                    <h4 className="font-semibold text-green-900 dark:text-green-100">Namespace</h4>
                  </div>
                  <p className="text-sm text-green-800 dark:text-green-200 mb-2">
                    <strong>Active in Step 2:</strong> Determines the target universe for element mapping
                  </p>
                  <p className="text-xs text-green-700 dark:text-green-300">
                    Example: "lamish-galaxy" maps a CEO to a Crystal Frequency Controller
                  </p>
                </div>
                
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Users className="w-5 h-5 text-purple-600" />
                    <h4 className="font-semibold text-purple-900 dark:text-purple-100">Persona</h4>
                  </div>
                  <p className="text-sm text-purple-800 dark:text-purple-200 mb-2">
                    <strong>Active in Step 3:</strong> Shapes the narrative voice and perspective
                  </p>
                  <p className="text-xs text-purple-700 dark:text-purple-300">
                    Example: "philosopher" tells the story seeking deeper universal truths
                  </p>
                </div>
                
                <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                  <div className="flex items-center gap-2 mb-2">
                    <Palette className="w-5 h-5 text-orange-600" />
                    <h4 className="font-semibold text-orange-900 dark:text-orange-100">Style</h4>
                  </div>
                  <p className="text-sm text-orange-800 dark:text-orange-200 mb-2">
                    <strong>Active in Step 4:</strong> Adjusts linguistic expression and tone
                  </p>
                  <p className="text-xs text-orange-700 dark:text-orange-300">
                    Example: "poetic" adds rhythm, metaphor, and lyrical language
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeSection === "inspector" && (
          <motion.div
            key="inspector"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Inspector Header and Controls */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3 mb-6">
                <Activity className="w-6 h-6 text-indigo-600" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Pipeline Inspector - Live Prompts & Execution
                </h2>
              </div>
              
              {/* Attribute Selectors */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Persona
                  </label>
                  <select
                    value={selectedAttributes.persona}
                    onChange={(e) => {
                      setSelectedAttributes({...selectedAttributes, persona: e.target.value});
                      loadPromptPreview();
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {concepts.personas?.map(p => (
                      <option key={p.id} value={p.name}>{p.name}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Namespace
                  </label>
                  <select
                    value={selectedAttributes.namespace}
                    onChange={(e) => {
                      setSelectedAttributes({...selectedAttributes, namespace: e.target.value});
                      loadPromptPreview();
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {concepts.namespaces?.map(n => (
                      <option key={n.id} value={n.name}>{n.name}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Style
                  </label>
                  <select
                    value={selectedAttributes.style}
                    onChange={(e) => {
                      setSelectedAttributes({...selectedAttributes, style: e.target.value});
                      loadPromptPreview();
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {concepts.styles?.map(s => (
                      <option key={s.id} value={s.name}>{s.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <button
                onClick={loadPromptPreview}
                disabled={isLoadingPrompts}
                className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
              >
                {isLoadingPrompts ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Loading Prompts...
                  </>
                ) : (
                  <>
                    <Activity className="w-4 h-4" />
                    Load Live Prompts
                  </>
                )}
              </button>
            </div>

            {/* Step Navigation */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700">
              <div className="flex overflow-x-auto">
                {[
                  { id: "deconstruct", label: "1. Deconstruct", color: "blue" },
                  { id: "map", label: "2. Map", color: "green" },
                  { id: "reconstruct", label: "3. Reconstruct", color: "purple" },
                  { id: "stylize", label: "4. Stylize", color: "orange" },
                  { id: "reflect", label: "5. Reflect", color: "red" }
                ].map((step) => (
                  <button
                    key={step.id}
                    onClick={() => setSelectedStep(step.id)}
                    className={`flex items-center gap-2 px-6 py-4 whitespace-nowrap border-b-2 transition-colors ${
                      selectedStep === step.id
                        ? `border-${step.color}-500 text-${step.color}-600 dark:text-${step.color}-400`
                        : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                    }`}
                  >
                    {step.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Live Prompt Display */}
            {inspectorPrompts[selectedStep] && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* System Prompt */}
                <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      System Prompt ({selectedStep})
                    </h3>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500 dark:text-gray-400">Editable</span>
                      <Edit3 className="w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                  <textarea
                    value={inspectorPrompts[selectedStep]?.system_prompt || ''}
                    onChange={(e) => {
                      const newPrompts = { ...inspectorPrompts };
                      newPrompts[selectedStep] = {
                        ...newPrompts[selectedStep],
                        system_prompt: e.target.value
                      };
                      setInspectorPrompts(newPrompts);
                    }}
                    className="w-full h-32 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono resize-none"
                    placeholder="System prompt will appear here..."
                  />
                </div>

                {/* User Prompt */}
                <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      User Prompt ({selectedStep})
                    </h3>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500 dark:text-gray-400">Editable</span>
                      <Edit3 className="w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                  <textarea
                    value={inspectorPrompts[selectedStep]?.user_prompt || ''}
                    onChange={(e) => {
                      const newPrompts = { ...inspectorPrompts };
                      newPrompts[selectedStep] = {
                        ...newPrompts[selectedStep],
                        user_prompt: e.target.value
                      };
                      setInspectorPrompts(newPrompts);
                    }}
                    className="w-full h-40 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm font-mono resize-none"
                    placeholder="User prompt template will appear here..."
                  />
                </div>

                {/* Metadata Flow */}
                <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Content & Metadata Flow
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                      <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Input</h4>
                      <div className="text-sm text-blue-800 dark:text-blue-200">
                        {inspectorPrompts[selectedStep]?.input_description || 'Loading...'}
                      </div>
                    </div>
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                      <h4 className="font-semibold text-green-900 dark:text-green-100 mb-2">Output</h4>
                      <div className="text-sm text-green-800 dark:text-green-200">
                        {inspectorPrompts[selectedStep]?.output_description || 'Loading...'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Test Pipeline & Live Log */}
                <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Test Pipeline with Live Monitoring
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Test Narrative
                      </label>
                      <textarea
                        value={testNarrative}
                        onChange={(e) => setTestNarrative(e.target.value)}
                        className="w-full h-20 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm resize-none"
                        placeholder="Enter a test narrative to run through the pipeline with live monitoring..."
                      />
                    </div>
                    
                    <div className="flex gap-3">
                      <button
                        onClick={runTestPipeline}
                        disabled={!testNarrative.trim() || isTestRunning}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors"
                      >
                        {isTestRunning ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Running Pipeline...
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4" />
                            Run Test Pipeline
                          </>
                        )}
                      </button>
                      
                      <button
                        onClick={() => {
                          setLiveLogs([]);
                          setIsMonitoring(false);
                        }}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
                      >
                        <X className="w-4 h-4" />
                        Clear Logs
                      </button>
                    </div>
                  </div>
                  
                  {/* Live Log Window */}
                  {(liveLogs.length > 0 || isMonitoring) && (
                    <div className="mt-6">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold text-gray-900 dark:text-white">
                          Live Execution Log
                        </h4>
                        <div className="flex items-center gap-2">
                          {isMonitoring && (
                            <div className="flex items-center gap-1">
                              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                              <span className="text-xs text-green-600 dark:text-green-400">Live</span>
                            </div>
                          )}
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {liveLogs.length} entries
                          </span>
                        </div>
                      </div>
                      
                      <div className="bg-gray-900 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
                        {liveLogs.length === 0 && isMonitoring && (
                          <div className="text-gray-400 italic">Waiting for log entries...</div>
                        )}
                        {liveLogs.map((log, idx) => (
                          <div
                            key={idx}
                            className={`mb-1 ${
                              log.level === 'error' ? 'text-red-400' :
                              log.level === 'warning' ? 'text-yellow-400' :
                              log.level === 'success' ? 'text-green-400' :
                              log.level === 'info' ? 'text-blue-400' :
                              'text-gray-300'
                            }`}
                          >
                            <span className="text-gray-500">[{log.timestamp}]</span>
                            <span className="ml-2">{log.step && `[${log.step.toUpperCase()}]`}</span>
                            <span className="ml-2">{log.message}</span>
                            {log.duration && (
                              <span className="text-gray-400 ml-2">({log.duration}ms)</span>
                            )}
                          </div>
                        ))}
                        {isMonitoring && (
                          <div className="text-gray-400 animate-pulse">▊</div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Save Prompts */}
                <div className="flex justify-end">
                  <button
                    onClick={() => savePromptChanges(selectedStep)}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
                  >
                    <Save className="w-4 h-4" />
                    Save Prompt Changes
                  </button>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {activeSection === "extract" && (
          <motion.div
            key="extract"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Text Input and Analysis */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6 text-indigo-600" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Extract Attributes from Text
                </h2>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Narrative Text
                  </label>
                  <textarea
                    value={narrativeText}
                    onChange={(e) => setNarrativeText(e.target.value)}
                    placeholder="Enter narrative text to analyze and extract inherent persona, namespace, and style attributes..."
                    className="w-full h-32 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  />
                </div>
                
                <button
                  onClick={() => handleExtractAttributes()}
                  disabled={!narrativeText.trim() || isExtracting}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-all duration-200 disabled:cursor-not-allowed"
                >
                  {isExtracting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Analyzing Text...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-4 h-4" />
                      Extract Inherent Attributes
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Extracted Attributes */}
            {extractedAttributes && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                    Extracted Attributes
                  </h3>
                  
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Extracted Persona */}
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                      <div className="flex items-center gap-2 mb-3">
                        <Users className="w-5 h-5 text-purple-600" />
                        <h4 className="font-semibold text-purple-900 dark:text-purple-100">Persona</h4>
                      </div>
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={extractedAttributes.persona.name}
                          onChange={(e) => setExtractedAttributes({
                            ...extractedAttributes,
                            persona: { ...extractedAttributes.persona, name: e.target.value }
                          })}
                          className="w-full px-3 py-2 text-sm border border-purple-300 dark:border-purple-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-semibold"
                          placeholder="Persona name"
                        />
                        <textarea
                          value={extractedAttributes.persona.description}
                          onChange={(e) => setExtractedAttributes({
                            ...extractedAttributes,
                            persona: { ...extractedAttributes.persona, description: e.target.value }
                          })}
                          className="w-full px-3 py-2 text-sm border border-purple-300 dark:border-purple-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-20 resize-none"
                          placeholder="Persona description"
                        />
                        <div className="flex flex-wrap gap-1 mt-2">
                          {extractedAttributes.persona.characteristics?.map((char, idx) => (
                            <span key={idx} className="px-2 py-1 bg-purple-100 dark:bg-purple-900/40 text-purple-800 dark:text-purple-200 text-xs rounded-full">
                              {char}
                            </span>
                          ))}
                        </div>
                        <button
                          onClick={() => handleSaveExtracted('persona', extractedAttributes.persona)}
                          className="w-full mt-2 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg font-medium transition-colors"
                        >
                          Save Persona
                        </button>
                      </div>
                    </div>

                    {/* Extracted Namespace */}
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                      <div className="flex items-center gap-2 mb-3">
                        <Globe className="w-5 h-5 text-green-600" />
                        <h4 className="font-semibold text-green-900 dark:text-green-100">Namespace</h4>
                      </div>
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={extractedAttributes.namespace.name}
                          onChange={(e) => setExtractedAttributes({
                            ...extractedAttributes,
                            namespace: { ...extractedAttributes.namespace, name: e.target.value }
                          })}
                          className="w-full px-3 py-2 text-sm border border-green-300 dark:border-green-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-semibold"
                          placeholder="Namespace name"
                        />
                        <textarea
                          value={extractedAttributes.namespace.description}
                          onChange={(e) => setExtractedAttributes({
                            ...extractedAttributes,
                            namespace: { ...extractedAttributes.namespace, description: e.target.value }
                          })}
                          className="w-full px-3 py-2 text-sm border border-green-300 dark:border-green-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-20 resize-none"
                          placeholder="Namespace description"
                        />
                        <div className="flex flex-wrap gap-1 mt-2">
                          {extractedAttributes.namespace.characteristics?.map((char, idx) => (
                            <span key={idx} className="px-2 py-1 bg-green-100 dark:bg-green-900/40 text-green-800 dark:text-green-200 text-xs rounded-full">
                              {char}
                            </span>
                          ))}
                        </div>
                        <button
                          onClick={() => handleSaveExtracted('namespace', extractedAttributes.namespace)}
                          className="w-full mt-2 px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg font-medium transition-colors"
                        >
                          Save Namespace
                        </button>
                      </div>
                    </div>

                    {/* Extracted Style */}
                    <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
                      <div className="flex items-center gap-2 mb-3">
                        <Palette className="w-5 h-5 text-orange-600" />
                        <h4 className="font-semibold text-orange-900 dark:text-orange-100">Style</h4>
                      </div>
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={extractedAttributes.style.name}
                          onChange={(e) => setExtractedAttributes({
                            ...extractedAttributes,
                            style: { ...extractedAttributes.style, name: e.target.value }
                          })}
                          className="w-full px-3 py-2 text-sm border border-orange-300 dark:border-orange-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-semibold"
                          placeholder="Style name"
                        />
                        <textarea
                          value={extractedAttributes.style.description}
                          onChange={(e) => setExtractedAttributes({
                            ...extractedAttributes,
                            style: { ...extractedAttributes.style, description: e.target.value }
                          })}
                          className="w-full px-3 py-2 text-sm border border-orange-300 dark:border-orange-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-20 resize-none"
                          placeholder="Style description"
                        />
                        <div className="flex flex-wrap gap-1 mt-2">
                          {extractedAttributes.style.characteristics?.map((char, idx) => (
                            <span key={idx} className="px-2 py-1 bg-orange-100 dark:bg-orange-900/40 text-orange-800 dark:text-orange-200 text-xs rounded-full">
                              {char}
                            </span>
                          ))}
                        </div>
                        <button
                          onClick={() => handleSaveExtracted('style', extractedAttributes.style)}
                          className="w-full mt-2 px-3 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded-lg font-medium transition-colors"
                        >
                          Save Style
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {activeSection === "overview" && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Concepts</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.total_concepts || 0}</p>
                  </div>
                  <Layers className="w-8 h-8 text-blue-500" />
                </div>
              </div>
              
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Stored Meanings</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.total_meanings || 0}</p>
                  </div>
                  <Brain className="w-8 h-8 text-purple-500" />
                </div>
              </div>
              
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Avg Quality</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {stats?.avg_quality_score ? `${(stats.avg_quality_score * 100).toFixed(0)}%` : "0%"}
                    </p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-500" />
                </div>
              </div>
              
              <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Most Used</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">{stats?.most_used_persona || "None"}</p>
                  </div>
                  <Users className="w-8 h-8 text-orange-500" />
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Recent Activity</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <Plus className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">New meaning stored: "Call me Ishmael..."</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">2 min ago</span>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <TrendingUp className="w-4 h-4 text-blue-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Persona "storyteller" quality improved to 92%</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">1 hour ago</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {(activeSection === "personas" || activeSection === "namespaces" || activeSection === "styles") && (
          <motion.div
            key={activeSection}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Controls */}
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search concepts..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white w-64"
                    />
                  </div>
                </div>
                <button
                  onClick={() => setEditingConcept({ type: activeSection.slice(0, -1), name: "", description: "" })}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Add {activeSection.slice(0, -1)}
                </button>
              </div>
            </div>

            {/* Concepts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredConcepts(activeSection).map((concept) => (
                <div
                  key={concept.id}
                  className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{concept.name}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{concept.description}</p>
                    </div>
                    
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => setEditingConcept(concept)}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteConcept(concept.id)}
                        className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Component Breakdown */}
                  <div className="space-y-3">
                    {/* Characteristics */}
                    {concept.characteristics && concept.characteristics.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-2">
                          Characteristics
                        </h4>
                        <div className="flex flex-wrap gap-1">
                          {concept.characteristics.map((char, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-xs rounded-full"
                            >
                              {char}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Examples */}
                    {concept.examples && concept.examples.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-2">
                          Examples
                        </h4>
                        <div className="space-y-1">
                          {concept.examples.slice(0, 2).map((example, idx) => (
                            <div
                              key={idx}
                              className="text-xs text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50 px-2 py-1 rounded"
                            >
                              • {example}
                            </div>
                          ))}
                          {concept.examples.length > 2 && (
                            <div className="text-xs text-gray-500 dark:text-gray-500 italic">
                              +{concept.examples.length - 2} more...
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {/* Usage Stats */}
                    <div className="flex items-center justify-between pt-2 border-t border-gray-200 dark:border-gray-600">
                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>Used: {concept.usage_count} times</span>
                        <span>Quality: {(concept.quality_score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="text-xs text-gray-400 dark:text-gray-500">
                        {activeSection === 'personas' ? 'Step 3: Narrative Voice' : 
                         activeSection === 'namespaces' ? 'Step 2: Element Mapping' :
                         'Step 4: Linguistic Style'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {activeSection === "meanings" && (
          <motion.div
            key="meanings"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Stored Lamish Meanings</h3>
              
              <div className="space-y-3">
                {meanings.map((meaning) => (
                  <div
                    key={meaning.id}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="text-sm text-gray-700 dark:text-gray-300 font-mono">
                        {meaning.preview}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                        <span>Dimensions: {meaning.dimensions}</span>
                        <span>Created: {meaning.created}</span>
                      </div>
                    </div>
                    
                    <button className="p-2 text-gray-400 hover:text-red-500 transition-colors">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeSection === "config" && (
          <motion.div
            key="config"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Transform Tab Configuration</h3>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                    Available Personas in Transform Tab
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {concepts.personas.map((persona) => (
                      <label key={persona.id} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <input type="checkbox" defaultChecked className="rounded" />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{persona.name}</span>
                        <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">
                          {persona.usage_count} uses
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                    Default Transform Settings
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <select className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                      <option>Default Persona</option>
                      {concepts.personas.map(p => <option key={p.id}>{p.name}</option>)}
                    </select>
                    <select className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                      <option>Default Namespace</option>
                      {concepts.namespaces.map(n => <option key={n.id}>{n.name}</option>)}
                    </select>
                    <select className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                      <option>Default Style</option>
                      {concepts.styles.map(s => <option key={s.id}>{s.name}</option>)}
                    </select>
                  </div>
                </div>

                <button className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors">
                  Save Configuration
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Concept Editor Modal */}
      {editingConcept && (
        <ConceptEditor
          concept={editingConcept}
          onSave={handleSaveConcept}
          onCancel={() => setEditingConcept(null)}
        />
      )}
    </div>
  );
};

export default LamishDashboard;