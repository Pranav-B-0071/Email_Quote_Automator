// Welcome.jsx
import React from 'react';
import { useParams } from 'react-router-dom';
import './Welcome.css';

function Welcome() {
  const { username } = useParams();

  return (
    <div className="welcome-container">
      <h1>🌟 Welcome, {username}! 🌟</h1>
      <p>We're excited to have you in your universe of possibilities.</p>
    </div>
  );
}

export default Welcome;
