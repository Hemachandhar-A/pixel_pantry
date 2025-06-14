import React, { useState } from 'react';
import './mypage.css';
import Header from './components/Header';
import ModelRunner from './components/ModelRunner';
import RecommendationCard from './components/RecommendationCard';
import SoilAndClimateInfo from './components/SoilAndClimateInfo';
import ExplanationSection from './components/ExplanationSection';
import ChatSection from './components/ChatSection';
import ShcParser from './ShcParser';

const CropAnalysis = () => {
  const [modelResults, setModelResults] = useState(null);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState('home');

  const handleModelResults = (results) => {
    setModelResults(results);
    setSelectedCrop(null);
  };

  const handleSelectCrop = (crop) => {
    setSelectedCrop(crop);
  };

  return (
    <div className='hee'>
      {/* Stylish Toggle Switch */}
      <div className="page-toggle">
        <div className="toggle-container">
          <input 
            type="checkbox" 
            id="page-switch" 
            className="toggle-checkbox" 
            checked={page === 'parser'}
            onChange={() => setPage(page === 'home' ? 'parser' : 'home')}
          />
          <label htmlFor="page-switch" className="toggle-label">
            <span className="toggle-inner">
              <span className="toggle-home">Home</span>
              <span className="toggle-parser">SHC Parser</span>
            </span>
            <span className="toggle-switch"></span>
          </label>
        </div>
      </div>

      <div className="container">
        {page === 'home' && (
          <>
            <ModelRunner onModelResults={handleModelResults} setLoading={setLoading} />
            
            {loading ? (
              <div className="card loading-container">
                <div className="loading-spinner"></div>
                <p className="loading-text">
                  Processing your data and generating recommendations...
                </p>
              </div>
            ) : (
              modelResults && (
                <>
                  <RecommendationCard
                    recommendedCrops={modelResults.recommended_crops}
                    onSelectCrop={handleSelectCrop}
                    selectedCrop={selectedCrop}
                  />
                  <SoilAndClimateInfo modelResults={modelResults} />
                  <ExplanationSection
                    selectedCrop={selectedCrop}
                    modelResults={modelResults}
                  />
                  <ChatSection modelResults={modelResults} />
                </>
              )
            )}
          </>
        )}

        {page === 'parser' && (
          <ShcParser />
        )}
      </div>
    </div>
  );
};

export default CropAnalysis;