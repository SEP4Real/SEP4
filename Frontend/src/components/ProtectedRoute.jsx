import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
  const user = localStorage.getItem("user");

  // not logged in → redirect
  if (!user) {
    return <Navigate to="/login" />;
  }

  // logged in → allow access
  return children;
};

export default ProtectedRoute;