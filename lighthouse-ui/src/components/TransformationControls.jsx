import React from 'react'
import { User, Globe, Palette, ChevronDown, Info } from 'lucide-react'
import { cn } from '../utils'

const TransformationControls = ({
  options,
  selectedPersona,
  selectedNamespace,
  selectedStyle,
  onPersonaChange,
  onNamespaceChange,
  onStyleChange
}) => {
  const SelectionCard = ({ icon: Icon, title, value, onChange, optionsList, symbol }) => (
    <div className="space-y-3">
      <div className="flex items-center space-x-2">
        <Icon className="w-4 h-4 text-purple-400" />
        <h3 className="font-medium">{title}</h3>
        {symbol && <span className="text-sm text-purple-300 font-mono">{symbol}</span>}
      </div>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={cn(
            "w-full px-3 py-2 pr-8 rounded-lg appearance-none",
            "bg-white/5 border border-white/10",
            "focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent",
            "transition-all cursor-pointer"
          )}
        >
          {optionsList.map(option => (
            <option key={option.id} value={option.id} className="bg-slate-900">
              {option.name}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
      </div>
      {optionsList.find(opt => opt.id === value)?.description && (
        <div className="flex items-start space-x-2 p-2 bg-white/5 rounded-lg">
          <Info className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-muted-foreground">
            {optionsList.find(opt => opt.id === value)?.description}
          </p>
        </div>
      )}
    </div>
  )

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <SelectionCard
        icon={User}
        title="Persona"
        symbol="Ψ"
        value={selectedPersona}
        onChange={onPersonaChange}
        optionsList={options.personas}
      />
      <SelectionCard
        icon={Globe}
        title="Namespace"
        symbol="Ω"
        value={selectedNamespace}
        onChange={onNamespaceChange}
        optionsList={options.namespaces}
      />
      <SelectionCard
        icon={Palette}
        title="Style"
        symbol="Σ"
        value={selectedStyle}
        onChange={onStyleChange}
        optionsList={options.styles}
      />
    </div>
  )
}

export default TransformationControls