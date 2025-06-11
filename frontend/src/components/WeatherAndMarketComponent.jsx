import React, { useState } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';

const WeatherAndMarketComponent = () => {
  const [location, setLocation] = useState('Nairobi');
  const [weather, setWeather] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchWeather = async () => {
    try {
      setLoading(true);
      const apiKey = 'YOUR_OPENWEATHER_API_KEY';
      const response = await axios.get(
        `https://api.openweathermap.org/data/2.5/weather?q=${location}&units=metric&appid=${apiKey}`
      );
      setWeather(response.data);
    } catch (error) {
      console.error('Error fetching weather:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMarketPrices = async () => {
    try {
      setLoading(true);
      const response = await axios.get('https://kilimostat.api.ke/v1/prices'); // example endpoint
      setMarketData(response.data);
    } catch (error) {
      console.error('Error fetching market prices:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-4 p-4 bg-white rounded shadow">
      <h2 className="h4 fw-bold mb-4">Weather and Market Information</h2>

      <div className="mb-3">
        <label className="form-label">Enter Location:</label>
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="form-control"
        />
        <button
          onClick={fetchWeather}
          className="btn btn-primary mt-2"
        >
          Get Weather
        </button>
      </div>

      {weather && (
        <div className="mb-4">
          <h5>Current Weather in {location}</h5>
          <p>Temperature: {weather.main.temp} °C</p>
          <p>Humidity: {weather.main.humidity}%</p>
          <p>Weather: {weather.weather[0].description}</p>
        </div>
      )}

      <button
        onClick={fetchMarketPrices}
        className="btn btn-success mb-3"
      >
        Load KilimoStat Market Prices
      </button>

      {marketData && (
        <div className="">
          <h5 className="mb-2">Market Prices (Top 5)</h5>
          <ul className="list-group">
            {marketData.slice(0, 5).map((item, index) => (
              <li key={index} className="list-group-item">
                {item.commodity} in {item.market}: KES {item.price} per {item.unit}
              </li>
            ))}
          </ul>
        </div>
      )}

      {loading && <p className="text-muted mt-3">Loading...</p>}
    </div>
  );
};

export default WeatherAndMarketComponent;
