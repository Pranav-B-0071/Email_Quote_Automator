import './GoogleSignIn.css';
import React, { useState } from 'react';

function GoogleSignIn() {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleSignIn = () => {
    setIsLoading(true);
    
    // Simulate loading animation before redirect
    setTimeout(() => {
      window.location.href = "http://localhost:8000/auth";
    }, 1500);
  };

  return (
    <div className="container">
      {/* Background stars */}
      {Array(20).fill().map((_, i) => (
        <div 
          key={i}
          className="star"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 3}s`,
            animationDuration: `${2 + Math.random() * 2}s`,
          }}
        />
      ))}
      
      {/* Background orbs */}
      {Array(8).fill().map((_, i) => (
        <div
          key={`orb-${i}`}
          className="orb"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            width: `${50 + Math.random() * 100}px`,
            height: `${50 + Math.random() * 100}px`,
            animationDelay: `${Math.random() * 2}s`,
            animationDuration: `${4 + Math.random() * 2}s`,
          }}
        />
      ))}

      {/* Main content */}
      <div className="content">
        <div className="title">
          <h1>✨ Welcome Back ✨</h1>
          <p>Enter your realm of possibilities</p>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="icon-container">
              <span className="sparkle">✨</span>
            </div>
            <h2>Sign Into Your Universe</h2>
            <p>One click to unlock infinite adventures</p>
          </div>

          <div className="card-content">
            <button 
              onClick={handleGoogleSignIn} 
              disabled={isLoading}
              className="google-button"
            >
              {isLoading ? (
                <div className="loading">
                  <div className="spinner"></div>
                  <span>Entering your realm...</span>
                </div>
              ) : (
                <div className="button-content">
                  <svg className="google-icon" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  <span>Continue with Google</span>
                  <span className="sparkle">✨</span>
                </div>
              )}
            </button>

            <p className="footer-text">Ready to explore infinite possibilities? ✨</p>
          </div>
        </div>

        <div className="dots">
          {Array(5).fill().map((_, i) => (
            <div 
              key={i} 
              className="dot"
              style={{ animationDelay: `${i * 0.2}s` }}
            />
          ))}
        </div>
      </div>

      <style jsx>{`
        /* CSS will be included inline */
      `}</style>
    </div>
  );
}

export default GoogleSignIn;