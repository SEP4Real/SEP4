import { Navigate } from "react-router-dom";

const PublicRoute = ({ children }) => {
  const user = localStorage.getItem("user");

  // logged in → dashboard
  if (user) {
    return <Navigate to="/dashboard" />;
  }

  // not logged in → access
  return children;
};

export default PublicRoute;