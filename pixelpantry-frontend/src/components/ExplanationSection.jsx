
// src/components/ExplanationSection.jsx
import React, { useState, useEffect } from 'react';
import { getExplanation } from '../api';

const ExplanationSection = ({ selectedCrop, modelResults }) => {
  const [explanation, setExplanation] = useState('');
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    if (selectedCrop && modelResults) {
      fetchExplanation();
    } else {
      setExplanation('');
    }
    
    async function fetchExplanation() {
      setLoading(true);
      try {
        // Get first prediction for climate data
        const firstPrediction = modelResults.predictions && modelResults.predictions.length > 0 
          ? modelResults.predictions[0] 
          : {};
          
        // Prepare crop data with all available context
        const cropData = {
          crop: selectedCrop,
          location: modelResults.location,
          N: modelResults.N,
          P: modelResults.P,
          K: modelResults.K,
          predicted_avg_temp: firstPrediction.predicted_avg_temp,
          predicted_total_rainfall: firstPrediction.predicted_total_rainfall,
          ph: firstPrediction.ph,
          humidity: firstPrediction.humidity
        };
        
        const result = await getExplanation(cropData);
        setExplanation(result.explanation || 'No explanation available.');
      } catch (error) {
        console.error('Error fetching explanation:', error);
        setExplanation('Failed to fetch explanation. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  }, [selectedCrop, modelResults]);
  
  if (!selectedCrop) {
    return (
      <div className="card" style={{ backgroundColor: 'var(--light)', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--dark)', marginBottom: '1rem' }}>Crop Information</h2>
        <p>Select a recommended crop to see detailed information</p>
      </div>
    );
  }
  
  return (
    <div className="card">
      <h2 style={{ color: 'var(--dark)', marginBottom: '1rem', display: 'flex', alignItems: 'center' }}>
        <span style={{ marginRight: '0.5rem' }}>🌱</span>
        Why {selectedCrop} Is Recommended
      </h2>
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div className="loading-spinner" style={{ 
            width: '2rem', 
            height: '2rem', 
            border: '3px solid rgba(76, 175, 80, 0.3)',
            borderTopColor: 'var(--primary)'
          }}></div>
          <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>
            Generating explanation...
          </p>
        </div>
      ) : (
        <div style={{ lineHeight: '1.7' }}>
          {explanation.split('\n').map((paragraph, index) => (
            <p key={index} style={{ marginBottom: '1rem' }}>{paragraph}</p>
          ))}
        </div>
      )}
    </div>
  );
};

export default ExplanationSection;
