import React from 'react'
import { motion } from 'framer-motion'
import { Brain, Hash, Sparkles } from 'lucide-react'

const DeconstructionView = ({ deconstruction }) => {
  return (
    <motion.div className="glass rounded-2xl p-8">
      <div className="flex items-center space-x-2 mb-6">
        <Brain className="w-5 h-5 text-purple-400" />
        <h2 className="text-xl font-semibold">Narrative Deconstruction</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Essence */}
        <div className="space-y-3">
          <h3 className="font-medium text-purple-300">Core Essence</h3>
          <div className="bg-white/5 rounded-lg p-4">
            <p className="text-sm leading-relaxed">{deconstruction.essence}</p>
          </div>
        </div>

        {/* Detected Layers */}
        <div className="space-y-3">
          <h3 className="font-medium text-purple-300">Detected Layers</h3>
          <div className="bg-white/5 rounded-lg p-4 space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Persona:</span>
              <span className="text-sm font-medium">{deconstruction.detected_persona}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Namespace:</span>
              <span className="text-sm font-medium">{deconstruction.detected_namespace}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Style:</span>
              <span className="text-sm font-medium">{deconstruction.detected_style}</span>
            </div>
          </div>
        </div>

        {/* Entities & Themes */}
        <div className="space-y-3">
          <h3 className="font-medium text-purple-300">Key Elements</h3>
          <div className="bg-white/5 rounded-lg p-4 space-y-3">
            {deconstruction.entities && deconstruction.entities.length > 0 && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">Entities</p>
                <div className="flex flex-wrap gap-2">
                  {deconstruction.entities.map((entity, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-500/20 text-purple-300"
                    >
                      <Hash className="w-3 h-3 mr-1" />
                      {entity}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {deconstruction.themes && deconstruction.themes.length > 0 && (
              <div>
                <p className="text-xs text-muted-foreground mb-2">Themes</p>
                <div className="flex flex-wrap gap-2">
                  {deconstruction.themes.map((theme, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-pink-500/20 text-pink-300"
                    >
                      <Sparkles className="w-3 h-3 mr-1" />
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Linguistic Features */}
        {deconstruction.linguistic_features && (
          <div className="space-y-3">
            <h3 className="font-medium text-purple-300">Linguistic Analysis</h3>
            <div className="bg-white/5 rounded-lg p-4 space-y-2">
              {Object.entries(deconstruction.linguistic_features).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="text-sm text-muted-foreground capitalize">
                    {key.replace('_', ' ')}:
                  </span>
                  <span className="text-sm font-medium">{value}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default DeconstructionView
