export const getEnvironmentDataa = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        environmentStatus: 1,
        temperature: 22,
        humidity: 45,
        co2Level: 400,
        lightLevel: 300,
        suitabilityLevel: 0.85,
        predictedSuitabilityLevel: 0.9,
        predictedTrend: 1,
        recommendation: "Current conditions are suitable for studying.",
      });
    }, 700);
  });
};

export const getEnvironmentData = async () => {
  try {
    const response = await fetch("/api/Data");

    if (!response.ok) {
      throw new Error("Error while retrieving data");
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching history:", error);
    return [];
  }
};