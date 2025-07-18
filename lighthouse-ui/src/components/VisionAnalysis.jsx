import React, { useState } from 'react'
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
  Wand2
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
  const [selectedProvider, setSelectedProvider] = useState('google')
  const [selectedVisionModel, setSelectedVisionModel] = useState('gemini-2.5-pro')

  const visionProviders = [
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

  // Get current provider's models
  const currentProviderModels = visionProviders.find(p => p.id === selectedProvider)?.models || []
  
  // Update model when provider changes
  const handleProviderChange = (providerId) => {
    setSelectedProvider(providerId)
    const provider = visionProviders.find(p => p.id === providerId)
    if (provider && provider.models.length > 0) {
      setSelectedVisionModel(provider.models[0].id)
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
        const response = await fetch('/api/image/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: imagePrompt,
            provider: 'openai',
            size: '1024x1024',
            model: 'dall-e-3'
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
        
        const endpoint = selectedFunction === 'analyze' ? '/api/vision/analyze' :
                        selectedFunction === 'transcribe' ? '/api/vision/transcribe' :
                        '/api/vision/redraw'

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: customPrompt,
            image_data: base64Data,
            provider: selectedProvider,
            model: selectedVisionModel
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
              onChange={(e) => setSelectedVisionModel(e.target.value)}
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