module.exports = class MockProvider {
  id() {
    return 'mock-provider';
  }

  async callApi(prompt, context) {
    const vars = context?.vars || {};
    const risk = vars.risk_band || 'low';
    const prob = parseFloat(vars.late_delivery_probability || '0');

    let response = '';

    if (risk === 'high' || prob > 0.7) {
      response = 'Notify the courier immediately. High risk of late delivery detected. Consider proactive customer communication.';
    } else if (risk === 'medium' || prob > 0.4) {
      response = 'Monitor the order closely. Moderate risk detected. Watch for further delays.';
    } else {
      response = 'Monitor only. Low risk order. No immediate action needed.';
    }

    return {
      output: response,
    };
  }
};
