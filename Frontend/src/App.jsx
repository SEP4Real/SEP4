import { Routes, Route } from "react-router-dom";
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import History from "./pages/History";
import Navbar from "./components/Navbar";
import StudentDashboard from "./pages/StudentDashboard";
import CalendarPage from "./pages/CalendarPage";
import Profile from './pages/Profile';
import ProtectedRoute from "./components/ProtectedRoute";
import PublicRoute from "./components/PublicRoute";


function App() {
  return (
    <>
      <Navbar />

      <Routes>
        <Route path="/" element={<RegisterPage />} />
        import PublicRoute from "./components/PublicRoute";

        {/* public routes */}
        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />

        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />

        {/* protected routes */}
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <History />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student"
          element={
            <ProtectedRoute>
              <StudentDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/calendar"
          element={
            <ProtectedRoute>
              <CalendarPage />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<RegisterPage />} />
      </Routes>
    </>
  );
}

export default App;