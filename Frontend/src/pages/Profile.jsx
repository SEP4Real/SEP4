import { Navigate, useNavigate } from 'react-router-dom';
import './Profile.css';

const Profile = () => {
  const navigate = useNavigate();
  const userData = localStorage.getItem('user');
  if (!userData) {
    return <Navigate to="/login" replace />;
  }
  // no data - log out
  if (!userData) {
    return <Navigate to="/login" replace />;
  }

  // test user
  const user = JSON.parse(localStorage.getItem('user')) || {
    name: "Test User",
    email: "test@test.com",
    role: "Premium Member"
  };

  const handleLogout = () => {
    localStorage.removeItem("user"); // better than clear()
    window.dispatchEvent(new Event("storage")); // 🔥 force update
    navigate('/login', { replace: true });
  };

 return (
  <div className="profile-page-container">
    <div className="profile-card-wrapper">
      <h1>User Profile</h1>
      
      <div className="profile-content-grid">
        {/* info Card */}
        <div className="profile-section">
          <div className="profile-avatar">
            {user.name.charAt(0)}
          </div>
          <div className="profile-info">
            <h2>{user.name}</h2>
            <p>{user.email}</p>
            <span className="profile-badge">{user.role}</span>
          </div>
          <div style={{textAlign: 'center'}}>
            <button className="logout-btn" onClick={handleLogout}>Logout</button>
          </div>
        </div>

        {/* pref Card */}
        <div className="profile-section" style={{marginTop: '20px'}}>
          <h3 style={{color: '#1b5e20', marginBottom: '15px'}}>Environment Preferences</h3>
          
          <div className="setting-row">
            <span>Ideal Temperature (°C)</span>
            <input type="number" className="profile-input" defaultValue="22" />
          </div>
          
          <div className="setting-row">
            <span>CO2 Max Threshold (ppm)</span>
            <input type="number" className="profile-input" defaultValue="800" />
          </div>

          <div className="setting-row">
            <span>Notification Alerts</span>
            <input type="checkbox" defaultChecked style={{accentColor: '#4CAF50', transform: 'scale(1.2)'}} />
          </div>

          <button className="save-btn">Update Preferences</button>
        </div>
      </div>
    </div>
  </div>
);
};

export default Profile;
