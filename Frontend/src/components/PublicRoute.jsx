import { Navigate } from "react-router-dom";

const PublicRoute = ({ children }) => {
  const user = localStorage.getItem("user");
  const token = localStorage.getItem("token");

  if (user && token) {
    return <Navigate to="/dashboard" />;
  }

  return children;
};

export default PublicRoute;
