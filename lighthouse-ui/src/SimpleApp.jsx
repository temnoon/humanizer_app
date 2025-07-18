import React, { useState, useEffect } from "react";

function SimpleApp() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    // Test backend connectivity
    fetch("/health")
      .then(response => response.json())
      .then(data => {
        setMessage("Backend connected: " + data.status);
      })
      .catch(error => {
        setMessage("Backend error: " + error.message);
      });
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h1>Lighthouse UI - Debug Mode</h1>
      <p>{message}</p>
      <div>
        <h2>Navigation Test</h2>
        <button onClick={() => setMessage("Tab 1 clicked")}>Tab 1</button>
        <button onClick={() => setMessage("Tab 2 clicked")}>Tab 2</button>
        <button onClick={() => setMessage("Tab 3 clicked")}>Tab 3</button>
      </div>
    </div>
  );
}

export default SimpleApp;