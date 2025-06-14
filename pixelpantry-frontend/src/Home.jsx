// First, you'll need to install a PDF generation library
// Run this in your project directory:
// npm install jspdf jspdf-autotable

// Then import it in your Home.js file
import { useState } from "react";
import "./Home.css";
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import autoTable from 'jspdf-autotable';


function Home() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [modelType, setModelType] = useState("disease");
  const [activeTab, setActiveTab] = useState("information");
  const [errorMessage, setErrorMessage] = useState(null);
  
  // URLs for both model endpoints
  const API_URLS = {
    disease: "http://localhost:5000/rice-disease/predict",
    pest: "http://localhost:5000/rice-pest/predict"
  };

  // Handle image selection
  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewImage(URL.createObjectURL(file));
      setPrediction(null);
    }
  };

  // Handle model type change
  const handleModelChange = (event) => {
    setModelType(event.target.value);
    setPrediction(null);
  };

  // Handle tab change
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  // Handle image upload and prediction
  const handleUpload = async () => {
    if (!selectedImage) {
      alert("Please select an image first!");
      return;
    }

    setLoading(true);
    setPrediction(null);

    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      const response = await fetch(API_URLS[modelType], {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to get ${modelType} prediction`);
      }

      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error("Error:", error);
      alert(`Error analyzing image with ${modelType} model. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  // New function to download results as PDF
  const downloadPDF = () => {
    if (!prediction) {
      alert("No analysis results to download!");
      return;
    }

    // Create a new PDF document
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.width;
    
    // Add title
    doc.setFontSize(20);
    doc.setTextColor(0, 128, 0); // Green color for title
    doc.text("Rice Plant Analyzer - Analysis Results", pageWidth / 2, 20, { align: "center" });
    
    // Add current date
    const date = new Date().toLocaleDateString();
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text(`Generated on: ${date}`, pageWidth - 15, 30, { align: "right" });
    
    // Add image if available
    if (previewImage) {
      try {
        doc.addImage(previewImage, 'JPEG', 15, 35, 60, 60);
        doc.setDrawColor(200, 200, 200);
        doc.rect(15, 35, 60, 60);
      } catch (e) {
        console.error("Could not add image to PDF:", e);
      }
    }
    
    // Add analysis details
    doc.setFontSize(14);
    doc.setTextColor(0, 0, 0);
    doc.text("Analysis Details", 85, 45);
    
    doc.setFontSize(12);
    doc.text(`Analysis Type: ${modelType === "disease" ? "Disease Detection" : "Pest Detection"}`, 85, 55);
    doc.text(`Detected ${modelType === "disease" ? "Disease" : "Pest"}: ${prediction.predicted_class}`, 85, 65);
    doc.text(`Confidence Level: ${(prediction.confidence * 100).toFixed(1)}%`, 85, 75);
    
    // Add detailed information based on active tab
    doc.setFontSize(14);
    doc.text("Detailed Information", 15, 110);
    
    doc.setFontSize(11);
    let yPosition = 120;
    
    // Add description
    if (modelType === "disease") {
      const description = getDiseaseDescription(prediction.predicted_class);
      doc.setFontSize(12);
      doc.text("About this disease:", 15, yPosition);
      yPosition += 10;
      
      // Handle multi-line text
      const splitDescription = doc.splitTextToSize(description, pageWidth - 30);
      doc.setFontSize(10);
      doc.text(splitDescription, 15, yPosition);
      yPosition += splitDescription.length * 6 + 10;
      
      // Add severity information
      doc.setFontSize(12);
      doc.text("Potential Severity:", 15, yPosition);
      yPosition += 10;
      
      const severity = getDiseaseSeverity(prediction.predicted_class);
      doc.setFontSize(10);
      doc.text(`${severity}% (${severity < 40 ? "Low" : severity < 70 ? "Medium" : "High"})`, 15, yPosition);
      yPosition += 15;
    } else {
      const description = getPestDescription(prediction.predicted_class);
      doc.setFontSize(12);
      doc.text("About this pest:", 15, yPosition);
      yPosition += 10;
      
      // Handle multi-line text
      const splitDescription = doc.splitTextToSize(description, pageWidth - 30);
      doc.setFontSize(10);
      doc.text(splitDescription, 15, yPosition);
      yPosition += splitDescription.length * 6 + 10;
      
      // Add impact areas
      doc.setFontSize(12);
      doc.text("Impact Areas:", 15, yPosition);
      yPosition += 10;
      
      const impactAreas = getPestImpactAreas(prediction.predicted_class);
      doc.setFontSize(10);
      doc.text(impactAreas.join(", "), 15, yPosition);
      yPosition += 15;
    }
    
    // Add treatment recommendations
    doc.setFontSize(12);
    doc.text("Treatment Recommendations:", 15, yPosition);
    yPosition += 10;
    
    let treatmentText = "";
    if (modelType === "disease") {
      treatmentText = "Please consult with an agricultural expert for specific treatment of " + prediction.predicted_class + ".";
    } else {
      treatmentText = getPestTreatment(prediction.predicted_class);
    }
    
    const splitTreatment = doc.splitTextToSize(treatmentText, pageWidth - 30);
    doc.setFontSize(10);
    doc.text(splitTreatment, 15, yPosition);
    
    // Add other possibilities table if available
    if (prediction.sorted_probabilities && prediction.sorted_probabilities.length > 0) {
      doc.addPage();
      doc.setFontSize(14);
      doc.text("Other Possibilities", pageWidth / 2, 20, { align: "center" });
      
      autoTable(doc, {
        startY: 30,
        head: [["Possibility", "Confidence"]], // Directly defining table headers
        body: prediction.sorted_probabilities.map(item => [item.class, (item.probability * 100).toFixed(1) + "%"]),
        theme: 'grid',
        headStyles: { fillColor: [76, 175, 80] },
        alternateRowStyles: { fillColor: [240, 240, 240] }
      });
      

      
    }
    
    // Add footer
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150, 150, 150);
      doc.text("© 2025 Rice Plant Analyzer | Powered by Advanced AI", pageWidth / 2, 290, { align: "center" });
      doc.text(`Page ${i} of ${pageCount}`, pageWidth - 15, 290, { align: "right" });
    }
    
    // Save the PDF
    const filename = `rice-${modelType}-analysis-${prediction.predicted_class.toLowerCase().replace(/\s+/g, '-')}.pdf`;
    doc.save(filename);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="logo-container">
          <button 
            className="back-button" 
            onClick={() => window.history.back()}
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
            Back
          </button>
          
          <h1>Crop Analyzer</h1>
        </div>
       {/* <p className="subtitle" style={{color:"white",paddingRight:'20px'}}>Advanced pest and disease detection for rice crops</p>*/}
      </header>

      <main className="app-main">
        {errorMessage && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {errorMessage}
            <button 
              className="dismiss-error" 
              onClick={() => setErrorMessage(null)}
            >
              ✕
            </button>
          </div>
        )}
        
        
      </main>

      <main className="main-content">
        <div className="content-wrapper">
          {/* Left panel - Controls */}
          <div className="control-panel">
            <div className="model-selection-card">
              <h2>Detection Type</h2>
              <div className="toggle-container">
                <button 
                  className={`toggle-btn ${modelType === "disease" ? "active" : ""}`}
                  value="disease"
                  onClick={handleModelChange}
                >
                  Disease
                </button>
                <button 
                  className={`toggle-btn ${modelType === "pest" ? "active" : ""}`}
                  value="pest"
                  onClick={handleModelChange}
                >
                  Pest
                </button>
              </div>
              <p className="model-description">
                {modelType === "disease" 
                  ? "Detect fungal, bacterial, and viral diseases affecting rice plants." 
                  : "Identify harmful insects and pests that damage rice crops."}
              </p>
            </div>

            <div className="upload-card">
              <h2>Upload Image</h2>
              <p>Select a clear image of the affected rice plant for analysis</p>
              
              <div className="upload-area" onClick={() => document.getElementById("fileInput").click()}>
                {previewImage ? (
                  <img src={previewImage} alt="Preview" className="preview-image" />
                ) : (
                  <div className="upload-placeholder">
                    <div className="upload-icon">📷</div>
                    <p>Click to browse or drag image here</p>
                  </div>
                )}
                <input 
                  id="fileInput" 
                  type="file" 
                  accept="image/*" 
                  onChange={handleImageChange} 
                  style={{ display: "none" }} 
                />
              </div>
              
              {previewImage && (
                <div className="image-controls">
                  <button 
                    className="remove-btn"
                    onClick={() => {
                      setPreviewImage(null);
                      setSelectedImage(null);
                      setPrediction(null);
                    }}
                  >
                    Remove
                  </button>
                  <button 
                    className="analyze-btn" 
                    onClick={handleUpload} 
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner"></span>
                        Analyzing...
                      </>
                    ) : (
                      `Analyze for ${modelType === "disease" ? "Diseases" : "Pests"}`
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right panel - Results */}
          <div className="results-panel">
            {prediction ? (
              <div className="results-card">
                <div className="results-header" >
                  <h2 style={{textAlign:'center'}}>Analysis Results</h2>
                  <span className={`result-badge ${prediction.confidence > 0.7 ? "high" : prediction.confidence > 0.4 ? "medium" : "low"}`} >
                    {prediction.confidence > 0.7 ? "High Confidence" : prediction.confidence > 0.4 ? "Medium Confidence" : "Low Confidence"}
                  </span>
                </div>

                <div className="detection-result">
                  <div className="result-item primary">
                    <h3>Detected {modelType === "disease" ? "Disease" : "Pest"}</h3>
                    <div className="result-value">
                      <strong>{prediction.predicted_class}</strong>
                      <span className="confidence-value">{(prediction.confidence * 100).toFixed(1)}% confidence</span>
                    </div>
                  </div>

                  {prediction.sorted_probabilities && prediction.sorted_probabilities.length > 0 && (
                    <div className="result-item secondary">
                      <h3>Other Possibilities</h3>
                      <ul className="possibilities-list">
                        {prediction.sorted_probabilities.slice(0, 3).map((item, index) => (
                          <li key={index} className="possibility-item">
                            <span className="possibility-name">{item.class}</span>
                            <div className="probability-bar-container">
                              <div 
                                className="probability-bar"
                                style={{ width: `${item.probability * 100}%` }}
                              ></div>
                              <span className="probability-value">{(item.probability * 100).toFixed(1)}%</span>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                <div className="info-tabs">
                  <div className="tabs-header">
                    <button 
                      className={`tab-btn ${activeTab === "information" ? "active" : ""}`}
                      onClick={() => handleTabChange("information")}
                    >
                      Information
                    </button>
                    <button 
                      className={`tab-btn ${activeTab === "treatment" ? "active" : ""}`}
                      onClick={() => handleTabChange("treatment")}
                    >
                      Treatment
                    </button>
                    <button 
                      className={`tab-btn ${activeTab === "prevention" ? "active" : ""}`}
                      onClick={() => handleTabChange("prevention")}
                    >
                      Prevention
                    </button>
                  </div>
                  
                  <div className="tab-content">
                    {modelType === "disease" ? (
                      <>
                        {activeTab === "information" && (
                          <div className="tab-pane">
                            <h3>About this disease</h3>
                            <p>{getDiseaseDescription(prediction.predicted_class)}</p>
                            
                            <div className="severity-indicator">
                              <h4>Potential Severity</h4>
                              <div className="severity-bar">
                                <div 
                                  className="severity-level" 
                                  style={{ 
                                    width: `${getDiseaseSeverity(prediction.predicted_class)}%`,
                                    backgroundColor: getSeverityColor(getDiseaseSeverity(prediction.predicted_class))
                                  }}
                                ></div>
                              </div>
                              <div className="severity-labels">
                                <span>Low</span>
                                <span>Medium</span>
                                <span>High</span>
                              </div>
                            </div>
                          </div>
                        )}
                        
                        {activeTab === "treatment" && (
                           <div className="tab-pane">
                              <h3>Treatment Recommendations</h3>
                              <p>
                                {modelType === "disease"
                                  ? getDiseaseTreatment(prediction.predicted_class)
                                  : getPestTreatment(prediction.predicted_class)}
                              </p>
                            </div>
                          )}

                        
                        {activeTab === "prevention" && (
                          <div className="tab-pane">
                            <h3>Prevention strategies</h3>
                            <p>
                              {modelType === "disease"
                               ? getDiseasePrevention(prediction.predicted_class)
                               :getPestTreatment(prediction.predicted_class)}
                            </p>
                          </div>
                        )}
                      </>
                    ) : (
                      <>
                        {activeTab === "information" && (
                          <div className="tab-pane">
                            <h3>About this pest</h3>
                            <p>{getPestDescription(prediction.predicted_class)}</p>
                            
                            <div className="impact-section">
                              <h4>Impact Areas</h4>
                              <div className="impact-areas">
                                {getPestImpactAreas(prediction.predicted_class).map((area, index) => (
                                  <div key={index} className="impact-tag">
                                    {area}
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                        
                        {activeTab === "treatment" && (
                          <div className="tab-pane">
                            <h3>Treatment Recommendations</h3>
                            <p>{getPestTreatment(prediction.predicted_class)}</p>
                          </div>
                        )}
                        
                        {activeTab === "prevention" && (
                          <div className="tab-pane">
                            <h3>Prevention strategies</h3>
                            <p>Information about preventing {prediction.predicted_class} infestations would go here.</p>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>

                {/* Add Download PDF button */}
                <div className="export-controls">
                  <button 
                    className="download-btn"
                    onClick={downloadPDF}
                  >
                    <span className="download-icon">📥</span>
                    Download as PDF
                  </button>
                </div>
              </div>
            ) : (
              <div className="empty-results" style={{padding:'2rem'}}>

                <div className="empty-icon">🔍</div>
                <h2>No Analysis Results Yet</h2>
                <p>Upload an image and click Analyze to detect {modelType === "disease" ? "diseases" : "pests"} in your rice plants.</p>
                
                <div className="info-box" style={{padding:'3rem',textAlign:'left'}}>
                  <h2>How it works ?</h2>
                  <br/>
                  <ol className="steps-list" >
                    <li>
                      <span className="step-number"></span>
                      <span className="step-text">Select detection type (pest or disease)</span>
                    </li>
                    <li>
                      <span className="step-number"></span>
                      <span className="step-text">Upload a clear image of your rice plant</span>
                    </li>
                    <li>
                      <span className="step-number"></span>
                      <span className="step-text">Click analyze to get AI-powered detection results</span>
                    </li>
                    <li>
                      <span className="step-number"></span>
                      <span className="step-text">Review detailed information and treatment options</span>
                    </li>
                  </ol>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
      
      
    </div>
  );
}

// Helper functions remain the same as in your original code
function getDiseaseDescription(diseaseName) {
  const descriptions = {
    "Bacterial Leaf Blight": "A serious bacterial disease affecting rice plants, causing yellowing and drying of leaves. It begins as water-soaked lesions at leaf margins which enlarge and turn yellow to white as they expand. In severe cases, entire leaves may become blighted and die.",
    
    "Brown Spot": "A fungal disease characterized by brown lesions on leaves, reducing photosynthetic area. The spots are initially small, circular, and dark brown, later enlarging with gray centers and brown margins. Severe infections lead to numerous spots that may coalesce, causing leaf death.",
    
    "Healthy Rice Leaf": "No disease detected. The rice leaf appears vibrant green with uniform color and no visible signs of lesions, spots, or discoloration. Proper monitoring and good agricultural practices should be maintained to ensure continued plant health.",
    
    "Leaf Blast": "A devastating fungal disease showing diamond-shaped lesions on leaves. Lesions start as small water-soaked spots that enlarge quickly to form diamond-shaped or spindle-shaped spots with gray centers and brown borders. Under favorable conditions, the disease can kill young plants or cause severe yield loss.",
    
    "Leaf Scald": "A fungal disease causing elongated, light brown to gray lesions with wavy margins on rice leaves. These lesions expand along the leaf veins, often giving a scalded or burned appearance. In severe cases, leaf tips may dry up, reducing the plant’s ability to photosynthesize effectively.",
    
    "Sheath Blight": "A fungal disease that initially appears as greenish-gray, water-soaked lesions on the lower leaf sheaths. These lesions expand and turn light brown, often forming irregular patches. In severe cases, the disease spreads to upper leaves, leading to lodging and significant yield reduction."
  };

  
  return descriptions[diseaseName] || "No description available for this disease.";
}

function getDiseaseSeverity(diseaseName) {
  const severities = {
    "Bacterial Leaf Blight": 80,  // Can cause yield losses of 20-60%
    "Brown Spot": 50,            // Can lead to moderate yield losses, worsened by poor nutrition
    "Leaf Blast": 90,            // One of the most destructive rice diseases, causing 70-100% loss in severe cases
    "Leaf Scald": 60,            // Can cause significant damage but is less aggressive than blast
    "Sheath Blight": 75,         // Affects plant vigor, leading to 25-50% yield loss
    "Healthy Rice Leaf": 0       // No disease present
  };

  return severities[diseaseName] || 50; // Default severity if disease is not listed
}

function getSeverityColor(severity) {
  if (severity < 40) return "#4caf50"; // Green for low severity
  if (severity < 70) return "#ff9800"; // Orange for medium severity
  return "#f44336"; // Red for high severity
}

function getDiseaseTreatment(diseaseName) {
  const treatments = {
    "Bacterial Leaf Blight": "Use resistant rice varieties. Apply copper-based bactericides (e.g., copper hydroxide). Avoid excessive nitrogen fertilization. Improve drainage to reduce disease spread.",
    
    "Brown Spot": "Apply fungicides like Mancozeb or Tricyclazole at early disease stages. Improve soil fertility with proper nitrogen and potassium levels. Use resistant varieties where available.",
    
    "Leaf Blast": "Apply systemic fungicides like Tricyclazole or Isoprothiolane. Avoid excessive nitrogen application. Ensure proper water management to reduce humidity in fields.",
    
    "Leaf Scald": "Use fungicides such as Propiconazole if symptoms appear. Avoid overhead irrigation to reduce leaf wetness. Use balanced fertilization to strengthen plant resistance.",
    
    "Sheath Blight": "Apply fungicides like Hexaconazole or Validamycin when symptoms appear. Use wider plant spacing to improve air circulation. Remove and destroy infected plant debris.",
    
    "Healthy Rice Leaf": "No treatment needed. Maintain regular monitoring and good agronomic practices to ensure continued plant health."
  };

  return treatments[diseaseName] || "No specific treatment recommendation available for this disease.";
}

function getDiseasePrevention(diseaseName) {
  const preventionStrategies = {
    "Bacterial Leaf Blight": "Plant resistant varieties. Avoid planting in areas prone to water stagnation. Use certified disease-free seeds. Reduce plant density to improve airflow.",
    
    "Brown Spot": "Ensure proper nitrogen and potassium fertilization. Improve drainage to prevent prolonged leaf wetness. Use disease-resistant rice varieties.",
    
    "Leaf Blast": "Plant resistant varieties. Avoid excessive nitrogen application. Implement proper field sanitation by removing infected plant residues.",
    
    "Leaf Scald": "Use resistant rice varieties. Avoid planting in humid conditions. Implement crop rotation to reduce fungal buildup in soil.",
    
    "Sheath Blight": "Use wider plant spacing to reduce humidity and improve airflow. Remove weeds and plant debris after harvest. Use resistant rice varieties where available.",
    
    "Healthy Rice Leaf": "Maintain healthy soil and water conditions. Use disease-free seeds and proper crop rotation. Regularly monitor plants for early signs of disease."
  };

  return preventionStrategies[diseaseName] || "No specific prevention recommendation available for this disease.";
}


function getPestDescription(pestName) {
  const descriptions = {
    "Asiatic Rice Borer": "A destructive pest that bores into rice stems. The larvae feed inside the stem, causing 'deadhearts' during vegetative stage and 'whiteheads' during reproductive stage. Infested plants show withered central shoots and unfilled grains.",
    
    "Brown Plant Hopper": "A major rice pest that sucks sap from the base of the plant. Severe infestations cause 'hopper burn', a condition where patches of plants turn yellow, wither, and die. They also transmit viral diseases, compounding the damage.",
    
    "Paddy Stem Maggot": "The larvae of this pest feed on the central shoot of rice plants, causing 'deadhearts'. The maggots tunnel inside the stem, disrupting nutrient flow. Adult flies are small and gray, laying eggs on rice leaves near the stem.",
    
    "Rice Gall Midge": "The larvae cause silver shoots or 'onion leaves' by forming galls at the base of tillers. Affected tillers do not produce panicles, leading to yield loss. The adult resembles a mosquito with long legs and a slender body.",
    
    "Rice Leaf Caterpillar": "These caterpillars feed on rice leaves, creating irregular patterns of damage and reducing photosynthetic area. Heavy infestations can defoliate plants. The adult moths are brown with distinctive wing patterns.",
    
    "Rice Leaf Hopper": "These insects suck sap from rice leaves and stems, causing yellowing, wilting, and stunting. They also transmit viral diseases like tungro. They move sideways when disturbed, a characteristic behavior.",
    
    "Rice Leaf Roller": "The larvae roll leaves and feed inside the rolled leaves, causing whitish streaks. Severe infestation reduces photosynthetic activity and grain yield. The adults are small moths with distinctive wing patterns.",
    
    "Rice Shell Pest": "Damages developing grains by sucking out the contents, resulting in partially filled or empty grains with dark spots. Can cause significant yield reduction. The bugs are shield-shaped with piercing-sucking mouthparts.",
    
    "Rice Stem Fly": "The maggots feed on central shoot tissue, causing 'deadhearts'. Infested tillers become yellow and easily detachable from the base. The adult flies are small, measuring about 2-3mm in length.",
    
    "Rice Water Weevil": "The larvae feed on rice roots, reducing the plant's ability to absorb nutrients and water. Adults chew on rice leaves, creating characteristic slit-like feeding scars. This pest is particularly problematic in flooded rice fields.",
    
    "Thrips": "Tiny insects that rasp the leaf surface and suck the oozing cell sap, causing silvery streaks and rolling of leaves. Severe infestation leads to wilting and yield loss. They are barely visible to the naked eye but cause distinctive damage.",
    
    "Yellow Rice Borer": "The larvae bore into stems and feed internally, causing 'deadhearts' and 'whiteheads'. One of the most damaging rice stem borers across many rice-growing regions. Adult moths are yellow with dark markings on the wings.",
    
    "None": "No pest detected. The plant appears to be free from pest infestation."
  };
  
  return descriptions[pestName] || "No description available for this pest.";
}

function getPestImpactAreas(pestName) {
  const impactAreas = {
    "Asiatic Rice Borer": ["Stems", "Tillers", "Panicles"],
    "Brown Plant Hopper": ["Base of plant", "Stems", "Viral transmission"],
    "Paddy Stem Maggot": ["Central shoot", "Stems"],
    "Rice Gall Midge": ["Tillers", "Panicle development"],
    "Rice Leaf Caterpillar": ["Leaves", "Photosynthesis"],
    "Rice Leaf Hopper": ["Leaves", "Stems", "Viral transmission"],
    "Rice Leaf Roller": ["Leaves", "Photosynthesis"],
    "Rice Shell Pest": ["Developing grains", "Grain quality"],
    "Rice Stem Fly": ["Central shoot", "Tillers"],
    "Rice Water Weevil": ["Roots", "Leaves"],
    "Thrips": ["Leaves", "Seedlings"],
    "Yellow Rice Borer": ["Stems", "Tillers", "Panicles"],
  };
  
  return impactAreas[pestName] || ["Unknown impact areas"];
}

function getPestTreatment(pestName) {
  const treatments = {
    "Asiatic Rice Borer": "Apply appropriate insecticides like chlorantraniliprole or flubendiamide. For biological control, release Trichogramma parasitoids. Remove and destroy crop residues after harvest to eliminate overwintering sites.",
    
    "Brown Plant Hopper": "Use resistant rice varieties. Avoid excessive use of nitrogen fertilizers. Apply insecticides like buprofezin or pymetrozine. Drain rice fields periodically to disrupt the pest's habitat.",
    
    "Paddy Stem Maggot": "Early planting can help avoid peak infestation periods. Apply systemic insecticides like cartap or thiamethoxam. Maintain field hygiene by removing alternative hosts and crop residues.",
    
    "Rice Gall Midge": "Plant resistant varieties. Synchronize planting in a given area. Apply dinotefuran or thiamethoxam as soil application or foliar spray. Remove alternate hosts around rice fields.",
    
    "Rice Leaf Caterpillar": "Apply insecticides like chlorantraniliprole or flubendiamide when infestation is detected. Encourage natural enemies like parasitic wasps and predatory bugs through conservation biological control.",
    
    "Rice Leaf Hopper": "Use resistant varieties. Apply insecticides like buprofezin, thiamethoxam, or dinotefuran. Avoid excessive nitrogen application. Preserve natural enemies by using selective insecticides.",
    
    "Rice Leaf Roller": "Apply insecticides like chlorantraniliprole or flubendiamide when young larvae are detected. Remove weeds that serve as alternative hosts. Encourage natural enemies through habitat management.",
    
    "Rice Shell Pest": "Apply insecticides during the milky stage of the crop when pests are most active. Use neem-based products as a deterrent. Remove weeds that serve as alternative hosts.",
    
    "Rice Stem Fly": "Early planting can help avoid peak infestation periods. Apply carbofuran or phorate granules in nursery beds. Remove and destroy stubble after harvest to kill overwintering larvae.",
    
    "Rice Water Weevil": "Drain rice fields temporarily to reduce larval survival. Apply insecticides like chlorantraniliprole or thiamethoxam as seed treatment or granular application. Use cultural practices like winter flooding to reduce overwintering populations.",
    
    "Thrips": "Apply insecticides like thiamethoxam or spinosad when infestation is detected. Use blue sticky traps to monitor and reduce adult populations. Maintain adequate soil moisture to help plants withstand damage.",
    
    "Yellow Rice Borer": "Use sex pheromone traps for monitoring and mass trapping. Apply insecticides like chlorantraniliprole or flubendiamide. Remove stubble and crop residues after harvest. Use light traps to catch adult moths."
  };
  
  return treatments[pestName] || "No specific treatment recommendation available for this pest.";
}

export default Home;