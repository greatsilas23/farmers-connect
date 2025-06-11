import React, { useState, useEffect } from "react";

export default function CropPricePrediction() {
  const [options, setOptions] = useState({ crops: [], markets: [], units: [] });
  const [formData, setFormData] = useState({
    market: "",
    commodity: "",
    unit: "",
    quantity: "",
    year: "",
    month: "",
  });
  const [result, setResult] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/api/options")
      .then(res => res.json())
      .then(data => setOptions(data))
      .catch(console.error);
  }, []);

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResult("Loading...");

    try {
      const response = await fetch("http://localhost:5000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      if (data.success) {
        setResult(data.message);
      } else {
        setResult(data.error || "Prediction failed");
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
    backgroundColor: "#28a745",
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
    color: "#007bff",
    textAlign: "center",
  };

  return (
    <div style={containerStyle}>
      <h2 style={{ textAlign: "center", marginBottom: "20px" }}>Crop Price Prediction</h2>
      <form onSubmit={handleSubmit}>
        <label style={labelStyle}>Market:</label>
        <select name="market" value={formData.market} onChange={handleChange} required style={inputStyle}>
          <option value="">Select Market</option>
          {options.markets.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>

        <label style={labelStyle}>Commodity:</label>
        <select name="commodity" value={formData.commodity} onChange={handleChange} required style={inputStyle}>
          <option value="">Select Commodity</option>
          {options.crops.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <label style={labelStyle}>Unit:</label>
        <select name="unit" value={formData.unit} onChange={handleChange} required style={inputStyle}>
          <option value="">Select Unit</option>
          {options.units.map((u) => (
            <option key={u} value={u}>{u}</option>
          ))}
        </select>

        <label style={labelStyle}>Quantity:</label>
        <input
          type="number"
          name="quantity"
          value={formData.quantity}
          onChange={handleChange}
          required
          style={inputStyle}
        />

        <label style={labelStyle}>Year:</label>
        <input
          type="number"
          name="year"
          value={formData.year}
          onChange={handleChange}
          required
          style={inputStyle}
        />

        <label style={labelStyle}>Month:</label>
        <input
          type="number"
          name="month"
          value={formData.month}
          onChange={handleChange}
          required
          min="1"
          max="12"
          style={inputStyle}
        />

        <button type="submit" style={buttonStyle}>Predict Price</button>
      </form>

      {result && <p style={resultStyle}>{result}</p>}
    </div>
  );
}
