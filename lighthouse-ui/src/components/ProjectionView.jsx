import React from 'react'
import { motion } from 'framer-motion'
import { Wand2, Copy, Check, Shield } from 'lucide-react'
import { cn } from '../utils'

const ProjectionView = ({ projection, onCopy, copied }) => {
  return (
    <motion.div className="glass rounded-2xl p-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Wand2 className="w-5 h-5 text-purple-400" />
          <h2 className="text-xl font-semibold">Transformed Narrative</h2>
        </div>
        <button
          onClick={onCopy}
          className={cn(
            "flex items-center space-x-2 px-3 py-1.5 rounded-lg",
            "bg-white/5 hover:bg-white/10 transition-colors",
            "text-sm focus:outline-none focus:ring-2 focus:ring-purple-400"
          )}
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-green-400" />
              <span>Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      <div className="space-y-6">
        {/* Transformed Text */}
        <div className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-lg p-6 border border-purple-500/20">
          <p className="text-lg leading-relaxed whitespace-pre-wrap">
            {projection.narrative}
          </p>
        </div>

        {/* Transformation Metadata */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {projection.metadata && Object.entries(projection.metadata).map(([key, value]) => {
            if (key === 'timestamp') return null
            return (
              <div key={key} className="bg-white/5 rounded-lg p-3">
                <p className="text-xs text-muted-foreground capitalize mb-1">
                  {key.replace('_', ' ')}
                </p>
                <p className="text-sm font-medium">{value}</p>
              </div>
            )
          })}
        </div>

        {/* Diff Summary */}
        {projection.diff_summary && (
          <div className="bg-white/5 rounded-lg p-4">
            <h3 className="font-medium text-purple-300 mb-3">Transformation Impact</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              {Object.entries(projection.diff_summary).map(([key, value]) => (
                <div key={key}>
                  <p className="text-2xl font-bold text-purple-400">{value}</p>
                  <p className="text-xs text-muted-foreground capitalize">
                    {key.replace('_', ' ')}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lamish Pulse Signature */}
        {projection.lamish_pulse_signature && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg p-4 border border-purple-500/20"
          >
            <div className="flex items-center space-x-2 mb-2">
              <Shield className="w-4 h-4 text-purple-400" />
              <h4 className="font-medium text-sm">Lamish Pulse Signature</h4>
            </div>
            <div className="font-mono text-xs text-muted-foreground break-all">
              {projection.lamish_pulse_signature.text_hash?.substring(0, 32)}...
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

export default ProjectionView
