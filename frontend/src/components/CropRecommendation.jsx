import React, { useState } from "react";

export default function CropRecommendation() {
  const [formData, setFormData] = useState({
    Nitrogen: "",
    Phosphorus: "",
    Potassium: "",
    Temperature: "",
    Humidity: "",
    pH: "",
    Rainfall: "",
  });
  const [result, setResult] = useState("");

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult("Loading...");

    try {
      const response = await fetch("http://localhost:5000/api/recommend_crop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (response.ok) {
        setResult(data.recommendation);
      } else {
        setResult(data.error || "Failed to get recommendation");
      }
    } catch (error) {
      setResult("Error: " + error.message);
    }
  };

  const containerStyle = {
    maxWidth: "500px",
    margin: "40px auto",
    padding: "30px",
    border: "1px solid #ccc",
    borderRadius: "10px",
    backgroundColor: "#f9f9f9",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
  };

  const labelStyle = {
    fontWeight: "bold",
    marginBottom: "5px",
    display: "block",
  };

  const inputStyle = {
    width: "100%",
    padding: "10px",
    marginBottom: "20px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    fontSize: "14px",
  };

  const buttonStyle = {
    padding: "10px 20px",
    backgroundColor: "#007bff",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
    fontWeight: "bold",
    cursor: "pointer",
    width: "100%",
  };

  const resultStyle = {
    marginTop: "20px",
    fontSize: "16px",
    fontWeight: "bold",
    color: "#28a745",
    textAlign: "center",
  };

  return (
    <div style={containerStyle}>
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>Crop Recommendation</h2>
      <form onSubmit={handleSubmit}>
        {Object.keys(formData).map((key) => (
          <div key={key}>
            <label style={labelStyle}>{key}:</label>
            <input
              type="number"
              name={key}
              value={formData[key]}
              onChange={handleChange}
              step="any"
              required
              style={inputStyle}
            />
          </div>
        ))}
        <button type="submit" style={buttonStyle}>Get Recommendation</button>
      </form>
      {result && <p style={resultStyle}>{result}</p>}
    </div>
  );
}
