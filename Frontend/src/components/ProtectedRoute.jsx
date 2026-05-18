import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const user = localStorage.getItem("user");
  const token = localStorage.getItem("token");

  // not logged in → redirect
  if (!user) {
    return <Navigate to="/login" />;
  }

  // logged in → allow access
  return children;
};

export default ProtectedRoute;