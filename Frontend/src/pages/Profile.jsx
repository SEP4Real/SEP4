import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { getDashboardData } from "../services/DashboardService";
import { getProfile, updateProfile } from "../services/ProfileService";
import "./Profile.css";
import SessionRating from "../components/SessionRating";
import {
  Eye,
  EyeOff,
  History,
  ImageUp,
  LogOut,
  Unplug,
  UserRoundKey,
  UserRoundPen,
} from "lucide-react";

const readUser = () => {
  const userData = localStorage.getItem("user");

  if (!userData || userData === "undefined") {
    return null;
  }

  try {
    return JSON.parse(userData);
  } catch (e) {
    console.error("Error reading user from storage", e);
    return null;
  }
};

const Profile = () => {
  const navigate = useNavigate();
  const userData = localStorage.getItem("user");
  const user = readUser();

  const [recentHistory, setRecentHistory] = useState([]);
  const [passwordForm, setPasswordForm] = useState({ current: "", next: "" });
  const [isEditing, setIsEditing] = useState(false);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNextPassword, setShowNextPassword] = useState(false);

  const [studentInfo, setStudentInfo] = useState({
    university: "",
    StudyProgram: "",
    year: "",
    goal: "",
    profilePic: null,
  });

  const [prefs, setPreferences] = useState({
    temp: 22,
    co2: 800,
  });

  useEffect(() => {
    if (!userData) {
      return;
    }

    const loadProfile = async () => {
      try {
        const result = await getProfile();

        if (result.profile) {
          setStudentInfo({
            university: result.profile.university || "",
            StudyProgram: result.profile.study_program || "",
            year: result.profile.study_year || "",
            goal: result.profile.study_goal || "",
            profilePic: result.profile.profile_picture || null,
          });

          setPreferences({
            temp: result.profile.preferred_temp || 22,
            co2: result.profile.preferred_co2 || 800,
          });
        }
      } catch (e) {
        console.error("Error loading profile:", e);
      }
    };

    const loadData = async () => {
      try {
        const data = await getDashboardData();
        if (Array.isArray(data) && data.length > 0) {
          setRecentHistory([...data].reverse().slice(0, 3));
        }
      } catch (e) {
        console.error("Error loading history:", e);
      }
    };

    loadData();
    loadProfile();
  }, [userData]);

  if (!userData || !user) {
    return <Navigate to="/login" replace />;
  }

  const displayName =
    [user.name, user.last_name || user.lastName].filter(Boolean).join(" ") ||
    user.email;

  const calculateProgress = () => {
    const fields = [
      user?.name,
      studentInfo.university,
      studentInfo.StudyProgram,
      studentInfo.year,
      studentInfo.goal,
      studentInfo.profilePic,
    ];
    const completed = fields.filter((field) => field && field !== "").length;
    return Math.round((completed / fields.length) * 100);
  };

  const handleSaveStudent = async () => {
    try {
      await updateProfile({
        university: studentInfo.university,
        study_program: studentInfo.StudyProgram,
        study_year: studentInfo.year,
        study_goal: studentInfo.goal,
        preferred_temp: prefs.temp,
        preferred_co2: prefs.co2,
        profile_picture: studentInfo.profilePic,
      });

      setIsEditing(false);
      alert("Information has been saved!");
    } catch (e) {
      console.error(e);
      alert("Failed to save profile");
    }
  };

  const handleConnectDevice = () => {
    const id = document.getElementById("deviceIdInput").value;
    if (!id) {
      alert("Please enter an ID");
      return;
    }

    const userDevices = JSON.parse(localStorage.getItem("user_devices")) || [];
    const alreadyConnected = userDevices.find(
      (device) => device.email === user.email && device.deviceId === id,
    );

    if (alreadyConnected) {
      alert("This device is already connected to your account!");
      return;
    }

    userDevices.push({ email: user.email, deviceId: id });
    localStorage.setItem("user_devices", JSON.stringify(userDevices));
    window.dispatchEvent(new Event("storage"));
    alert("Device " + id + " connected to your account!");
  };

  const handleUpdatePassword = () => {
    const { current, next } = passwordForm;
    const storedUser = JSON.parse(localStorage.getItem("user"));
    const allUsers = JSON.parse(localStorage.getItem("users")) || [];

    if (!storedUser) {
      alert("You are not logged in! Please log in again.");
      return;
    }

    if (!storedUser.password) {
      alert("Password updates are not available yet.");
      return;
    }

    if (storedUser.password !== current) {
      alert("Current password is incorrect!");
      return;
    }

    if (next.length < 8) {
      alert("New password too short!");
      return;
    }

    const updatedUser = { ...storedUser, password: next };
    localStorage.setItem("user", JSON.stringify(updatedUser));

    const userIdx = allUsers.findIndex((item) => item.email === storedUser.email);
    if (userIdx !== -1) {
      allUsers[userIdx].password = next;
      localStorage.setItem("users", JSON.stringify(allUsers));
    }

    alert("Password changed successfully!");
    setPasswordForm({ current: "", next: "" });
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setStudentInfo({ ...studentInfo, profilePic: reader.result });
        localStorage.setItem("stud_pic", reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const completeLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    window.dispatchEvent(new Event("storage"));
    navigate("/login", { replace: true });
  };

  return (
    <div className="profile-page-container">
      <div className="profile-card-wrapper">
        <h1>User Profile</h1>
        <h1>Welcome, {user?.name}</h1>

        <div className="completion-container">
          <div className="completion-text">
            <span>
              <UserRoundPen size={18} /> Profile Completion
            </span>
            <strong>{calculateProgress()}%</strong>
          </div>
          <div className="progress-bar-bg">
            <div
              className="progress-bar-fill"
              style={{ width: `${calculateProgress()}%` }}
            ></div>
          </div>
        </div>

        <div className="profile-section student-header-box">
          <div className="profile-header-new">
            <div className="avatar-side">
              <div className="profile-avatar">
                {studentInfo.profilePic ? (
                  <img src={studentInfo.profilePic} alt="Profile" />
                ) : (
                  (user?.name || user?.email || "U").charAt(0).toUpperCase()
                )}
              </div>
              <label className="upload-label">
                <span>
                  <ImageUp size={16} /> Change Photo
                </span>
                <input type="file" onChange={handleImageChange} hidden />
              </label>
            </div>

            <div className="info-side">
              <div className="profile-name-header">
                <h2>{displayName}</h2>
                <button
                  className="logout-btn-top"
                  onClick={() => setShowRatingModal(true)}
                >
                  <LogOut size={16} /> Logout
                </button>
              </div>

              <p className="user-email-display">{user?.email}</p>

              <div className="student-details-grid">
                <div className="detail-item">
                  <span>University:</span>
                  {isEditing ? (
                    <input
                      value={studentInfo.university}
                      onChange={(e) =>
                        setStudentInfo({
                          ...studentInfo,
                          university: e.target.value,
                        })
                      }
                    />
                  ) : (
                    <strong>{studentInfo.university || "Not set"}</strong>
                  )}
                </div>
                <div className="detail-item">
                  <span>Program:</span>
                  {isEditing ? (
                    <input
                      value={studentInfo.StudyProgram}
                      onChange={(e) =>
                        setStudentInfo({
                          ...studentInfo,
                          StudyProgram: e.target.value,
                        })
                      }
                    />
                  ) : (
                    <strong>{studentInfo.StudyProgram || "Not set"}</strong>
                  )}
                </div>
                <div className="detail-item">
                  <span>Year:</span>
                  {isEditing ? (
                    <input
                      value={studentInfo.year}
                      onChange={(e) =>
                        setStudentInfo({ ...studentInfo, year: e.target.value })
                      }
                    />
                  ) : (
                    <strong>{studentInfo.year || "Not set"}</strong>
                  )}
                </div>
                <div className="detail-item">
                  <span>Goal:</span>
                  {isEditing ? (
                    <input
                      value={studentInfo.goal}
                      onChange={(e) =>
                        setStudentInfo({ ...studentInfo, goal: e.target.value })
                      }
                    />
                  ) : (
                    <strong>{studentInfo.goal || "Not set"}</strong>
                  )}
                </div>
              </div>

              <div className="header-action-btns">
                {isEditing ? (
                  <button className="update-btn-full" onClick={handleSaveStudent}>
                    Save Changes
                  </button>
                ) : (
                  <button
                    className="update-btn-full"
                    onClick={() => setIsEditing(true)}
                  >
                    Edit Profile
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="profile-row-grid">
          <div className="profile-section">
            <h3>
              <UserRoundKey size={18} /> Password & Security
            </h3>
            <div className="setting-row">
              <span className="setting-label">Current:</span>
              <div className="password-input-wrapper">
                <input
                  type={showCurrentPassword ? "text" : "password"}
                  value={passwordForm.current}
                  onChange={(e) =>
                    setPasswordForm({
                      ...passwordForm,
                      current: e.target.value,
                    })
                  }
                  className="profile-input"
                />
                <button
                  type="button"
                  className="password-toggle-btn"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                >
                  {showCurrentPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            <div className="setting-row">
              <span className="setting-label">New:</span>
              <div className="password-input-wrapper">
                <input
                  type={showNextPassword ? "text" : "password"}
                  value={passwordForm.next}
                  onChange={(e) =>
                    setPasswordForm({ ...passwordForm, next: e.target.value })
                  }
                  className="profile-input"
                />
                <button
                  type="button"
                  className="password-toggle-btn"
                  onClick={() => setShowNextPassword(!showNextPassword)}
                >
                  {showNextPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>
            <button className="update-btn-full" onClick={handleUpdatePassword}>
              Update Password
            </button>
          </div>

          <div className="profile-section">
            <h3>
              <Unplug size={18} /> Connect Device
            </h3>
            <div className="setting-row">
              <span>Device ID:</span>
              <input
                type="text"
                placeholder="Ex: DEV-123"
                className="profile-input"
                id="deviceIdInput"
              />
            </div>
            <button className="update-btn-full" onClick={handleConnectDevice}>
              Connect Now
            </button>
          </div>
        </div>

        <div className="profile-row-grid">
          <div className="profile-section">
            <h3>AI Insights (MAL)</h3>
            <div className="ai-bubble-new">
              Suggestion: Maintain {prefs.temp}C for better focus.
            </div>
          </div>

          <div className="profile-section">
            <h3>
              <History size={18} /> History (Last 3)
            </h3>
            <table className="history-table-compact">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Temp</th>
                  <th>CO2</th>
                </tr>
              </thead>
              <tbody>
                {recentHistory.map((item, idx) => (
                  <tr key={idx}>
                    <td>{new Date(item.sent_at).toLocaleDateString()}</td>
                    <td>{item.temperature}C</td>
                    <td>{item.co2_level}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
            {showRatingModal && (
        <div className="rating-modal">
          <div className="rating-modal-content">
            <button
              className="close-rating-modal"
              onClick={() => setShowRatingModal(false)}
            >
              ×
            </button>

            <SessionRating onSuccess={completeLogout} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;