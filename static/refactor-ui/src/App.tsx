import { Fragment, useEffect } from "react";
import { Box, CssBaseline } from "@mui/joy";
import { Route, Routes } from "react-router-dom";

import { HomePage } from "./components/Home";
import Settings from "./components/Settings";
import { About } from "./components/AboutUs";
import { HomeLayout } from "./layout/HomeLayout";
import { Dashboard } from "./components/Dashboard";
import { Documentation } from "./components/Documentation";
import { ProtectedLayout } from "./layout/ProtectedLayout";
import { prepareSessionData } from "./redux/actions/SessionActions";

const App = () => {
  useEffect(() => {
    fetchSession();
  }, []);

  const fetchSession = async () => {
    await prepareSessionData();
  };

  return (
    <Fragment>
      <CssBaseline />
      <Box sx={{ display: "flex", minHeight: "100dvh" }}>
        <Routes>
          <Route path="/" element={<HomeLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/about" element={<About />} />
            <Route path="/documentation" element={<Documentation />} />
          </Route>
          <Route path="/dashboard" element={<ProtectedLayout />}>
            <Route path="/dashboard/" element={<Dashboard />} />
            <Route path="/dashboard/home" element={<Dashboard />} />
            <Route path="/dashboard/refactorings" element={<Dashboard />} />
            <Route path="/dashboard/settings" element={<Settings />} />
          </Route>
        </Routes>
      </Box>
    </Fragment>
  );
};

export default App;
