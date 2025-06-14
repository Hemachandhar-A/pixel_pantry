// src/api.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
;

export const runModel = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/run-model`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to run model');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error running model:', error);
    throw error;
  }
};

export const getExplanation = async (cropData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/explain-recommendation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(cropData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get explanation');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting explanation:', error);
    throw error;
  }
};

export const sendChatMessage = async (message, context) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, context }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to send message');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};









