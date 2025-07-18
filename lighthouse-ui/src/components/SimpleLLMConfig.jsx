import React, { useState, useEffect } from "react";

const SimpleLLMConfig = () => {
  const [configs, setConfigs] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const response = await fetch("/api/llm/configurations");
        if (response.ok) {
          const data = await response.json();
          setConfigs(data);
        } else {
          setError("Failed to load configurations");
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return <div className="p-8">Loading LLM configurations...</div>;
  }

  if (error) {
    return <div className="p-8 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">LLM Configuration</h1>
      <div className="bg-gray-100 p-4 rounded">
        <p>LLM Configuration loaded successfully!</p>
        <p>Available providers: {configs.available_providers?.length || 0}</p>
        <p>Configured tasks: {Object.keys(configs.task_configs || {}).length}</p>
      </div>
    </div>
  );
};

export default SimpleLLMConfig;