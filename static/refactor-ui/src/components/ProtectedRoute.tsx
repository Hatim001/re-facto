import { isEmpty } from "lodash";
import { useAuth } from "../hooks/useAuth";
import { Navigate } from "react-router-dom";

export const ProtectedRoute = ({ children }: any) => {
  const { session }: any = useAuth();
  if (isEmpty(session)) {
    return <Navigate to="/" />;
  }
  return children;
};
