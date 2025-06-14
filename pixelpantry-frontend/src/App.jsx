import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./Home";
import NewsPage from "./NewsPage";
//import FarmQuest from "./FarmQuest"; 
import ProfilePage from "./ProfilePage"; 
//import NgoList from "./components/NgoList"; 
import Chatbot from "./components/chatbot"; // ✅ Import Chatbot Component
import HomePage from "./HomePage";
import CropAnalysis from './CropAnalysis';
import "./App.css"; 

function App() {
  return (
    <Router>
      <div className="App">
            
        {/* Navigation Bar */}
        <header className="cropnavbar">
          {/* Back Button and Logo */}
          <div className="back-and-logo">
            <button 
              className="back-button" 
              onClick={() => window.history.back()}
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
              </svg>
              Back
            </button>
            {/*<h2 className="logo">Pixel Pantry</h2>*/}
          </div>

          {/* Centered Text */}
          <h3 className="centered-text">Crop Guard</h3>

          {/* Navigation Links */}
          {/*
          <nav className="nav-links">
            <Link to="/cropguard">Home</Link>
            <Link to="/news">News</Link>
            <Link to="/">HomePage</Link>
            <Link to="/profile">Profile</Link>
          </nav>*/}
        </header>







        {/* Routes */}
        <Routes>
          <Route path="/cropguard" element={<Home />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/" element = {<HomePage/>}/>
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/cropanalysis" element={<CropAnalysis />} />
          
          
        </Routes>

        {/* Floating Chatbot Component (Accessible on All Pages) */}
        <Chatbot />

        {/* Footer */}
        <footer className="footer">
          <p>© {new Date().getFullYear()} Pixel Pantry - Technology Meets Sustainability</p>
          <p style={{ fontSize: '0.9rem', marginTop: '0.5rem', opacity: '0.7' }}>
          Helping farmers make data-driven decisions for sustainable agriculture
          </p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
