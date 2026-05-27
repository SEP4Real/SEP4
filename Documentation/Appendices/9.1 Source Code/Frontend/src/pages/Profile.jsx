import { useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { ensureDeviceExists } from "../services/DeviceService";
import { getProfile, updatePassword, updateProfile } from "../services/ProfileService";
import { logout } from "../services/AuthService";
import "./Profile.css";
import { useLanguage } from "../context/LanguageContext";
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

const getStoredDeviceForUser = (email) => {
  const userDevices = JSON.parse(localStorage.getItem("user_devices")) || [];
  const connectedDevice = userDevices.find((device) => device.email === email);

  return connectedDevice?.deviceId || "";
};

const Profile = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const userData = localStorage.getItem("user");
  const user = readUser();

  const [passwordForm, setPasswordForm] = useState({
    current: "",
    next: "",
    confirmNext: "",
  });
  const [isEditing, setIsEditing] = useState(false);
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
          const savedDeviceId =
            result.profile.connected_device_id || getStoredDeviceForUser(user?.email);

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

          setConnectedDeviceId(savedDeviceId);
          setDeviceId(savedDeviceId || DEFAULT_DEVICE_ID);
        }
      } catch (e) {
        console.error("Error loading profile:", e);
      }
    };

    const loadConnectedDevice = () => {
      const storedDeviceId = getStoredDeviceForUser(user?.email);

      setConnectedDeviceId(storedDeviceId);
      setDeviceId(storedDeviceId || DEFAULT_DEVICE_ID);
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
      alert(t.profileSaved);
    } catch (e) {
      console.error(e);
      alert(e.message || t.profileSaveFailed);
    }
  };

  const handleConnectDevice = async () => {
    const id = deviceId.trim();
    if (!id) {
      alert(t.profileSaveFailed);
      return;
    }

    try {
      await ensureDeviceExists(id);
      await saveProfile(studentInfo.profilePic, id);
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
   alert(`${t.deviceConnected} ${id}`);
  };

  const saveProfile = async (
    profilePic = studentInfo.profilePic,
    deviceIdToSave = connectedDeviceId,
  ) => {
    await updateProfile({
      university: studentInfo.university,
      study_program: studentInfo.StudyProgram,
      study_year: studentInfo.year,
      study_goal: studentInfo.goal,
      preferred_temp: prefs.temp,
      preferred_co2: prefs.co2,
      connected_device_id: deviceIdToSave || null,
      profile_picture: profilePic,
    });
  };

  const handleUpdatePassword = async () => {
    const { current, next, confirmNext } = passwordForm;

    if (!current || !next || !confirmNext) {
      alert(t.fillPasswordFields);
      return;
    }

    if (next.length < 8) {
      alert(t.newPasswordTooShort);
      return;
    }

    if (next !== confirmNext) {
      alert(t.passwordsDoNotMatch);
      return;
    }

    try {
      await updatePassword({
        current_password: current,
        new_password: next,
      });

      alert(t.passwordChanged);
      setPasswordForm({ current: "", next: "", confirmNext: "" });
    } catch (error) {
      console.error(error);
      alert(error.message || t.passwordUpdateFailed);
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
          alert(error.message || t.profilePhotoSaveFailed);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const completeLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error(t.logoutCookieClearError, error);
    }

    localStorage.removeItem("user");
    window.dispatchEvent(new Event("storage"));
    navigate("/login", { replace: true });
  };

  return (
    <div className="profile-page-container">
      <div className="profile-card-wrapper">
        <h1>{t.profileTitle}</h1>
<h1>{t.welcome}, {user?.name}</h1>

        <div className="completion-container">
          <div className="completion-text">
            <span>
              <UserRoundPen size={18} /> {t.profileCompletion}
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
                  <img src={studentInfo.profilePic} alt={t.profileImageAlt} />
                ) : (
                  (user?.name || user?.email || "U").charAt(0).toUpperCase()
                )}
              </div>
              <label className="upload-label">
                <span>
                  <ImageUp size={16} /> {t.changePhoto}
                </span>
                <input type="file" onChange={handleImageChange} hidden />
              </label>
            </div>

            <div className="info-side">
              <div className="profile-name-header">
                <h2>{displayName}</h2>
                <button
                  className="logout-btn-top"
                  onClick={completeLogout}
                >
                 <LogOut size={16} /> {t.logout}
                </button>
              </div>

              <p className="user-email-display">{user?.email}</p>

              <div className="student-details-grid">
                <div className="detail-item">
                  <span>{t.university}:</span>
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
                    <strong>{studentInfo.university || t.notSet}</strong>
                  )}
                </div>
                <div className="detail-item">
                  <span>{t.program}:</span>
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
                    <strong>{studentInfo.StudyProgram || t.notSet}</strong>
                  )}
                </div>
                <div className="detail-item">
                  <span>{t.year}:</span>
                  {isEditing ? (
                    <input
                      value={studentInfo.year}
                      onChange={(e) =>
                        setStudentInfo({ ...studentInfo, year: e.target.value })
                      }
                    />
                  ) : (
                    <strong>{studentInfo.year || t.notSet}</strong>
                  )}
                </div>
                <div className="detail-item">
                  <span>{t.goal}:</span>
                  {isEditing ? (
                    <input
                      value={studentInfo.goal}
                      onChange={(e) =>
                        setStudentInfo({ ...studentInfo, goal: e.target.value })
                      }
                    />
                  ) : (
                    <strong>{studentInfo.goal || t.notSet}</strong>
                  )}
                </div>
              </div>

              <div className="header-action-btns">
                {isEditing ? (
                  <button className="update-btn-full" onClick={handleSaveStudent}>
                    {t.saveChanges}
                  </button>
                ) : (
                  <button
                    className="update-btn-full"
                    onClick={() => setIsEditing(true)}
                  >
                    {t.editProfile}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="profile-row-grid">
          <div className="profile-section">
            <h3>
              <UserRoundKey size={18} /> {t.changePassword}
            </h3>
            <div className="setting-row">
              <span className="setting-label">{t.currentPassword}:</span>
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
              <span className="setting-label">{t.newPassword}:</span>
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
              <span className="setting-label">{t.confirmPassword}:</span>
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
              {t.updatePassword}
            </button>
          </div>

          <div className="profile-section device-section">
            <h3>
              <Unplug size={18} /> {t.connectDevice}</h3>
            {connectedDeviceId && (
              <p className="connected-device-status">
                {t.connectedDevice}:<strong>{connectedDeviceId}</strong>
              </p>
            )}
            <div className="setting-row">
              <span>{t.deviceId}:</span>
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
              {connectedDeviceId  ? t.saveDevice  : t.connectNow}
            </button>
          </div>
        </div>

        </div>

    </div>
  );
};

export default Profile;
