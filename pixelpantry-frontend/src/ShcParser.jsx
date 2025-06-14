import React, { useState, useEffect } from 'react';
import './ShcParser.css';

function ShcParser() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [serverStatus, setServerStatus] = useState(null);

  // Check if the server is running when the component mounts
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/health', {
          method: 'GET',
          mode: 'cors'
        });
        
        if (response.ok) {
          setServerStatus('connected');
        } else {
          setServerStatus('error');
        }
      } catch (err) {
        setServerStatus('error');
        console.error('Server health check failed:', err);
      }
    };

    checkServerStatus();
  }, []);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError(null);
    setParsedData(null);
    
    if (selectedFile) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file");
      return;
    }

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/parse-shc', {
        method: 'POST',
        body: formData,
        mode: 'cors',
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`${response.status}: ${errorData.error || response.statusText}`);
      }

      const data = await response.json();
      setParsedData(data);
    } catch (err) {
      console.error('Error details:', err);
      setError(`Failed to parse SHC: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getNutrientStatusClass = (value, nutrient) => {
    if (value === null || value === undefined) return '';
    
    // These are general thresholds and should be adjusted based on actual recommendations
    const thresholds = {
      'pH': { low: 6.0, high: 8.5 },
      'EC': { low: 0.8, high: 1.6 },
      'OC': { low: 0.5, high: 0.75 },
      'N': { low: 280, high: 560 },
      'P': { low: 10, high: 25 },
      'K': { low: 108, high: 280 },
      'S': { low: 10, high: 20 },
      'Zn': { low: 0.6, high: 1.2 },
      'Fe': { low: 4.5, high: 9.0 },
      'Cu': { low: 0.2, high: 0.4 },
      'Mn': { low: 2.0, high: 4.0 },
      'B': { low: 0.5, high: 1.0 },
    };
    
    if (!thresholds[nutrient]) return '';
    
    if (value < thresholds[nutrient].low) {
      return 'status-low';
    } else if (value > thresholds[nutrient].high) {
      return 'status-high';
    } else {
      return 'status-medium';
    }
  };

  const getNutrientStatusText = (value, nutrient) => {
    if (value === null || value === undefined) return 'Not found';
    
    const className = getNutrientStatusClass(value, nutrient);
    if (className === 'status-low') {
      return `${value} (Low)`;
    } else if (className === 'status-high') {
      return `${value} (High)`;
    } else if (className === 'status-medium') {
      return `${value} (Medium)`;
    } else {
      return value;
    }
  };

  const getFertilizerRecommendation = (nutrientValues) => {
    if (!nutrientValues) return null;
    
    let recommendations = [];
    
    // Simple logic for recommendations based on nutrient values
    if (nutrientValues.N?.value !== undefined && nutrientValues.N.value < 280) {
      recommendations.push("Apply nitrogen-rich fertilizers like urea or ammonium sulfate");
    }
    
    if (nutrientValues.P?.value !== undefined && nutrientValues.P.value < 10) {
      recommendations.push("Apply phosphorus fertilizers like single superphosphate (SSP) or diammonium phosphate (DAP)");
    }
    
    if (nutrientValues.K?.value !== undefined && nutrientValues.K.value < 108) {
      recommendations.push("Apply potassium fertilizers like muriate of potash (MOP) or sulfate of potash (SOP)");
    }
    
    if (nutrientValues.S?.value !== undefined && nutrientValues.S.value < 10) {
      recommendations.push("Apply sulfur-containing fertilizers like ammonium sulfate or gypsum");
    }
    
    if (nutrientValues.Zn?.value !== undefined && nutrientValues.Zn.value < 0.6) {
      recommendations.push("Apply zinc sulfate as a micronutrient supplement");
    }
    
    if (nutrientValues.B?.value !== undefined && nutrientValues.B.value < 0.5) {
      recommendations.push("Apply borax as a micronutrient supplement");
    }
    
    if (nutrientValues.pH?.value !== undefined && nutrientValues.pH.value < 6.0) {
      recommendations.push("Apply lime to increase soil pH");
    } else if (nutrientValues.pH?.value !== undefined && nutrientValues.pH.value > 8.5) {
      recommendations.push("Apply gypsum to decrease soil pH");
    }
    
    return recommendations.length > 0 ? recommendations : ["No specific fertilizer recommendations based on current values"];
  };

  return (
    <div className="shc-container">
      <div className="shc-card">
        <div className="shc-header">
          <div className="shc-logo">SH</div>
          <div className="shc-title">
            <h2>Soil Health Card Parser</h2>
            <p>Upload a Soil Health Card image to extract information using Google Cloud Vision API</p>
            {serverStatus === 'error' && (
              <div className="server-status error">
                Server connection error. Please make sure your backend is running.
              </div>
            )}
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="shc-form">
          <div className="form-group">
            <label>Upload SHC Image</label>
            <input 
              type="file" 
              accept="image/*" 
              onChange={handleFileChange}
              className="file-input" 
            />
          </div>
          
          {preview && (
            <div className="image-preview">
              <img src={preview} alt="Preview" />
            </div>
          )}
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          <div className="form-actions">
            <button 
              type="submit" 
              className="submit-button"
              disabled={!file || isLoading || serverStatus === 'error'}
            >
              {isLoading ? 'Processing...' : 'Parse SHC'}
            </button>
          </div>
        </form>
        
        {parsedData && (
          <div className="results-section">
            <h3>Parsed Information</h3>
            
            <div className="info-panel">
              <h4>Farmer & Location</h4>
              <div className="info-grid">
                <div><span className="label">Farmer:</span> {parsedData.farmer_details?.name || 'N/A'}</div>
                <div><span className="label">Sample No:</span> {parsedData.sample_details?.sample_number || 'N/A'}</div>
                <div><span className="label">Survey No:</span> {parsedData.sample_details?.survey_number || 'N/A'}</div>
                <div><span className="label">Village:</span> {parsedData.sample_details?.village || 'N/A'}</div>
                <div><span className="label">Gram Panchayat:</span> {parsedData.sample_details?.gram_panchayat || 'N/A'}</div>
                <div><span className="label">Block:</span> {parsedData.sample_details?.block || 'N/A'}</div>
                <div><span className="label">District:</span> {parsedData.sample_details?.district || 'N/A'}</div>
                <div><span className="label">State:</span> {parsedData.sample_details?.state || 'N/A'}</div>
              </div>
            </div>
            
            <div className="info-panel">
              <h4>Nutrient Analysis</h4>
              <div className="nutrient-grid">
                {parsedData.nutrients && Object.entries(parsedData.nutrients).map(([key, nutrientObj]) => (
                  <div key={key} className="nutrient-item">
                    <div className="nutrient-name">{key}</div>
                    <div className={getNutrientStatusClass(nutrientObj.value, key)}>
                      {getNutrientStatusText(nutrientObj.value, key)} {nutrientObj.unit}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="recommendations">
              <h4>Fertilizer Recommendations</h4>
              <ul className="recommendation-list">
                {parsedData.nutrients && 
                  getFertilizerRecommendation(parsedData.nutrients).map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
              <p className="note">
                These recommendations are general guidelines. Consult with a local agricultural expert 
                for advice specific to your crops and region.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ShcParser;