import React, { createContext, useContext, useState, useEffect } from 'react';

const AttributeContext = createContext();

export const useAttributes = () => {
  const context = useContext(AttributeContext);
  if (!context) {
    throw new Error('useAttributes must be used within an AttributeProvider');
  }
  return context;
};

export const AttributeProvider = ({ children }) => {
  const [attributes, setAttributes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load attributes from localStorage on mount
  useEffect(() => {
    loadAttributes();
  }, []);

  // Save to localStorage whenever attributes change
  useEffect(() => {
    if (!isLoading) {
      saveAttributes();
    }
  }, [attributes, isLoading]);

  const loadAttributes = () => {
    try {
      const stored = localStorage.getItem('lighthouse-attributes');
      if (stored) {
        const parsed = JSON.parse(stored);
        setAttributes(parsed);
      }
    } catch (error) {
      console.error('Failed to load attributes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveAttributes = () => {
    try {
      localStorage.setItem('lighthouse-attributes', JSON.stringify(attributes));
    } catch (error) {
      console.error('Failed to save attributes:', error);
    }
  };

  const addAttribute = (attribute) => {
    const newAttribute = {
      ...attribute,
      id: `attr_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      created: new Date().toISOString(),
      lastUsed: null,
      usageCount: 0,
      tags: attribute.tags || [],
      source: attribute.source || 'manual'
    };
    
    setAttributes(prev => [newAttribute, ...prev]);
    return newAttribute;
  };

  const updateAttribute = (id, updates) => {
    setAttributes(prev => 
      prev.map(attr => 
        attr.id === id ? { ...attr, ...updates } : attr
      )
    );
  };

  const deleteAttribute = (id) => {
    setAttributes(prev => prev.filter(attr => attr.id !== id));
  };

  const useAttribute = (id) => {
    setAttributes(prev =>
      prev.map(attr =>
        attr.id === id
          ? {
              ...attr,
              usageCount: attr.usageCount + 1,
              lastUsed: new Date().toISOString()
            }
          : attr
      )
    );
  };

  const getAttributesByType = (type) => {
    return attributes.filter(attr => attr.type === type);
  };

  const searchAttributes = (query) => {
    if (!query.trim()) return attributes;
    
    const lowercaseQuery = query.toLowerCase();
    return attributes.filter(attr =>
      attr.name.toLowerCase().includes(lowercaseQuery) ||
      attr.description.toLowerCase().includes(lowercaseQuery) ||
      attr.tags.some(tag => tag.toLowerCase().includes(lowercaseQuery)) ||
      attr.content.toLowerCase().includes(lowercaseQuery)
    );
  };

  const getAttributeChoicesForTab = (tabType) => {
    // Return attributes formatted for use in specific tabs
    switch (tabType) {
      case 'transform':
        return {
          personas: getAttributesByType('persona').map(attr => ({
            id: attr.id,
            name: attr.name,
            description: attr.description,
            value: attr.content || attr.description
          })),
          namespaces: getAttributesByType('namespace').map(attr => ({
            id: attr.id,
            name: attr.name,
            description: attr.description,
            value: attr.content || attr.description
          })),
          styles: getAttributesByType('style').map(attr => ({
            id: attr.id,
            name: attr.name,
            description: attr.description,
            value: attr.content || attr.description
          }))
        };
      
      case 'maieutic':
        return getAttributesByType('persona').map(attr => ({
          id: attr.id,
          name: attr.name,
          description: attr.description,
          content: attr.content
        }));
      
      default:
        return attributes;
    }
  };

  const exportAttributes = () => {
    const exportData = {
      exported: new Date().toISOString(),
      version: '1.0',
      attributes: attributes
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lighthouse-attributes-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const importAttributes = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          if (data.attributes && Array.isArray(data.attributes)) {
            // Add imported attributes with new IDs to avoid conflicts
            const importedAttributes = data.attributes.map(attr => ({
              ...attr,
              id: `imported_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              imported: new Date().toISOString()
            }));
            
            setAttributes(prev => [...importedAttributes, ...prev]);
            resolve(importedAttributes.length);
          } else {
            reject(new Error('Invalid attribute file format'));
          }
        } catch (error) {
          reject(error);
        }
      };
      reader.readAsText(file);
    });
  };

  const value = {
    attributes,
    isLoading,
    addAttribute,
    updateAttribute,
    deleteAttribute,
    useAttribute,
    getAttributesByType,
    searchAttributes,
    getAttributeChoicesForTab,
    exportAttributes,
    importAttributes
  };

  return (
    <AttributeContext.Provider value={value}>
      {children}
    </AttributeContext.Provider>
  );
};