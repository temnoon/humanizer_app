import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChevronRight, 
  ChevronDown, 
  Clock, 
  Eye, 
  EyeOff, 
  Code, 
  Layers,
  ArrowRight,
  CheckCircle
} from 'lucide-react'
import { cn } from '../utils'

const TransformationSteps = ({ steps, totalDuration, isVisible }) => {
  const [expandedStep, setExpandedStep] = useState(null)
  const [showDetails, setShowDetails] = useState(false)

  const stepIcons = {
    'Deconstructing narrative': '🔍',
    'Mapping to namespace': '🗺️',
    'Reconstructing allegory': '🏗️',
    'Applying style': '🎨',
    'Generating reflection': '💭'
  }

  const stepColors = {
    'Deconstructing narrative': 'text-red-400',
    'Mapping to namespace': 'text-blue-400',
    'Reconstructing allegory': 'text-green-400',
    'Applying style': 'text-purple-400',
    'Generating reflection': 'text-yellow-400'
  }

  const toggleStep = (index) => {
    setExpandedStep(expandedStep === index ? null : index)
  }

  if (!isVisible || !steps || steps.length === 0) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Layers className="w-5 h-5 text-purple-400" />
          <h2 className="text-xl font-semibold">Transformation Process</h2>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Clock className="w-4 h-4" />
            <span>{totalDuration}ms total</span>
          </div>
          
          <button
            onClick={() => setShowDetails(!showDetails)}
            className={cn(
              "px-3 py-1 rounded-lg text-sm font-medium transition-all",
              "bg-white/5 hover:bg-white/10 border border-white/10",
              "flex items-center space-x-2"
            )}
          >
            {showDetails ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            <span>{showDetails ? 'Hide' : 'Show'} Details</span>
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-muted-foreground">Pipeline Progress</span>
          <span className="text-sm font-medium">5/5 steps completed</span>
        </div>
        <div className="w-full bg-white/5 rounded-full h-2">
          <div className="bg-gradient-to-r from-purple-500 to-cyan-500 h-2 rounded-full w-full transition-all duration-1000" />
        </div>
      </div>

      {/* Steps List */}
      <div className="space-y-3">
        {steps.map((step, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="border border-white/10 rounded-lg overflow-hidden"
          >
            <div 
              className={cn(
                "flex items-center justify-between p-4 cursor-pointer transition-all",
                "hover:bg-white/5",
                expandedStep === index && "bg-white/5"
              )}
              onClick={() => toggleStep(index)}
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-cyan-500 flex items-center justify-center text-white text-sm font-medium">
                  {index + 1}
                </div>
                
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{stepIcons[step.name]}</span>
                    <span className="font-medium">{step.name}</span>
                    <CheckCircle className="w-4 h-4 text-green-400" />
                  </div>
                  
                  <div className="flex items-center space-x-4 mt-1">
                    <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      <span>{step.duration_ms}ms</span>
                    </div>
                    
                    {showDetails && (
                      <div className="text-sm text-muted-foreground">
                        {step.metadata.step_type} transformation
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                {expandedStep === index ? (
                  <ChevronDown className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                )}
              </div>
            </div>
            
            <AnimatePresence>
              {expandedStep === index && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="border-t border-white/10 bg-white/5"
                >
                  <div className="p-4 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <ArrowRight className="w-4 h-4 text-blue-400" />
                          <span className="font-medium text-blue-400">Input</span>
                        </div>
                        <div className="p-3 bg-white/5 rounded-lg">
                          <code className="text-sm text-muted-foreground whitespace-pre-wrap">
                            {step.input_snapshot}
                          </code>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <ArrowRight className="w-4 h-4 text-green-400" />
                          <span className="font-medium text-green-400">Output</span>
                        </div>
                        <div className="p-3 bg-white/5 rounded-lg">
                          <code className="text-sm text-muted-foreground whitespace-pre-wrap">
                            {step.output_snapshot}
                          </code>
                        </div>
                      </div>
                    </div>
                    
                    {step.metadata && Object.keys(step.metadata).length > 0 && (
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <Code className="w-4 h-4 text-purple-400" />
                          <span className="font-medium text-purple-400">Metadata</span>
                        </div>
                        <div className="p-3 bg-white/5 rounded-lg">
                          <pre className="text-sm text-muted-foreground overflow-x-auto">
                            {JSON.stringify(step.metadata, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
      
      {/* Summary */}
      <div className="mt-6 p-4 bg-gradient-to-r from-purple-500/10 to-cyan-500/10 rounded-lg border border-white/10">
        <div className="flex items-center space-x-2 mb-2">
          <CheckCircle className="w-5 h-5 text-green-400" />
          <span className="font-medium">Transformation Complete</span>
        </div>
        <p className="text-sm text-muted-foreground">
          Successfully processed through all 5 stages of the Lamish Projection Engine pipeline. 
          Your narrative has been deconstructed, mapped to the target namespace, reconstructed 
          with the selected persona, stylized, and reflected upon.
        </p>
      </div>
    </motion.div>
  )
}

export default TransformationSteps