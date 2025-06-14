
// src/components/Header.jsx
import React from 'react';

const Header = () => {
  return (
    <header style={{ 
      color: 'white',
      padding: '1.5rem',
      textAlign: 'center',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>CropSmart</h1>
      <p style={{ fontSize: '1.1rem', opacity: '0.9' }}>
        Intelligent Crop Recommendation System for Optimized Farming
      </p>
    </header>
  );
};

export default Header;
