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

export const getEnvironmentData = async () => {
    try {
        const response = await fetch('/api/Data'); // /api for proxy
        if (!response.ok) throw new Error('Error while retrieving data');
       return await response.json();

    } catch (error) {
        console.error("Error fetching history:", error);
        return [];
    }
};
