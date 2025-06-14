import './HomePage.css';
import { Link } from 'react-router-dom';
import cropAnalysisIcon from './assets/crop-analysis.jpg';
import cropGuardIcon from './assets/crop-guard.jpg';
import connectIcon from './assets/connect.jpg';
import logo from './assets/logo.png';

const HomePage = () => {
  return (
    <div className="home-page">
      {/* Navigation Bar */}
      <div className="navbar">
        <div className="logo-container">
          <img src={logo} alt="Pixel Pantry Logo" className="logo-img" />
          <a href="#" className="logo">Pixel Pantry</a>
        </div>
        <div className="nav-links">
          <a href="#">About</a>
          <a href="#">Contact</a>
          <a href="#">Sustainability</a>
          <a href="#">Profile</a>
        </div>
      </div>

      {/* Main Content */}
      <div className="container">
        <div className="hero-section">
          <h1 className="main-heading">Home</h1>
        </div>

        <div className="feature-cards">
          <div className="feature-card">
            <div className="card-image">
            <Link to="/cropanalysis">
              <img src={cropAnalysisIcon} alt="Crop Analysis" />
            </Link>
            </div>
            <h3>Crop Analysis</h3>
          </div>

          <div className="feature-card">
            <div className="card-image">
            <Link to="/cropguard">
              <img src={cropGuardIcon} alt="cropguard" />
            </Link>
            </div>
            <h3>Crop Guard</h3>
          </div>

          <div className="feature-card">
            <div className="card-image">
              <img src={connectIcon} alt="Connect" />
            </div>
            <h3>Connect</h3>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;