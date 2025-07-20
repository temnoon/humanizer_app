import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Languages, 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Globe, 
  ArrowRightLeft, 
  Loader2, 
  CheckCircle, 
  AlertCircle,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { cn } from '../utils'

const TranslationAnalysis = ({ narrative, isActive }) => {
  const [selectedLanguage, setSelectedLanguage] = useState('spanish')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [stabilityResult, setStabilityResult] = useState(null)
  const [showStabilityAnalysis, setShowStabilityAnalysis] = useState(false)
  const [selectedLanguages, setSelectedLanguages] = useState(['spanish', 'french', 'german'])

  const supportedLanguages = [
    'spanish', 'french', 'german', 'italian', 'portuguese', 'russian',
    'chinese', 'japanese', 'korean', 'arabic', 'hebrew', 'hindi',
    'dutch', 'swedish', 'norwegian', 'danish', 'polish', 'czech'
  ]

  const performRoundTripAnalysis = async () => {
    if (!narrative.trim()) return

    setIsAnalyzing(true)
    try {
      const response = await fetch('http://127.0.0.1:8100/translation/roundtrip', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: narrative,
          intermediate_language: selectedLanguage,
          source_language: 'english'
        })
      })

      if (!response.ok) {
        throw new Error(`Translation failed: ${response.status}`)
      }

      const data = await response.json()
      setAnalysisResult(data)
    } catch (error) {
      console.error('Translation analysis failed:', error)
      alert(`Translation analysis failed: ${error.message}`)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const performStabilityAnalysis = async () => {
    if (!narrative.trim()) return

    setIsAnalyzing(true)
    try {
      const response = await fetch('http://127.0.0.1:8100/translation/stability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: narrative,
          test_languages: selectedLanguages
        })
      })

      const data = await response.json()
      setStabilityResult(data)
      setShowStabilityAnalysis(true)
    } catch (error) {
      console.error('Stability analysis failed:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getDriftColor = (drift) => {
    if (drift >= 0.8) return 'text-green-400'
    if (drift >= 0.6) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getDriftDescription = (drift) => {
    if (drift >= 0.8) return 'Excellent preservation'
    if (drift >= 0.6) return 'Good preservation'
    if (drift >= 0.4) return 'Moderate drift'
    return 'Significant drift'
  }

  if (!isActive) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <Languages className="w-6 h-6 text-purple-400" />
          <h2 className="text-xl font-semibold">Translation Analysis</h2>
        </div>
        
        <p className="text-muted-foreground mb-6">
          Analyze semantic stability through round-trip translation. Text is translated to an intermediate 
          language and back to English to reveal what meaning persists across linguistic boundaries.
        </p>

        {/* Single Language Analysis */}
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-2">Intermediate Language</label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 focus:outline-none focus:ring-2 focus:ring-purple-400"
              >
                {supportedLanguages.map(lang => (
                  <option key={lang} value={lang} className="bg-slate-900 capitalize">
                    {lang}
                  </option>
                ))}
              </select>
            </div>
            
            <button
              onClick={performRoundTripAnalysis}
              disabled={isAnalyzing || !narrative.trim()}
              className={cn(
                "px-4 py-2 rounded-lg font-medium transition-all",
                "bg-purple-600 hover:bg-purple-700 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "flex items-center space-x-2"
              )}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <ArrowRightLeft className="w-4 h-4" />
                  <span>Analyze</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Multi-Language Stability Analysis */}
        <div className="mt-6 pt-6 border-t border-white/10">
          <h3 className="font-medium mb-4">Multi-Language Stability Analysis</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Test Languages</label>
              <div className="flex flex-wrap gap-2">
                {supportedLanguages.slice(0, 12).map(lang => (
                  <button
                    key={lang}
                    onClick={() => {
                      setSelectedLanguages(prev => 
                        prev.includes(lang) 
                          ? prev.filter(l => l !== lang)
                          : [...prev, lang]
                      )
                    }}
                    className={cn(
                      "px-3 py-1 rounded-lg text-sm font-medium transition-all capitalize",
                      selectedLanguages.includes(lang)
                        ? "bg-purple-600 text-white"
                        : "bg-white/5 text-muted-foreground hover:bg-white/10"
                    )}
                  >
                    {lang}
                  </button>
                ))}
              </div>
            </div>
            
            <button
              onClick={performStabilityAnalysis}
              disabled={isAnalyzing || !narrative.trim() || selectedLanguages.length === 0}
              className={cn(
                "px-4 py-2 rounded-lg font-medium transition-all",
                "bg-blue-600 hover:bg-blue-700 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "flex items-center space-x-2"
              )}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Analyzing stability...</span>
                </>
              ) : (
                <>
                  <BarChart3 className="w-4 h-4" />
                  <span>Analyze Stability</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Single Language Results */}
      {analysisResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <ArrowRightLeft className="w-5 h-5 text-purple-400" />
              <h3 className="text-lg font-semibold">Round-trip Analysis Results</h3>
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-blue-400 capitalize">{analysisResult.intermediate_language}</span>
              </div>
            </div>
            <button
              onClick={performRoundTripAnalysis}
              disabled={isAnalyzing || !narrative.trim()}
              className={cn(
                "px-3 py-2 rounded-lg text-sm font-medium transition-all",
                "bg-purple-600 hover:bg-purple-700 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "flex items-center space-x-2"
              )}
              title="Reanalyze with current settings"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Reanalyzing...</span>
                </>
              ) : (
                <>
                  <ArrowRightLeft className="w-3 h-3" />
                  <span>Another Round</span>
                </>
              )}
            </button>
          </div>

          {/* Semantic Drift Score */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Semantic Preservation Score</span>
              <span className={cn("text-lg font-bold", getDriftColor(analysisResult.semantic_drift))}>
                {(analysisResult.semantic_drift * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-white/5 rounded-full h-2">
              <div 
                className={cn(
                  "h-2 rounded-full transition-all duration-1000",
                  analysisResult.semantic_drift >= 0.8 ? "bg-green-400" :
                  analysisResult.semantic_drift >= 0.6 ? "bg-yellow-400" : "bg-red-400"
                )}
                style={{ width: `${analysisResult.semantic_drift * 100}%` }}
              />
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              {getDriftDescription(analysisResult.semantic_drift)}
            </p>
          </div>

          {/* Text Comparison - Three Steps */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="w-4 h-4 text-blue-400" />
                <span className="font-medium text-blue-400">Original (English)</span>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  {analysisResult.original_text}
                </p>
              </div>
            </div>
            
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Globe className="w-4 h-4 text-purple-400" />
                <span className="font-medium text-purple-400 capitalize">
                  Forward ({analysisResult.intermediate_language})
                </span>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  {analysisResult.forward_translation}
                </p>
              </div>
            </div>
            
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <ArrowRightLeft className="w-4 h-4 text-green-400" />
                <span className="font-medium text-green-400">Back-translated (English)</span>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <p className="text-sm text-muted-foreground">
                  {analysisResult.final_text}
                </p>
              </div>
            </div>
          </div>

          {/* Element Analysis */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="font-medium text-green-400">Preserved Elements</span>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <ul className="space-y-1">
                  {analysisResult.preserved_elements.map((element, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start space-x-2">
                      <span className="text-green-400 mt-1">•</span>
                      <span>{element}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <TrendingDown className="w-4 h-4 text-red-400" />
                <span className="font-medium text-red-400">Lost Elements</span>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <ul className="space-y-1">
                  {analysisResult.lost_elements.map((element, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start space-x-2">
                      <span className="text-red-400 mt-1">•</span>
                      <span>{element}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-4 h-4 text-blue-400" />
                <span className="font-medium text-blue-400">Gained Elements</span>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <ul className="space-y-1">
                  {analysisResult.gained_elements.map((element, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start space-x-2">
                      <span className="text-blue-400 mt-1">•</span>
                      <span>{element}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Stability Analysis Results */}
      {stabilityResult && showStabilityAnalysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <BarChart3 className="w-5 h-5 text-blue-400" />
              <h3 className="text-lg font-semibold">Semantic Stability Analysis</h3>
            </div>
            <button
              onClick={performStabilityAnalysis}
              disabled={isAnalyzing || !narrative.trim() || selectedLanguages.length === 0}
              className={cn(
                "px-3 py-2 rounded-lg text-sm font-medium transition-all",
                "bg-blue-600 hover:bg-blue-700 text-white",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "flex items-center space-x-2"
              )}
              title="Reanalyze stability with current settings"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Reanalyzing...</span>
                </>
              ) : (
                <>
                  <BarChart3 className="w-3 h-3" />
                  <span>Another Analysis</span>
                </>
              )}
            </button>
          </div>

          {/* Overall Stability Score */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Overall Stability Score</span>
              <span className={cn("text-lg font-bold", getDriftColor(stabilityResult.stability_score))}>
                {(stabilityResult.stability_score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-white/5 rounded-full h-2">
              <div 
                className={cn(
                  "h-2 rounded-full transition-all duration-1000",
                  stabilityResult.stability_score >= 0.8 ? "bg-green-400" :
                  stabilityResult.stability_score >= 0.6 ? "bg-yellow-400" : "bg-red-400"
                )}
                style={{ width: `${stabilityResult.stability_score * 100}%` }}
              />
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Average drift: {(stabilityResult.average_drift * 100).toFixed(1)}%
            </p>
          </div>

          {/* Language-specific Results */}
          <div className="mb-6">
            <h4 className="font-medium mb-3">Language-specific Preservation</h4>
            <div className="space-y-2">
              {Object.entries(stabilityResult.language_results).map(([lang, score]) => (
                <div key={lang} className="flex items-center space-x-3">
                  <div className="w-20 text-sm font-medium capitalize">{lang}</div>
                  <div className="flex-1 bg-white/5 rounded-full h-2">
                    <div 
                      className={cn(
                        "h-2 rounded-full transition-all duration-1000",
                        score >= 0.8 ? "bg-green-400" :
                        score >= 0.6 ? "bg-yellow-400" : "bg-red-400"
                      )}
                      style={{ width: `${score * 100}%` }}
                    />
                  </div>
                  <div className={cn("text-sm font-medium w-12", getDriftColor(score))}>
                    {(score * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Most Stable/Volatile Elements */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="font-medium text-green-400">Most Stable Elements</span>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <ul className="space-y-1">
                  {stabilityResult.most_stable_elements.map((element, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start space-x-2">
                      <span className="text-green-400 mt-1">•</span>
                      <span>{element}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <AlertCircle className="w-4 h-4 text-orange-400" />
                <span className="font-medium text-orange-400">Most Volatile Elements</span>
              </div>
              <div className="p-3 bg-white/5 rounded-lg">
                <ul className="space-y-1">
                  {stabilityResult.most_volatile_elements.map((element, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start space-x-2">
                      <span className="text-orange-400 mt-1">•</span>
                      <span>{element}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default TranslationAnalysis