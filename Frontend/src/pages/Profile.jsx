import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { ensureDeviceExists } from "../services/DeviceService";
import { getProfile, updatePassword, updateProfile } from "../services/ProfileService";
import { logout } from "../services/AuthService";
import "./Profile.css";
import SessionRating from "../components/SessionRating";
import {
  Eye,
  EyeOff,
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

const DEFAULT_DEVICE_ID = "arduino-device-01";

const Profile = () => {
  const navigate = useNavigate();
  const userData = localStorage.getItem("user");
  const user = readUser();

  const [passwordForm, setPasswordForm] = useState({
    current: "",
    next: "",
    confirmNext: "",
  });
  const [isEditing, setIsEditing] = useState(false);
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNextPassword, setShowNextPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [deviceId, setDeviceId] = useState(DEFAULT_DEVICE_ID);
  const [connectedDeviceId, setConnectedDeviceId] = useState("");

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

    const loadConnectedDevice = () => {
      const userDevices = JSON.parse(localStorage.getItem("user_devices")) || [];
      const connectedDevice = userDevices.find(
        (device) => device.email === user?.email,
      );

      setConnectedDeviceId(connectedDevice?.deviceId || "");
      setDeviceId(connectedDevice?.deviceId || DEFAULT_DEVICE_ID);
    };

    loadProfile();
    loadConnectedDevice();
  }, [userData, user?.email]);

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
      await saveProfile();

      setIsEditing(false);
      alert("Information has been saved!");
    } catch (e) {
      console.error(e);
      alert(e.message || "Failed to save profile");
    }
  };

  const handleConnectDevice = async () => {
    const id = deviceId.trim();
    if (!id) {
      alert("Please enter an ID");
      return;
    }

    try {
      await ensureDeviceExists(id);
    } catch (error) {
      console.error(error);
      alert(error.message);
      return;
    }

    const userDevices = JSON.parse(localStorage.getItem("user_devices")) || [];
    const otherDevices = userDevices.filter(
      (device) => device.email !== user.email,
    );
    localStorage.setItem(
      "user_devices",
      JSON.stringify([...otherDevices, { email: user.email, deviceId: id }]),
    );
    setConnectedDeviceId(id);
    setDeviceId(id);
    window.dispatchEvent(new Event("storage"));
    alert("Device " + id + " connected to your account!");
  };

  const saveProfile = async (profilePic = studentInfo.profilePic) => {
    await updateProfile({
      university: studentInfo.university,
      study_program: studentInfo.StudyProgram,
      study_year: studentInfo.year,
      study_goal: studentInfo.goal,
      preferred_temp: prefs.temp,
      preferred_co2: prefs.co2,
      profile_picture: profilePic,
    });
  };

  const handleUpdatePassword = async () => {
    const { current, next, confirmNext } = passwordForm;

    if (!current || !next || !confirmNext) {
      alert("Please fill in all password fields.");
      return;
    }

    if (next.length < 8) {
      alert("New password too short!");
      return;
    }

    if (next !== confirmNext) {
      alert("New passwords do not match.");
      return;
    }

    try {
      await updatePassword({
        current_password: current,
        new_password: next,
      });

      alert("Password changed successfully!");
      setPasswordForm({ current: "", next: "", confirmNext: "" });
    } catch (error) {
      console.error(error);
      alert(error.message || "Failed to update password");
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const profilePic = reader.result;
        setStudentInfo({ ...studentInfo, profilePic });

        try {
          await saveProfile(profilePic);
        } catch (error) {
          console.error(error);
          alert(error.message || "Failed to save profile photo");
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const completeLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error("Error clearing auth cookie:", error);
    }

    localStorage.removeItem("user");
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
              <UserRoundKey size={18} /> Change Password
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
                  {showCurrentPassword ? <Eye size={18} /> : <EyeOff size={18} />}
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
                  {showNextPassword ? <Eye size={18} /> : <EyeOff size={18} />}
                </button>
              </div>
            </div>
            <div className="setting-row">
              <span className="setting-label">Confirm:</span>
              <div className="password-input-wrapper">
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  value={passwordForm.confirmNext}
                  onChange={(e) =>
                    setPasswordForm({
                      ...passwordForm,
                      confirmNext: e.target.value,
                    })
                  }
                  className="profile-input"
                />
                <button
                  type="button"
                  className="password-toggle-btn"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <Eye size={18} /> : <EyeOff size={18} />}
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
            {connectedDeviceId && (
              <p className="connected-device-status">
                Connected device: <strong>{connectedDeviceId}</strong>
              </p>
            )}
            <div className="setting-row">
              <span>Device ID:</span>
              <input
                type="text"
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
                placeholder={DEFAULT_DEVICE_ID}
                className="profile-input"
                id="deviceIdInput"
              />
            </div>
            <button className="update-btn-full" onClick={handleConnectDevice}>
              {connectedDeviceId ? "Save Device" : "Connect Now"}
            </button>
          </div>
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

            <SessionRating
              submitLabel="Submit & Logout"
              allowSuccessOnError
              onSuccess={completeLogout}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
