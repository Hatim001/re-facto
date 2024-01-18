import Box from "@mui/joy/Box";
import { Typography } from "@mui/joy";
import CssBaseline from "@mui/joy/CssBaseline";
import Breadcrumbs from "@mui/joy/Breadcrumbs";
import { CssVarsProvider } from "@mui/joy/styles";
import HomeRoundedIcon from "@mui/icons-material/HomeRounded";
import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";

import BranchTable from "../../layout/BranchTable";

export const Dashboard = () => {
  return (
    <CssVarsProvider disableTransitionOnChange>
      <CssBaseline />
      <Box
        sx={{
          padding: 0,
          display: "flex",
          minHeight: "100%",
        }}
      >
        <Box
          component="main"
          className="MainContent"
          title="Root Content"
          sx={{
            px: {
              xs: 2,
              md: 6,
            },
            pt: 0,
            pb: 0,
            flex: 1,
            display: "flex",
            flexDirection: "column",
            minWidth: 0,
            height: "100%",
            gap: 1,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <Breadcrumbs
              size="sm"
              aria-label="breadcrumbs"
              separator={<ChevronRightRoundedIcon fontSize="small" />}
              sx={{ pl: 0 }}
            >
              <HomeRoundedIcon />
              <Typography color="neutral" fontSize={12} fontWeight={500}>
                Dashboard
              </Typography>
            </Breadcrumbs>
          </Box>
          <BranchTable />
        </Box>
      </Box>
    </CssVarsProvider>
  );
};
