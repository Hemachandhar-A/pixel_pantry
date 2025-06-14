import { useState, useEffect } from "react";
import axios from "axios";
import "./FarmQuest.css"; // Import CSS

const FarmQuest = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [diseaseInfo, setDiseaseInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tips, setTips] = useState([]); // Optional: Store farming tips
  const [cropType, setCropType] = useState(""); // For labeling
  const [diseaseType, setDiseaseType] = useState(""); // For labeling
  const [imageId, setImageId] = useState(null); // Store uploaded image ID

  // Fetch farming tips on mount
  useEffect(() => {
    axios.get("/farming-tips")
      .then(response => setTips(response.data))
      .catch(error => console.error("Error fetching farming tips:", error));
  }, []);

  // Handle file selection
  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  // Upload and analyze image
  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
      setLoading(true);
      const response = await axios.post("/upload", formData);
      setDiseaseInfo(response.data);
      setImageId(response.data.image_id); // Store image ID for labeling
    } catch (error) {
      console.error("Error uploading image:", error);
      alert("Failed to analyze the image. Try again.");
    } finally {
      setLoading(false);
    }
  };

  // Label Image after analysis
  const handleLabelImage = async () => {
    if (!imageId || !cropType || !diseaseType) {
      alert("Please provide all details for labeling.");
      return;
    }

    try {
      await axios.post(`/label/${imageId}`, {
        cropType,
        diseaseType,
      });
      alert("Label saved successfully!");
    } catch (error) {
      console.error("Error labeling image:", error);
      alert("Failed to label the image.");
    }
  };

  return (
    <div className="farmquest-container">
      <h1 className="farmquest-title">🌾 Farm Quest</h1>

      <input type="file" accept="image/*" onChange={handleFileChange} className="farmquest-input" />
      <button 
        onClick={handleUpload} 
        className="farmquest-button"
        disabled={loading}
      >
        {loading ? "Scanning..." : "Upload & Identify"}
      </button>

      {diseaseInfo && (
        <div className="farmquest-results">
          <h2>Disease Identified:</h2>
          <p>{diseaseInfo.disease}</p>
          <h3>Possible Solutions:</h3>
          <p>{diseaseInfo.solution}</p>
        </div>
      )}

      {/* Labeling Section */}
      {diseaseInfo && (
        <div className="farmquest-label">
          <h2>📌 Label Image:</h2>
          <input 
            type="text" 
            placeholder="Crop Type" 
            value={cropType} 
            onChange={(e) => setCropType(e.target.value)} 
          />
          <input 
            type="text" 
            placeholder="Disease Type" 
            value={diseaseType} 
            onChange={(e) => setDiseaseType(e.target.value)} 
          />
          <button onClick={handleLabelImage} className="farmquest-button">Save Label</button>
        </div>
      )}

      {/* Farming Tips Section */}
      {tips.length > 0 && (
        <div className="farmquest-tips">
          <h2>🌱 Farming Tips:</h2>
          <ul>
            {tips.map((tip, index) => (
              <li key={index}> {tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FarmQuest;
