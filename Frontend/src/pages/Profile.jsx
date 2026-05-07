import { useState, useEffect } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { getEnvironmentData } from "../services/EnvironmentService";
import './Profile.css';

const Profile = () => {
  const navigate = useNavigate();
  const userData = JSON.parse(localStorage.getItem('user'));

  const [recentHistory, setRecentHistory] = useState([]);
  const [stats, setStats] = useState({ totalSessions: 0, lastActivity: "--" });
  const [passwordForm, setPasswordForm] = useState({ current: "", next: "" });
  const [isEditing, setIsEditing] = useState(false);

  const [studentInfo, setStudentInfo] = useState({
    university: localStorage.getItem('stud_uni') || "",
    StudyProgram: localStorage.getItem('stud_prog') || "",
    year: localStorage.getItem('stud_year') || "",
    goal: localStorage.getItem('stud_goal') || "",
    profilePic: localStorage.getItem('stud_pic') || null
  });

  const [prefs, setPreferences] = useState({
    temp: localStorage.getItem('pref_temp') || 22,
    co2: localStorage.getItem('pref_co2') || 800,
  });

  useEffect(() => {
    if (!userData) return;
    const loadData = async () => {
      try {
        const data = await getEnvironmentData();
        if (data && data.length > 0) {
          setStats({ 
            totalSessions: data.length, 
            lastActivity: new Date(data[data.length - 1].sentAt).toLocaleDateString() 
          });
          setRecentHistory([...data].reverse().slice(0, 3));
        }
      } catch (e) { console.error("Error loading history:", e); }
    };
    loadData();
  }, [userData]);

  if (!userData) return <Navigate to="/login" replace />;

  const calculateProgress = () => {
    let fields = [userData.name, studentInfo.university, studentInfo.StudyProgram, studentInfo.year, studentInfo.goal, studentInfo.profilePic];
    let completed = fields.filter(f => f && f !== "").length;
    return Math.round((completed / fields.length) * 100);
  };

  const handleSaveStudent = () => {
    localStorage.setItem('stud_uni', studentInfo.university);
    localStorage.setItem('stud_prog', studentInfo.StudyProgram);
    localStorage.setItem('stud_year', studentInfo.year);
    localStorage.setItem('stud_goal', studentInfo.goal);
    setIsEditing(false); 
    alert("Information has been saved!");
  };

  const handleSaveAll = () => {
    handleSaveStudent();
    localStorage.setItem('pref_temp', prefs.temp);
    localStorage.setItem('pref_co2', prefs.co2);
    alert("Profile and Preferences updated!");
  };

  const handleUpdatePassword = () => {
    const allUsers = JSON.parse(localStorage.getItem("users")) || [];
    const userIdx = allUsers.findIndex(u => u.email === userData.email);

    if (userIdx === -1 || allUsers[userIdx].password !== passwordForm.current) {
      alert("Current password is incorrect!");
      return;
    }
    if (passwordForm.next.length < 3) {
      alert("New password too short!");
      return;
    }

    allUsers[userIdx].password = passwordForm.next;
    localStorage.setItem("users", JSON.stringify(allUsers));
    alert("Password changed! Use it at next login.");
    setPasswordForm({ current: "", next: "" });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setStudentInfo({ ...studentInfo, profilePic: reader.result });
        localStorage.setItem('stud_pic', reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user");
    window.dispatchEvent(new Event("storage"));
    navigate('/login', { replace: true });
  };

  return (
    <div className="profile-page-container">
  <div className="profile-card-wrapper">
    <h1>User Profile</h1>

    {/* PROGRESS */}
    <div className="completion-container">
      <div className="completion-text">
        <span>Profile Completion</span>
        <strong>{calculateProgress()}%</strong>
      </div>
      <div className="progress-bar-bg">
        <div className="progress-bar-fill" style={{ width: `${calculateProgress()}%` }}></div>
      </div>
    </div>

    {/* INFO */}
    <div className="profile-section student-header-box">
      <div className="profile-header-new">
        <div className="avatar-side">
          <div className="profile-avatar">
            {studentInfo.profilePic ? <img src={studentInfo.profilePic} alt="Profile" /> : userData.name.charAt(0).toUpperCase()}
          </div>
          <label className="upload-label">
            <span>Change Photo</span>
            <input type="file" onChange={handleImageChange} hidden />
          </label>
        </div>

        <div className="info-side">
          <div className="profile-name-header">
            <h2>{userData.name} {userData.lastName}</h2>
            <button className="logout-btn-top" onClick={handleLogout}>Logout</button>
          </div>
          
          <p className="user-email-display">{userData.email}</p>
          
          <div className="student-details-grid">
            <div className="detail-item">
              <span>University:</span> 
              {isEditing ? <input value={studentInfo.university} 
              onChange={e => setStudentInfo({...studentInfo, university: e.target.value})} /> 
              : <strong>{studentInfo.university || "Not set"}</strong>}
            </div>
            <div className="detail-item">
              <span>Program:</span> 
              {isEditing ? <input value={studentInfo.StudyProgram} 
              onChange={e => setStudentInfo({...studentInfo, StudyProgram: e.target.value})} />
               : <strong>{studentInfo.StudyProgram || "Not set"}</strong>}
            </div>
            <div className="detail-item">
              <span>Year:</span> 
              {isEditing ? <input value={studentInfo.year} 
              onChange={e => setStudentInfo({...studentInfo, year: e.target.value})} />
               : <strong>{studentInfo.year || "Not set"}</strong>}
            </div>
            <div className="detail-item">
              <span>Goal:</span> 
              {isEditing ? <input value={studentInfo.goal} 
              onChange={e => setStudentInfo({...studentInfo, goal: e.target.value})} /> 
              : <strong>{studentInfo.goal || "Not set"}</strong>}
            </div>
          </div>

          <div className="header-action-btns">
            {isEditing ? (
              <button className="update-btn-full" onClick={handleSaveStudent}>Save Changes</button>
            ) : (
              <button className="update-btn-full" onClick={() => setIsEditing(true)}>Edit Profile</button>
            )}
          </div>
        </div>
      </div>
    </div>

    {/* SECURITY & PREFS */}
    <div className="profile-row-grid">
      <div className="profile-section">
        <h3>🔒 Security 🔒</h3>
        <div className="setting-row">
          <span>Current:</span>
          <input type="password" value={passwordForm.current} onChange={e => setPasswordForm({...passwordForm, current: e.target.value})} className="profile-input" />
        </div>
        <div className="setting-row">
          <span>New:</span>
          <input type="password" value={passwordForm.next} onChange={e => setPasswordForm({...passwordForm, next: e.target.value})} className="profile-input" />
        </div>
        <button className="update-btn-full" onClick={handleUpdatePassword}>Update Password</button>
      </div>

      <div className="profile-section">
        <h3>⚙️ Preferences ⚙️</h3>
        <div className="setting-row">
          <span>Ideal Temp:</span>
          <input type="number" value={prefs.temp} onChange={e => setPreferences({...prefs, temp: e.target.value})} className="profile-input" />
        </div>
        <div className="setting-row">
          <span>Max CO2:</span>
          <input type="number" value={prefs.co2} onChange={e => setPreferences({...prefs, co2: e.target.value})} className="profile-input" />
        </div>
        <button className="update-btn-full" onClick={handleSaveAll}>Save Info</button>
      </div>
    </div>

    {/* GRID JOS: AI & HISTORY */}
    <div className="profile-row-grid">
      <div className="profile-section">
        <h3>🤖 AI Insights 🤖 (MAL)</h3>
        <div className="ai-bubble-new">
          Suggestion: Maintain {prefs.temp}°C for better focus.
        </div>
      </div>

      <div className="profile-section">
        <h3>🕒 History 🕒 (Last 3)</h3>
        <table className="history-table-compact">
          <thead>
            <tr><th>Date</th><th>Temp</th><th>CO2</th></tr>
          </thead>
          <tbody>
            {recentHistory.map((item, idx) => (
              <tr key={idx}>
                <td>{new Date(item.sentAt).toLocaleDateString()}</td>
                <td>{item.temperature}°C</td>
                <td>{item.co2Level}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
  );
};

export default Profile;