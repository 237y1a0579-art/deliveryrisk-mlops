module.exports = {
  id: "mock-delivery-ops-assistant",
  callApi: async function callApi(prompt) {
    const isHighRisk = prompt.includes("Risk band: high");
    const isStorm = prompt.includes("Weather: storm") || prompt.includes("Weather: rain");
    let output = "Monitor the order and refresh the ETA after pickup confirmation.";

    if (isHighRisk && isStorm) {
      output =
        "Notify the customer about weather-related delay risk, prioritize courier reassignment, and refresh the ETA after pickup.";
    } else if (isHighRisk) {
      output =
        "Notify the customer about possible delay, route the order to the operations queue, and review courier availability.";
    }

    return { output };
  },
};

