
// src/components/RecommendationCard.jsx
import React from 'react';

const RecommendationCard = ({ recommendedCrops, onSelectCrop, selectedCrop }) => {
  if (!recommendedCrops || recommendedCrops.length === 0) {
    return null;
  }

  return (
    <div className="card">
      <h2 style={{ marginBottom: '1rem', color: 'var(--dark)' }}>Recommended Crops</h2>
      <div style={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: '0.8rem',
        marginTop: '1rem'
      }}>
        {recommendedCrops.map((crop, index) => (
          <button 
            key={index}
            onClick={() => onSelectCrop(crop)}
            style={{
              padding: '0.6rem 1.2rem',
              borderRadius: '4px',
              border: 'none',
              cursor: 'pointer',
              backgroundColor: selectedCrop === crop ? 'var(--primary)' : 'var(--light)',
              color: selectedCrop === crop ? 'white' : 'var(--dark)',
              fontWeight: selectedCrop === crop ? '600' : '400',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            <span style={{ marginRight: '0.4rem' }}>🌱</span>
            {crop}
          </button>
        ))}
      </div>
      <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
        Select a crop to see detailed explanation
      </p>
    </div>
  );
};

export default RecommendationCard;
