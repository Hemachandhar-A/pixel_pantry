import { useState } from "react";
import PropTypes from "prop-types";

function LabelImage({ imageId }) {
  const [cropType, setCropType] = useState("");
  const [diseaseType, setDiseaseType] = useState("");
  const [message, setMessage] = useState("");

  const submitLabel = async () => {
    if (!cropType || !diseaseType) {
      alert("Please fill in both fields!");
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/label/${imageId}`, {
        method: "POST",
        body: JSON.stringify({ cropType, diseaseType }),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to submit label");
      }

      const data = await response.json();
      setMessage(data.message);

      // Clear input fields after submission
      setCropType("");
      setDiseaseType("");
    } catch (error) {
      console.error("Error submitting label:", error);
      setMessage("Error submitting label. Please try again.");
    }
  };

  return (
    <div className="mt-6 p-4 bg-gray-50 rounded-lg shadow-md w-full">
      <h2 className="text-lg font-semibold">Label Image</h2>
      <p className="text-gray-600 mb-2">Image ID: {imageId}</p>

      <input
        type="text"
        value={cropType}
        onChange={(e) => setCropType(e.target.value)}
        placeholder="Enter crop type"
        className="p-2 border rounded-lg w-full mb-2"
      />
      <input
        type="text"
        value={diseaseType}
        onChange={(e) => setDiseaseType(e.target.value)}
        placeholder="Enter disease type"
        className="p-2 border rounded-lg w-full mb-2"
      />
      <button
        onClick={submitLabel}
        className="w-full px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
      >
        Submit Label
      </button>
      {message && <p className="text-sm text-gray-600 mt-2">{message}</p>}
    </div>
  );
}

LabelImage.propTypes = {
  imageId: PropTypes.string.isRequired,
};

export default LabelImage;
