import React from 'react'
import { Send } from 'lucide-react'
import { cn } from '../utils'

const NarrativeInput = ({ value, onChange, onTransform, isProcessing, placeholder }) => {
  const examples = [
    "The team struggled with the deadline, but their determination saw them through.",
    "She watched the sunset paint the sky in shades of gold and crimson.",
    "The algorithm efficiently sorted through millions of data points.",
    "Democracy requires active participation from informed citizens."
  ]

  const handleExample = (example) => {
    onChange(example)
  }

  return (
    <div className="space-y-4">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || "Enter any text - a story, an article, a thought..."}
        className={cn(
          "w-full h-32 px-4 py-3 rounded-lg",
          "bg-white/5 border border-white/10",
          "placeholder:text-muted-foreground/50",
          "focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent",
          "resize-none transition-all"
        )}
      />
      
      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-2">
          <span className="text-sm text-muted-foreground">Try an example:</span>
          {examples.map((example, idx) => (
            <button
              key={idx}
              onClick={() => handleExample(example)}
              className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
            >
              Example {idx + 1}
            </button>
          ))}
        </div>
        
        {onTransform && (
          <button
            onClick={onTransform}
            disabled={!value.trim() || isProcessing}
            className={cn(
              "flex items-center space-x-2 px-6 py-2 rounded-lg",
              "bg-gradient-to-r from-purple-500 to-pink-500",
              "hover:from-purple-600 hover:to-pink-600",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "transition-all transform hover:scale-105",
              "focus:outline-none focus:ring-2 focus:ring-purple-400"
            )}
          >
            <span>Quick Transform</span>
            <Send className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  )
}

export default NarrativeInput
