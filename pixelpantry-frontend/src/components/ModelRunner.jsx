// src/components/ModelRunner.jsx
import React, { useState } from 'react';
import { runModel } from '../api';

const ModelRunner = ({ onModelResults, setLoading }) => {
  const [runningModel, setRunningModel] = useState(false);

  const handleRunModel = async () => {
    try {
      setRunningModel(true);
      setLoading(true);
      
      const results = await runModel();
      onModelResults(results);
      
    } catch (error) {
      console.error('Failed to run model:', error);
      alert('Failed to run model. Please try again.');
    } finally {
      setRunningModel(false);
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <h2 style={{ marginBottom: '1rem', color: 'var(--dark)' }}>Get Crop Recommendations</h2>
      <p style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
        Click the button below to analyze your soil and climate data and get personalized crop recommendations.
      </p>
      <button 
        className="btn"
        onClick={handleRunModel}
        disabled={runningModel}
        style={{ 
          padding: '0.8rem 2rem',
          fontSize: '1.1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto'
        }}
      >
        {runningModel ? (
          <>
            <span className="loading-spinner" style={{ marginRight: '0.5rem' }}></span>
            Analyzing Data...
          </>
        ) : (
          'Analyze and Recommend Crops'
        )}
      </button>
    </div>
  );
};

export default ModelRunner;