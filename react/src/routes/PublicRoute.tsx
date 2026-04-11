import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import type { JSX } from "react";

interface PublicRouteProps {
  children: JSX.Element;
}

const PublicRoute = ({ children }: PublicRouteProps) => {
  const { isAuthenticated } = useAuth();

  // Si déjà connecté, redirige vers le chat
  if (isAuthenticated) {
    return <Navigate to="/chat" replace />;
  }

  return children;
};

export default PublicRoute;