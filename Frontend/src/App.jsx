import { Routes, Route } from "react-router-dom";
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import History from "./pages/History";
import Navbar from "./components/Navbar";
import StudentDashboard from "./pages/StudentDashboard";

import Profile from './pages/Profile';


function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path="/" element={<RegisterPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/history" element={<History />} />
        <Route path="/student" element={<StudentDashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="*" element={<RegisterPage />} />
      </Routes>
    </>
  );
}

export default App;