import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Eye, 
  FileText, 
  Image, 
  Palette, 
  Upload, 
  Loader2, 
  Copy, 
  Check,
  Download,
  Wand2,
  Settings
} from 'lucide-react'
import { cn } from '../utils'

const VisionAnalysis = ({ isActive }) => {
  const [selectedFunction, setSelectedFunction] = useState('analyze')
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [copied, setCopied] = useState(false)
  const [customPrompt, setCustomPrompt] = useState('')
  const [imagePrompt, setImagePrompt] = useState('')
  const [selectedProvider, setSelectedProvider] = useState('openai')
  const [selectedVisionModel, setSelectedVisionModel] = useState('gpt-4o')
  const [isUsingConfig, setIsUsingConfig] = useState(true)
  const [configSettings, setConfigSettings] = useState(null)

  const visionProviders = [
    {
      id: 'openai',
      label: 'OpenAI',
      models: [
        { id: 'gpt-4o', label: 'GPT-4o', description: 'Latest vision-capable model' },
        { id: 'gpt-4-turbo', label: 'GPT-4 Turbo', description: 'Fast and capable' },
        { id: 'gpt-4', label: 'GPT-4', description: 'Reliable vision model' }
      ]
    },
    {
      id: 'google',
      label: 'Google Gemini',
      models: [
        { id: 'gemini-2.5-pro', label: 'Gemini 2.5 Pro', description: 'Latest and most capable' },
        { id: 'gemini-1.5-pro', label: 'Gemini 1.5 Pro', description: 'Fast and efficient' },
        { id: 'gemini-1.5-flash', label: 'Gemini 1.5 Flash', description: 'Ultra-fast responses' }
      ]
    },
    {
      id: 'ollama',
      label: 'Ollama Local',
      models: [
        { id: 'gemma3:12b', label: 'Gemma3 12B', description: 'Local vision model' },
        { id: 'qwen3:14b', label: 'Qwen3 14B', description: 'Large local model' },
        { id: 'llama3.2:latest', label: 'Llama3.2', description: 'General purpose' }
      ]
    }
  ]

  const visionFunctions = [
    {
      id: 'analyze',
      label: 'Image Analysis',
      icon: Eye,
      description: 'Analyze and describe image content',
      defaultPrompt: 'What do you see in this image? Provide a detailed description.'
    },
    {
      id: 'transcribe',
      label: 'Handwriting OCR',
      icon: FileText,
      description: 'Transcribe handwritten text from images',
      defaultPrompt: 'Transcribe the handwritten text in this image.'
    },
    {
      id: 'redraw',
      label: 'Artistic Analysis',
      icon: Palette,
      description: 'Analyze for artistic reinterpretation',
      defaultPrompt: 'Analyze this image for artistic reinterpretation and redrawing.'
    },
    {
      id: 'generate',
      label: 'Generate Image',
      icon: Wand2,
      description: 'Generate new images from text prompts',
      defaultPrompt: 'A beautiful sunset over mountains'
    }
  ]

  // Load LLM Config settings
  useEffect(() => {
    const loadConfigSettings = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8100/api/llm/configurations')
        const data = await response.json()
        const visionConfig = data.task_configs?.vision
        if (visionConfig) {
          setConfigSettings(visionConfig)
          if (isUsingConfig) {
            setSelectedProvider(visionConfig.provider || 'openai')
            setSelectedVisionModel(visionConfig.model || 'gpt-4o')
          }
        }
      } catch (error) {
        console.error('Failed to load LLM Config:', error)
      }
    }
    
    if (isActive) {
      loadConfigSettings()
    }
  }, [isActive, isUsingConfig])

  // Get current provider's models
  const currentProviderModels = visionProviders.find(p => p.id === selectedProvider)?.models || []
  
  // Update model when provider changes
  const handleProviderChange = (providerId) => {
    setSelectedProvider(providerId)
    setIsUsingConfig(false) // Mark as override when user changes
    const provider = visionProviders.find(p => p.id === providerId)
    if (provider && provider.models.length > 0) {
      setSelectedVisionModel(provider.models[0].id)
    }
  }

  const handleModelChange = (modelId) => {
    setSelectedVisionModel(modelId)
    setIsUsingConfig(false) // Mark as override when user changes
  }

  const resetToConfig = () => {
    setIsUsingConfig(true)
    if (configSettings) {
      setSelectedProvider(configSettings.provider || 'openai')
      setSelectedVisionModel(configSettings.model || 'gpt-4o')
    }
  }

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file)
      
      // Create preview URL
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      
      // Set default prompt for selected function
      const func = visionFunctions.find(f => f.id === selectedFunction)
      if (func && !customPrompt) {
        setCustomPrompt(func.defaultPrompt)
      }
    }
  }

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result.split(',')[1])
      reader.onerror = error => reject(error)
    })
  }

  const processVision = async () => {
    if (!selectedFile && selectedFunction !== 'generate') return
    if (!customPrompt && selectedFunction !== 'generate') return
    if (!imagePrompt && selectedFunction === 'generate') return

    setIsProcessing(true)
    setResult(null)

    try {
      if (selectedFunction === 'generate') {
        // Image generation
        const response = await fetch('http://127.0.0.1:8100/api/image/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: imagePrompt,
            provider: isUsingConfig ? null : selectedProvider,
            size: '1024x1024',
            model: isUsingConfig ? null : selectedVisionModel
          })
        })

        const data = await response.json()
        setResult({
          type: 'generation',
          image_url: data.image_url,
          prompt_used: data.prompt_used,
          provider: data.provider_used,
          processing_time: data.generation_time_ms
        })
      } else {
        // Vision analysis functions
        const base64Data = await convertToBase64(selectedFile)
        
        const endpoint = selectedFunction === 'analyze' ? 'http://127.0.0.1:8100/api/vision/analyze' :
                        selectedFunction === 'transcribe' ? 'http://127.0.0.1:8100/api/vision/transcribe' :
                        'http://127.0.0.1:8100/api/vision/redraw'

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: customPrompt,
            image_data: base64Data,
            provider: isUsingConfig ? null : selectedProvider,
            model: isUsingConfig ? null : selectedVisionModel
          })
        })

        const data = await response.json()
        setResult({
          type: selectedFunction,
          content: selectedFunction === 'transcribe' ? data.transcription : data.analysis,
          provider: data.provider_used,
          model: data.model_used,
          processing_time: data.processing_time_ms
        })
      }
    } catch (error) {
      console.error('Vision processing failed:', error)
      setResult({
        type: 'error',
        content: 'Processing failed: ' + error.message
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const copyResult = () => {
    if (result?.content) {
      navigator.clipboard.writeText(result.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const resetUpload = () => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setResult(null)
    setCustomPrompt('')
    setImagePrompt('')
  }

  if (!isActive) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Side-by-side modal for results */}
      {result && (result.type === 'transcribe' || result.type === 'analyze' || result.type === 'redraw') && (
        <div className="fixed inset-0 bg-black/90 z-50 flex">
          {/* Left side - Image */}
          <div className="w-1/2 bg-gray-900 flex items-center justify-center p-6">
            <div className="max-w-full max-h-full flex items-center justify-center">
              <img 
                src={previewUrl} 
                alt="Source" 
                className="max-w-full max-h-full object-contain"
              />
            </div>
          </div>
          
          {/* Right side - Results & Controls */}
          <div className="w-1/2 bg-gray-800 text-white flex flex-col">
            {/* Header with controls */}
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h3 className="text-xl font-semibold">
                {result.type === 'transcribe' ? '📝 Handwriting Transcription' :
                 result.type === 'analyze' ? '👁️ Image Analysis' : 
                 '🎨 Artistic Analysis'}
              </h3>
              <div className="flex items-center gap-3">
                <button
                  onClick={processVision}
                  disabled={isProcessing}
                  className="px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  title="Try another analysis"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin inline mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>🔄 Another Round</>
                  )}
                </button>
                <button
                  onClick={copyResult}
                  className="px-3 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium transition-colors"
                  title="Copy to clipboard"
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
                <button
                  onClick={() => setResult(null)}
                  className="px-3 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors"
                >
                  ✕ Close
                </button>
              </div>
            </div>
            
            {/* Content area */}
            <div className="flex-1 p-6 overflow-y-auto">
              {/* Editable content */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    {result.type === 'transcribe' ? 'Transcribed Text (Editable)' : 'Analysis Result (Editable)'}
                  </label>
                  <textarea
                    value={result.content || ''}
                    onChange={(e) => setResult(prev => ({ ...prev, content: e.target.value }))}
                    className="w-full h-64 px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Analysis result will appear here..."
                  />
                </div>
                
                {/* Metadata */}
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-700">
                  <div>
                    <span className="text-sm text-gray-400">Provider:</span>
                    <div className="font-medium">{result.provider || 'Unknown'}</div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-400">Model:</span>
                    <div className="font-medium">{result.model || 'Unknown'}</div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-400">Processing Time:</span>
                    <div className="font-medium">{result.processing_time}ms</div>
                  </div>
                  <div>
                    <span className="text-sm text-gray-400">Type:</span>
                    <div className="font-medium capitalize">{result.type}</div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Save section */}
            <div className="p-6 border-t border-gray-700 bg-gray-750">
              <button
                onClick={() => {
                  const timestamp = new Date().toISOString();
                  const content = `# ${result.type === 'transcribe' ? 'Handwriting Transcription' : 'Vision Analysis'}

## Result
${result.content}

## Metadata
- Provider: ${result.provider}
- Model: ${result.model} 
- Processing Time: ${result.processing_time}ms
- Timestamp: ${timestamp}
- Type: ${result.type}
`;
                  const blob = new Blob([content], { type: 'text/markdown' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `vision-${result.type}-${timestamp.split('T')[0]}.md`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Save Analysis as Markdown
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Function Selection */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Eye className="w-6 h-6 text-purple-400" />
          <h2 className="text-xl font-semibold">Vision Analysis</h2>
        </div>
        
        <p className="text-muted-foreground mb-6">
          Advanced image analysis, handwriting transcription, artistic interpretation, and image generation.
        </p>

        {/* Provider and Model Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-2">Vision Provider</label>
            <select
              value={selectedProvider}
              onChange={(e) => handleProviderChange(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400"
            >
              {visionProviders.map(provider => (
                <option key={provider.id} value={provider.id} className="bg-slate-900">
                  {provider.label}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Model</label>
            <select
              value={selectedVisionModel}
              onChange={(e) => handleModelChange(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400"
            >
              {currentProviderModels.map(model => (
                <option key={model.id} value={model.id} className="bg-slate-900">
                  {model.label} - {model.description}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* LLM Config Integration Status */}
        <div className={cn(
          "flex items-center justify-between p-3 rounded-lg border mb-6",
          isUsingConfig 
            ? "border-green-500/20 bg-green-500/10" 
            : "border-yellow-500/20 bg-yellow-500/10"
        )}>
          <div className="flex items-center space-x-2">
            {isUsingConfig ? (
              <>
                <Check className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-300">
                  Using saved LLM Config settings
                  {configSettings && (
                    <span className="text-green-200/60 ml-1">
                      ({configSettings.provider}/{configSettings.model})
                    </span>
                  )}
                </span>
              </>
            ) : (
              <>
                <Settings className="w-4 h-4 text-yellow-400" />
                <span className="text-sm text-yellow-300">
                  Using tab-level overrides (not saved)
                </span>
              </>
            )}
          </div>
          
          {!isUsingConfig && (
            <button
              onClick={resetToConfig}
              className="text-xs px-2 py-1 rounded bg-white/10 hover:bg-white/20 transition-colors"
            >
              Reset to Config
            </button>
          )}
        </div>

        {/* Function Tabs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {visionFunctions.map((func) => {
            const Icon = func.icon
            return (
              <button
                key={func.id}
                onClick={() => {
                  setSelectedFunction(func.id)
                  setCustomPrompt(func.defaultPrompt)
                  setResult(null)
                }}
                className={cn(
                  "p-4 rounded-lg border transition-all text-left",
                  selectedFunction === func.id
                    ? "border-purple-400 bg-purple-400/10"
                    : "border-white/10 hover:border-white/20"
                )}
              >
                <Icon className="w-5 h-5 mb-2 text-purple-400" />
                <div className="font-medium text-sm">{func.label}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {func.description}
                </div>
              </button>
            )
          })}
        </div>

        {/* Image Generation Input */}
        {selectedFunction === 'generate' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Image Prompt</label>
              <textarea
                value={imagePrompt}
                onChange={(e) => setImagePrompt(e.target.value)}
                placeholder="Describe the image you want to generate..."
                className="w-full h-24 px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none"
              />
            </div>
            
            <button
              onClick={processVision}
              disabled={isProcessing || !imagePrompt.trim()}
              className={cn(
                "px-6 py-3 rounded-lg font-medium transition-all",
                "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "flex items-center space-x-2"
              )}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <Wand2 className="w-4 h-4" />
                  <span>Generate Image</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* File Upload for Vision Analysis */}
        {selectedFunction !== 'generate' && (
          <div className="space-y-4">
            {/* File Upload Area */}
            <div 
              className={cn(
                "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
                selectedFile 
                  ? "border-green-400 bg-green-400/5" 
                  : "border-white/20 hover:border-white/40"
              )}
            >
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
                id="image-upload"
              />
              <label htmlFor="image-upload" className="cursor-pointer">
                <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <div className="text-sm font-medium">
                  {selectedFile ? selectedFile.name : 'Click to upload an image'}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  Supports JPG, PNG, GIF, WebP
                </div>
              </label>
            </div>

            {/* Image Preview */}
            {previewUrl && (
              <div className="relative">
                <img 
                  src={previewUrl} 
                  alt="Preview" 
                  className="max-w-full h-48 object-contain mx-auto rounded-lg"
                />
                <button
                  onClick={resetUpload}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                >
                  ×
                </button>
              </div>
            )}

            {/* Custom Prompt */}
            <div>
              <label className="block text-sm font-medium mb-2">Analysis Prompt</label>
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Enter your analysis prompt..."
                className="w-full h-24 px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400 resize-none"
              />
            </div>

            {/* Process Button */}
            <button
              onClick={processVision}
              disabled={isProcessing || !selectedFile || !customPrompt.trim()}
              className={cn(
                "px-6 py-3 rounded-lg font-medium transition-all",
                "bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "flex items-center space-x-2"
              )}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Eye className="w-4 h-4" />
                  <span>Analyze Image</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              {result.type === 'generation' ? 'Generated Image' : 'Analysis Results'}
            </h3>
            <div className="flex items-center space-x-2">
              {result.processing_time && (
                <span className="text-sm text-muted-foreground">
                  {result.processing_time}ms
                </span>
              )}
              {result.content && (
                <button
                  onClick={copyResult}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  {copied ? (
                    <Check className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              )}
            </div>
          </div>

          {result.type === 'generation' ? (
            <div className="space-y-4">
              <img 
                src={result.image_url} 
                alt="Generated" 
                className="max-w-full h-auto rounded-lg mx-auto"
              />
              <div className="text-sm text-muted-foreground">
                <strong>Prompt:</strong> {result.prompt_used}
              </div>
              <div className="text-sm text-muted-foreground">
                <strong>Provider:</strong> {result.provider}
              </div>
            </div>
          ) : result.type === 'error' ? (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
              <p className="text-red-400">{result.content}</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="p-4 bg-white/5 rounded-lg">
                <pre className="whitespace-pre-wrap text-sm text-muted-foreground">
                  {result.content}
                </pre>
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                {result.provider && (
                  <div><strong>Provider:</strong> {result.provider}</div>
                )}
                {result.model && (
                  <div><strong>Model:</strong> {result.model}</div>
                )}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  )
}

export default VisionAnalysis