export const getEnvironmentDataa= async () => {
    // This simulates fetching data from the ML/Backend team later
    return {
        environmentStatus: 1, // 1 for Good, 0 for Bad
        temperature: 22,
        humidity: 45,
        co2Level: 400,
        lightLevel: 300,
        noiseLevel: 35,
        suitabilityLevel: 0.85,
        predictedSuitabilityLevel: 0.90,
        predictedTrend: 1, // 1 for improving, -1 for declining
    };
};

const API_URL = 'http://127.0.0.1:8000';

export const getEnvironmentHistory = async () => {
  const token = localStorage.getItem('token');

  try {
    const response = await fetch(`${API_URL}/data/history`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}` 
      }
    });

    if (!response.ok) throw new Error('Could not load history');
    
    return await response.json();
  } catch (error) {
    console.error("Error fetching history:", error);
    return [];
  }
};

export const getEnvironmentData = async () => {
  const token = localStorage.getItem('token');

  try {
    const response = await fetch(`${API_URL}/data/current`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) throw new Error('Error in current data');
    return await response.json();
  } catch (error) {
    console.error(error);
    return null;
  }
};