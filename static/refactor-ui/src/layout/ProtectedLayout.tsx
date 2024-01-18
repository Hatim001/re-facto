import { isEmpty } from "lodash";
import { Box, CssBaseline, CssVarsProvider } from "@mui/joy";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import Header from "./Header";
import { Sidebar } from "./Sidebar";
import { useAuth } from "../hooks/useAuth";

export const ProtectedLayout = () => {
  const { session }: any = useAuth();
  const location = useLocation();

  if (isEmpty(session)) {
    return <Navigate to="/" replace state={{ path: location.pathname }} />;
  }

  return (
    <CssVarsProvider disableTransitionOnChange>
      <CssBaseline />
      <Box sx={{ display: "flex", flex: 1, minHeight: "100%" }}>
        <Sidebar />
        <Header />
        <Box
          component="main"
          className="MainContent"
          sx={{
            pt: {
              xs: "calc(12px + var(--Header-height))",
              md: 3,
            },
            pb: {
              xs: 2,
              sm: 2,
              md: 3,
            },
            flex: 1,
            display: "flex",
            height: "100%",
            flexDirection: "column",
            minWidth: 0,
            gap: 1,
            overflow: "auto",
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </CssVarsProvider>
  );
};
