import { isEmpty } from "lodash";
import { Navigate, Outlet } from "react-router-dom";
import { Box, CssBaseline, CssVarsProvider } from "@mui/joy";

import { NavBar } from "./HomeNavBar";
import { useAuth } from "../hooks/useAuth";

export const HomeLayout = () => {
  const { session }: any = useAuth();

  if (!isEmpty(session)) {
    return <Navigate to="/dashboard/home" />;
  }

  return (
    <CssVarsProvider disableTransitionOnChange>
      <CssBaseline />
      <Box
        display={"flex"}
        flexDirection={"column"}
        flex={1}
        position={"absolute"}
        width={"100%"}
        height={"100%"}
      >
        <NavBar />
        <Outlet />
      </Box>
    </CssVarsProvider>
  );
};
