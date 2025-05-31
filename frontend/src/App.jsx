// App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import GoogleSignIn from './GoogleSignIn';
import Welcome from './Welcome';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/signin" element={<GoogleSignIn />} />
          <Route path="/welcome/:username" element={<Welcome />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
