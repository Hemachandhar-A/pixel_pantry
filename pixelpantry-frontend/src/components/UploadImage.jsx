import { useState } from "react";
import "./UploadImage.css";

function UploadImage() {
  const [selectedImage, setSelectedImage] = useState(null);

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload an Image</h2>
      
      {/* Upload Button */}
      <label className="upload-button">
        Choose Image
        <input 
          type="file" 
          accept="image/*" 
          onChange={handleImageChange} 
          style={{ display: "none" }} 
        />
      </label>

      {/* Preview Image */}
      {selectedImage && (
        <div className="image-preview">
          <h4>Preview:</h4>
          <img src={URL.createObjectURL(selectedImage)} alt="Selected Preview" />
        </div>
      )}
    </div>
  );
}

export default UploadImage;
