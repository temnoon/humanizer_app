import React from 'react'
import { User, Globe, Palette, ChevronDown, Info, Sparkles, Plus, Star } from 'lucide-react'
import { cn } from '../utils'
import { useAttributes } from '../contexts/AttributeContext'

const TransformationControls = ({
  options,
  selectedPersona,
  selectedNamespace,
  selectedStyle,
  onPersonaChange,
  onNamespaceChange,
  onStyleChange
}) => {
  const { getAttributesByType, useAttribute } = useAttributes();

  // Get user-created attributes
  const userPersonas = getAttributesByType('persona');
  const userNamespaces = getAttributesByType('namespace');
  const userStyles = getAttributesByType('style');

  const handleSelection = (type, value, onChange) => {
    onChange(value);
    
    // Track usage if it's a user-created attribute
    if (value.startsWith('user_')) {
      const attributeId = value.replace('user_', '');
      useAttribute(attributeId);
    }
  };

  const SelectionCard = ({ icon: Icon, title, value, onChange, optionsList, userAttributes, symbol, type }) => {
    // Combine built-in options with user attributes
    const allOptions = [
      ...optionsList,
      ...(userAttributes.length > 0 ? [{ id: 'divider', name: '──── Your Saved Attributes ────', disabled: true }] : []),
      ...userAttributes.map(attr => ({
        id: `user_${attr.id}`,
        name: `⭐ ${attr.name}`,
        description: attr.description,
        content: attr.content,
        isUserCreated: true
      }))
    ];

    const selectedOption = allOptions.find(opt => opt.id === value);
    const isUserCreated = selectedOption?.isUserCreated;

    return (
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Icon className="w-4 h-4 text-purple-400" />
            <h3 className="font-medium">{title}</h3>
            {symbol && <span className="text-sm text-purple-300 font-mono">{symbol}</span>}
          </div>
          {userAttributes.length > 0 && (
            <div className="text-xs text-purple-300">
              {userAttributes.length} saved
            </div>
          )}
        </div>
        
        <div className="relative">
          <select
            value={value}
            onChange={(e) => handleSelection(type, e.target.value, onChange)}
            className={cn(
              "w-full px-3 py-2 pr-8 rounded-lg appearance-none",
              "bg-white/5 border border-white/10",
              "focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent",
              "transition-all cursor-pointer",
              isUserCreated && "border-yellow-400/30 bg-yellow-400/5"
            )}
          >
            {allOptions.map(option => (
              <option 
                key={option.id} 
                value={option.id} 
                className={cn(
                  "bg-slate-900",
                  option.disabled && "text-gray-500 italic",
                  option.isUserCreated && "bg-yellow-900/20"
                )}
                disabled={option.disabled}
              >
                {option.name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
          {isUserCreated && (
            <Star className="absolute right-8 top-1/2 transform -translate-y-1/2 w-4 h-4 text-yellow-400" />
          )}
        </div>
        
        {selectedOption?.description && (
          <div className={cn(
            "flex items-start space-x-2 p-3 rounded-lg",
            isUserCreated 
              ? "bg-yellow-400/10 border border-yellow-400/20" 
              : "bg-white/5"
          )}>
            {isUserCreated ? (
              <Sparkles className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
            ) : (
              <Info className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
            )}
            <div className="flex-1">
              <p className="text-sm text-muted-foreground">
                {selectedOption.description}
              </p>
              {isUserCreated && selectedOption.content && (
                <p className="text-xs text-yellow-300/80 mt-1 italic">
                  {selectedOption.content.length > 100 
                    ? selectedOption.content.substring(0, 100) + "..." 
                    : selectedOption.content}
                </p>
              )}
            </div>
          </div>
        )}
        
        {isUserCreated && (
          <div className="text-xs text-yellow-300/60 italic">
            ✨ Using your custom {type} from Attribute Studio
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Usage Tip */}
      {(userPersonas.length > 0 || userNamespaces.length > 0 || userStyles.length > 0) && (
        <div className="bg-gradient-to-r from-yellow-400/10 to-purple-400/10 border border-yellow-400/20 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Sparkles className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-yellow-100 mb-1">
                Your Custom Attributes Available!
              </h4>
              <p className="text-sm text-yellow-200/80">
                Choose from {userPersonas.length + userNamespaces.length + userStyles.length} saved attributes 
                from your Attribute Studio, or use the built-in options below.
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <SelectionCard
          icon={User}
          title="Persona"
          symbol="Ψ"
          type="persona"
          value={selectedPersona}
          onChange={onPersonaChange}
          optionsList={options.personas}
          userAttributes={userPersonas}
        />
        <SelectionCard
          icon={Globe}
          title="Namespace"
          symbol="Ω"
          type="namespace"
          value={selectedNamespace}
          onChange={onNamespaceChange}
          optionsList={options.namespaces}
          userAttributes={userNamespaces}
        />
        <SelectionCard
          icon={Palette}
          title="Style"
          symbol="Σ"
          type="style"
          value={selectedStyle}
          onChange={onStyleChange}
          optionsList={options.styles}
          userAttributes={userStyles}
        />
      </div>

      {/* Quick Access to Attribute Studio */}
      {userPersonas.length + userNamespaces.length + userStyles.length === 0 && (
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Plus className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-blue-100 mb-1">
                Create Custom Attributes
              </h4>
              <p className="text-sm text-blue-200/80">
                Visit the <strong>Attribute Studio</strong> tab to analyze text and create your own 
                personas, namespaces, and styles that will appear here for use in transformations.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransformationControls;