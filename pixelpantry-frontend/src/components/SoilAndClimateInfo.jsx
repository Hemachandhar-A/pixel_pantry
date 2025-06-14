
// src/components/SoilAndClimateInfo.jsx
import React from 'react';

const SoilAndClimateInfo = ({ modelResults }) => {
  if (!modelResults) return null;
  
  // Default values in case some data is missing
  const location = modelResults.location || 'Unknown';
  const latitude = modelResults.latitude || 'N/A';
  const longitude = modelResults.longitude || 'N/A';
  const N = modelResults.N || 'Unknown';
  const P = modelResults.P || 'Unknown';
  const K = modelResults.K || 'Unknown';
  
  // Get averages from predictions if available
  let avgTemp = 'N/A';
  let avgRainfall = 'N/A';
  let avgPH = 'N/A';
  let avgHumidity = 'N/A';
  
  if (modelResults.predictions && modelResults.predictions.length > 0) {
    // Calculate averages from all predictions
    let tempSum = 0;
    let rainfallSum = 0;
    let phSum = 0;
    let humiditySum = 0;
    let count = 0;
    
    modelResults.predictions.forEach(pred => {
      if (pred.predicted_avg_temp) {
        tempSum += parseFloat(pred.predicted_avg_temp);
        count++;
      }
      if (pred.predicted_total_rainfall) rainfallSum += parseFloat(pred.predicted_total_rainfall);
      if (pred.ph) phSum += parseFloat(pred.ph);
      if (pred.humidity) humiditySum += parseFloat(pred.humidity);
    });
    
    if (count > 0) {
      avgTemp = (tempSum / count).toFixed(1) + '°C';
      avgRainfall = (rainfallSum / count).toFixed(1) + ' mm';
      avgPH = (phSum / count).toFixed(1);
      avgHumidity = (humiditySum / count).toFixed(1) + '%';
    }
  }
  
  return (
    <div className="card">
      <h2 style={{ marginBottom: '1rem', color: 'var(--dark)' }}>Soil & Climate Analysis</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.8rem', color: 'var(--primary-dark)' }}>Location</h3>
          <p><strong>Region:</strong> {location}</p>
          <p><strong>Coordinates:</strong> {latitude}, {longitude}</p>
        </div>
        
        <div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.8rem', color: 'var(--primary-dark)' }}>Soil Nutrients</h3>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ 
              padding: '0.6rem',
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              borderRadius: '4px',
              textAlign: 'center',
              flex: 1
            }}>
              <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>N</div>
              <div>{N}</div>
            </div>
            <div style={{ 
              padding: '0.6rem',
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              borderRadius: '4px',
              textAlign: 'center',
              flex: 1
            }}>
              <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>P</div>
              <div>{P}</div>
            </div>
            <div style={{ 
              padding: '0.6rem',
              backgroundColor: 'rgba(76, 175, 80, 0.1)',
              borderRadius: '4px',
              textAlign: 'center',
              flex: 1
            }}>
              <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>K</div>
              <div>{K}</div>
            </div>
          </div>
        </div>
        
        <div>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '0.8rem', color: 'var(--primary-dark)' }}>Climate Conditions</h3>
          <p><strong>Avg. Temperature:</strong> {avgTemp}</p>
          <p><strong>Total Rainfall:</strong> {avgRainfall}</p>
          <p><strong>pH Level:</strong> {avgPH}</p>
          <p><strong>Humidity:</strong> {avgHumidity}</p>
        </div>
      </div>
    </div>
  );
};

export default SoilAndClimateInfo;