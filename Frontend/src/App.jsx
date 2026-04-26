import { Routes, Route } from "react-router-dom";
import RegisterPage from "./pages/RegisterPage";
import History from "./pages/History";
import { Link } from "react-router-dom";
import Navbar from "./components/Navbar";

function Navigation() {
  return (
    <nav style={{ padding: "20px", background: "white", display: "flex", gap: "20px", borderBottom: "1px solid #ddd" }}>
      <Link to="/" style={{ color: "#2e7d32", fontWeight: "bold" }}>Register</Link>
      <Link to="/history" style={{ color: "#2e7d32", fontWeight: "bold" }}>History</Link>
    </nav>
  );
}

function App() {
  return (
  <>
  <Navbar />
      <Routes>
      <Route path="/" element={
          <div style={{ paddingTop: "70px", minHeight: "100vh" }}>
            <RegisterPage />
          </div>
        } />
        <Route path="/" element={<RegisterPage />} />
        <Route path="/history" element={<History />} />
        <Route path="*" element={<RegisterPage />} />
      </Routes>
  </>
  );
}

export default App;