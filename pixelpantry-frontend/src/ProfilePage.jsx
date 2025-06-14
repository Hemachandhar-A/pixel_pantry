import { useState } from "react";
import "./ProfilePage.css";

function ProfilePage() {
  // State for farmer details
  const [farmer, setFarmer] = useState({
    name: "John Doe",
    age: "40",
    experience: "15 years",
    location: "Rural Village, India",
    farmSize: "5 acres",
    cropType: "Wheat, Rice",
    preferredCrops: "Maize, Barley",
    contact: "9876543210",
    profileImage: null,
  });

  const [editing, setEditing] = useState(false);
  const [updatedFarmer, setUpdatedFarmer] = useState({ ...farmer });

  // Handle input changes
  const handleChange = (e) => {
    setUpdatedFarmer({ ...updatedFarmer, [e.target.name]: e.target.value });
  };

  // Handle profile image upload
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUpdatedFarmer((prev) => ({ ...prev, profileImage: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  // Save updated details with validation
  const handleSave = () => {
    if (!updatedFarmer.name || !updatedFarmer.contact) {
      alert("Name and Contact are required!");
      return;
    }
    setFarmer(updatedFarmer);
    setEditing(false);
  };

  return (
    <div className="profile-container">
      <h2>👨‍🌾 Farmer Profile</h2>
      
      {/* Profile Image */}
      <div className="profile-image-container">
        {farmer.profileImage ? (
          <img src={farmer.profileImage} alt="Profile" className="profile-image" />
        ) : (
          <div className="profile-placeholder">Upload Image</div>
        )}
      </div>

      <div className="profile-details">
        {editing ? (
          <>
            <label>📸 Profile Image:</label>
            <input type="file" accept="image/*" onChange={handleImageUpload} />

            <label>📝 Name:</label>
            <input type="text" name="name" value={updatedFarmer.name} onChange={handleChange} required />

            <label>🎂 Age:</label>
            <input type="number" name="age" value={updatedFarmer.age} onChange={handleChange} />

            <label>📅 Experience:</label>
            <input type="text" name="experience" value={updatedFarmer.experience} onChange={handleChange} />

            <label>📍 Location:</label>
            <input type="text" name="location" value={updatedFarmer.location} onChange={handleChange} />

            <label>🌾 Farm Size:</label>
            <input type="text" name="farmSize" value={updatedFarmer.farmSize} onChange={handleChange} />

            <label>🌱 Crop Type:</label>
            <input type="text" name="cropType" value={updatedFarmer.cropType} onChange={handleChange} />

            <label>🌾 Preferred Crops:</label>
            <input type="text" name="preferredCrops" value={updatedFarmer.preferredCrops} onChange={handleChange} />

            <label>📞 Contact:</label>
            <input type="text" name="contact" value={updatedFarmer.contact} onChange={handleChange} required />

            <button className="save-btn" onClick={handleSave}>💾 Save Profile</button>
          </>
        ) : (
          <>
            <p><strong>📝 Name:</strong> {farmer.name}</p>
            <p><strong>🎂 Age:</strong> {farmer.age}</p>
            <p><strong>📅 Experience:</strong> {farmer.experience}</p>
            <p><strong>📍 Location:</strong> {farmer.location}</p>
            <p><strong>🌾 Farm Size:</strong> {farmer.farmSize}</p>
            <p><strong>🌱 Crop Type:</strong> {farmer.cropType}</p>
            <p><strong>🌾 Preferred Crops:</strong> {farmer.preferredCrops}</p>
            <p><strong>📞 Contact:</strong> {farmer.contact}</p>
            <button className="edit-btn" onClick={() => setEditing(true)}>✏️ Edit Profile</button>
          </>
        )}
      </div>
    </div>
  );
}

export default ProfilePage;
