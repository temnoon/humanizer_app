import React, { useState, useEffect } from 'react';
import './SimpleTransformApp.css';

const SimpleTransformApp = () => {
  // Core state
  const [narrative, setNarrative] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [activeView, setActiveView] = useState('transform');
  
  // Configuration state
  const [personas, setPersonas] = useState([]);
  const [namespaces, setNamespaces] = useState([]);
  const [styles, setStyles] = useState([]);
  const [selectedPersona, setSelectedPersona] = useState('philosopher');
  const [selectedNamespace, setSelectedNamespace] = useState('lamish-galaxy');
  const [selectedStyle, setSelectedStyle] = useState('poetic');
  
  // Archive state
  const [narrativeArchive, setNarrativeArchive] = useState([]);
  const [attributeArchive, setAttributeArchive] = useState([]);
  const [meaningVectors, setMeaningVectors] = useState([]);
  
  // Load initial data
  useEffect(() => {
    loadConfigurations();
    loadArchives();
  }, []);

  const loadConfigurations = async () => {
    try {
      const response = await fetch('/configurations');
      const data = await response.json();
      setPersonas(data.personas || []);
      setNamespaces(data.namespaces || []);
      setStyles(data.styles || []);
    } catch (error) {
      console.error('Failed to load configurations:', error);
    }
  };

  const loadArchives = () => {
    // Mock data for now - in real implementation would load from backend
    setNarrativeArchive([
      {
        id: 1,
        text: "The traveler walked through the ancient forest...",
        persona: "storyteller",
        namespace: "medieval-realm",
        style: "poetic",
        timestamp: "2024-01-15T10:30:00Z",
        meaningVector: [0.8, 0.3, 0.9, 0.1, 0.7]
      },
      {
        id: 2,
        text: "Data flows through neural pathways like rivers...",
        persona: "scientist",
        namespace: "cyberpunk-future",
        style: "technical",
        timestamp: "2024-01-14T15:45:00Z",
        meaningVector: [0.2, 0.9, 0.4, 0.8, 0.3]
      }
    ]);

    setAttributeArchive([
      { persona: "philosopher", usage: 45, lastUsed: "2024-01-15" },
      { persona: "storyteller", usage: 32, lastUsed: "2024-01-14" },
      { persona: "scientist", usage: 28, lastUsed: "2024-01-13" }
    ]);

    setMeaningVectors([
      { narrative: "Ancient wisdom", vector: [0.9, 0.1, 0.8, 0.2, 0.7], cluster: "philosophical" },
      { narrative: "Future technology", vector: [0.1, 0.9, 0.3, 0.8, 0.4], cluster: "technical" },
      { narrative: "Natural beauty", vector: [0.7, 0.3, 0.9, 0.1, 0.8], cluster: "aesthetic" }
    ]);
  };

  const handleTransform = async () => {
    if (!narrative.trim()) return;
    
    setIsProcessing(true);
    try {
      const response = await fetch('/transform', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          narrative,
          target_persona: selectedPersona,
          target_namespace: selectedNamespace,
          target_style: selectedStyle
        })
      });
      
      const data = await response.json();
      setResult(data);
      
      // Add to archive
      const newEntry = {
        id: Date.now(),
        text: narrative,
        persona: selectedPersona,
        namespace: selectedNamespace,
        style: selectedStyle,
        timestamp: new Date().toISOString(),
        result: data.projection?.narrative,
        meaningVector: data.projection?.embedding?.slice(0, 5) || [Math.random(), Math.random(), Math.random(), Math.random(), Math.random()]
      };
      setNarrativeArchive(prev => [newEntry, ...prev.slice(0, 9)]); // Keep last 10
      
    } catch (error) {
      console.error('Transform failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const calculateSimilarity = (vector1, vector2) => {
    if (!vector1 || !vector2) return 0;
    const dotProduct = vector1.reduce((sum, val, i) => sum + val * (vector2[i] || 0), 0);
    const magnitude1 = Math.sqrt(vector1.reduce((sum, val) => sum + val * val, 0));
    const magnitude2 = Math.sqrt(vector2.reduce((sum, val) => sum + val * val, 0));
    return magnitude1 && magnitude2 ? dotProduct / (magnitude1 * magnitude2) : 0;
  };

  const getOptimalExpression = (currentNarrative) => {
    if (!currentNarrative || narrativeArchive.length === 0) return null;
    
    // Simple mock - find most similar narrative in archive
    const similarities = narrativeArchive.map(entry => ({
      ...entry,
      similarity: Math.random() * 0.8 + 0.2 // Mock similarity
    }));
    
    return similarities.sort((a, b) => b.similarity - a.similarity).slice(0, 3);
  };

  return (
    <div className="simple-transform-app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">🏠</div>
            <h1>Lighthouse Transform</h1>
          </div>
          <nav className="main-nav">
            <button 
              className={`nav-btn ${activeView === 'transform' ? 'active' : ''}`}
              onClick={() => setActiveView('transform')}
            >
              Transform
            </button>
            <button 
              className={`nav-btn ${activeView === 'archive' ? 'active' : ''}`}
              onClick={() => setActiveView('archive')}
            >
              Archive
            </button>
            <button 
              className={`nav-btn ${activeView === 'vectors' ? 'active' : ''}`}
              onClick={() => setActiveView('vectors')}
            >
              Vectors
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {activeView === 'transform' && (
          <div className="transform-view">
            {/* Input Section */}
            <section className="input-section">
              <h2>Transform Narrative</h2>
              <textarea
                value={narrative}
                onChange={(e) => setNarrative(e.target.value)}
                placeholder="Enter your narrative to transform..."
                className="narrative-input"
                rows={6}
              />
              
              {/* Configuration */}
              <div className="config-grid">
                <div className="config-item">
                  <label>Persona</label>
                  <select value={selectedPersona} onChange={(e) => setSelectedPersona(e.target.value)}>
                    {personas.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
                <div className="config-item">
                  <label>Namespace</label>
                  <select value={selectedNamespace} onChange={(e) => setSelectedNamespace(e.target.value)}>
                    {namespaces.map(n => (
                      <option key={n.id} value={n.id}>{n.name}</option>
                    ))}
                  </select>
                </div>
                <div className="config-item">
                  <label>Style</label>
                  <select value={selectedStyle} onChange={(e) => setSelectedStyle(e.target.value)}>
                    {styles.map(s => (
                      <option key={s.id} value={s.id}>{s.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <button 
                onClick={handleTransform}
                disabled={isProcessing || !narrative.trim()}
                className="transform-btn"
              >
                {isProcessing ? '🔄 Processing...' : '✨ Transform'}
              </button>
            </section>

            {/* Results Section */}
            {result && (
              <section className="results-section">
                <h2>Transformed Result</h2>
                <div className="result-content">
                  <div className="original">
                    <h3>Original</h3>
                    <p>{narrative}</p>
                  </div>
                  <div className="arrow">→</div>
                  <div className="transformed">
                    <h3>Transformed</h3>
                    <p>{result.projection?.narrative}</p>
                  </div>
                </div>
                
                {/* Optimal Expression Suggestions */}
                <div className="optimal-suggestions">
                  <h3>Similar Expressions</h3>
                  {getOptimalExpression(narrative)?.map(suggestion => (
                    <div key={suggestion.id} className="suggestion">
                      <div className="suggestion-meta">
                        <span className="persona">{suggestion.persona}</span>
                        <span className="similarity">{(suggestion.similarity * 100).toFixed(1)}% similar</span>
                      </div>
                      <p className="suggestion-text">{suggestion.text.substring(0, 100)}...</p>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}

        {activeView === 'archive' && (
          <div className="archive-view">
            <h2>Narrative Archive</h2>
            
            {/* Archive Stats */}
            <div className="archive-stats">
              <div className="stat">
                <span className="stat-number">{narrativeArchive.length}</span>
                <span className="stat-label">Narratives</span>
              </div>
              <div className="stat">
                <span className="stat-number">{new Set(narrativeArchive.map(n => n.persona)).size}</span>
                <span className="stat-label">Personas Used</span>
              </div>
              <div className="stat">
                <span className="stat-number">{new Set(narrativeArchive.map(n => n.namespace)).size}</span>
                <span className="stat-label">Namespaces</span>
              </div>
            </div>

            {/* Archive List */}
            <div className="archive-list">
              {narrativeArchive.map(entry => (
                <div key={entry.id} className="archive-entry">
                  <div className="entry-header">
                    <div className="entry-meta">
                      <span className="persona">{entry.persona}</span>
                      <span className="namespace">{entry.namespace}</span>
                      <span className="style">{entry.style}</span>
                    </div>
                    <span className="timestamp">
                      {new Date(entry.timestamp).toLocaleDateString()}
                    </span>
                  </div>
                  <p className="entry-text">{entry.text}</p>
                  {entry.result && (
                    <div className="entry-result">
                      <span className="result-label">→</span>
                      <p>{entry.result}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeView === 'vectors' && (
          <div className="vectors-view">
            <h2>Meaning Vectors</h2>
            
            {/* Vector Visualization */}
            <div className="vector-grid">
              {meaningVectors.map((item, index) => (
                <div key={index} className="vector-item">
                  <h3>{item.narrative}</h3>
                  <div className="vector-display">
                    {item.vector.map((val, i) => (
                      <div key={i} className="vector-component">
                        <div 
                          className="vector-bar"
                          style={{ height: `${val * 100}%` }}
                        ></div>
                        <span className="vector-value">{val.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                  <span className="cluster-label">{item.cluster}</span>
                </div>
              ))}
            </div>

            {/* Current Narrative Vector */}
            {result?.projection?.embedding && (
              <div className="current-vector">
                <h3>Current Narrative Vector</h3>
                <div className="vector-display">
                  {result.projection.embedding.slice(0, 5).map((val, i) => (
                    <div key={i} className="vector-component">
                      <div 
                        className="vector-bar current"
                        style={{ height: `${Math.abs(val) * 100}%` }}
                      ></div>
                      <span className="vector-value">{val.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default SimpleTransformApp;