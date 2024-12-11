import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setResults(null); // Clear previous results
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true); // Show loading state

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await axios.post('http://localhost:5000/predict', formData);  // Backend URL
      setResults(response.data);
    } catch (error) {
      console.error('Error uploading the image', error);
    } finally {
      setLoading(false); // Hide loading state
    }
  };

  return (
    <div className="App">
      <h1>BloodScan AI</h1>
      <form onSubmit={handleSubmit} className="upload-form">
        <input type="file" accept="image/*" onChange={handleFileChange} required />
        <button type="submit" disabled={!selectedFile || loading}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      {loading && <div className="loading">Processing your image...</div>}

      {results && (
        <div className="results">
          <h2>Results</h2>
          <div className="count-results">
            <p><strong>WBC Count:</strong> {results.WBC}</p>
            <p><strong>RBC Count:</strong> {results.RBC}</p>
            <p><strong>Platelets Count:</strong> {results.Platelets}</p>
          </div>
          <h3>Cell Size Distributions</h3>
          {results.sizeDistributions && (
            <div className="size-results">
              <p><strong>WBC Sizes:</strong> {results.sizeDistributions.WBC.join(', ')}</p>
              <p><strong>RBC Sizes:</strong> {results.sizeDistributions.RBC.join(', ')}</p>
              <p><strong>Platelet Sizes:</strong> {results.sizeDistributions.Platelets.join(', ')}</p>
            </div>
          )}

          <h3>Detected Conditions</h3>
          {results.detectedConditions && (
            <div className="condition-results">
              {results.detectedConditions.map((condition, index) => (
                <p key={index}>{condition}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
