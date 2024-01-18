import Box from "@mui/joy/Box";
import { useState } from "react";
import List from "@mui/joy/List";
import Sheet from "@mui/joy/Sheet";
import Avatar from "@mui/joy/Avatar";
import Divider from "@mui/joy/Divider";
import ListItem from "@mui/joy/ListItem";
import IconButton from "@mui/joy/IconButton";
import Typography from "@mui/joy/Typography";
import { useNavigate } from "react-router-dom";
import { useColorScheme } from "@mui/joy/styles";
import GlobalStyles from "@mui/joy/GlobalStyles";
import ListItemContent from "@mui/joy/ListItemContent";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import SettingsRoundedIcon from "@mui/icons-material/SettingsRounded";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import ListItemButton, { listItemButtonClasses } from "@mui/joy/ListItemButton";

import { AppState } from "../redux";
import { closeSidebar } from "./utils";
import { DELETE } from "../utils/axios";
import { useSelector } from "react-redux";
import { useAuth } from "../hooks/useAuth";
import logo from "../assets/images/logo.png";
import ColorSchemeToggle from "../components/ColorSchemeToggle";

export const Sidebar = () => {
  const { logout }: any = useAuth();
  const navigate = useNavigate();
  const { mode } = useColorScheme();
  const { user = {}, avatar_url = "" }: any = useSelector(
    (state: AppState) => state.session
  );

  const [activeTab, setActiveTab] = useState<string>(
    window.location.pathname?.split("/")?.[2]
  );

  const tabs = [
    {
      IconComponent: DashboardRoundedIcon,
      name: "Dashboard",
      key: "home",
      path: "/dashboard/home",
    },
    {
      IconComponent: SettingsRoundedIcon,
      name: "Configurations",
      key: "settings",
      path: "/dashboard/settings",
    },
  ];

  const handleLogout = () => {
    DELETE(`api/account/logout/`)?.then((res) => {
      logout(res?.data)?.finally(() => {
        navigate("/");
      });
    });
  };

  return (
    <>
      <Sheet
        className="Sidebar"
        sx={{
          position: {
            xs: "fixed",
            md: "sticky",
          },
          transform: {
            xs: "translateX(calc(100% * (var(--SideNavigation-slideIn, 0) - 1)))",
            md: "none",
          },
          transition: "transform 0.4s, width 0.4s",
          zIndex: 10000,
          height: "100dvh",
          width: "var(--Sidebar-width)",
          top: 0,
          p: 2,
          flexShrink: 0,
          display: "flex",
          flexDirection: "column",
          gap: 2,
          borderRight: "1px solid",
          borderColor: "divider",
        }}
      >
        <GlobalStyles
          styles={(theme) => ({
            ":root": {
              "--Sidebar-width": "220px",
              [theme.breakpoints.up("lg")]: {
                "--Sidebar-width": "240px",
              },
            },
          })}
        />
        <Box
          className="Sidebar-overlay"
          sx={{
            position: "fixed",
            zIndex: 9998,
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            opacity: "var(--SideNavigation-slideIn)",
            backgroundColor: "var(--joy-palette-background-backdrop)",
            transition: "opacity 0.4s",
            transform: {
              xs: "translateX(calc(100% * (var(--SideNavigation-slideIn, 0) - 1) + var(--SideNavigation-slideIn, 0) * var(--Sidebar-width, 0px)))",
              lg: "translateX(-100%)",
            },
          }}
          onClick={() => closeSidebar()}
        />
        <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
          <IconButton variant="soft" color="primary" size="sm">
            <img
              onClick={() => navigate("/")}
              style={{
                filter: mode === "dark" ? "invert(1)" : "invert(0)",
                width: "35px",
                height: "35px",
                padding: "0px",
                paddingLeft: "2px",
                margin: "0px",
              }}
              src={logo}
              alt="logo"
            />
          </IconButton>
          <Typography level="title-lg">Re-Factor</Typography>
          <ColorSchemeToggle sx={{ ml: "auto" }} />
        </Box>
        <Box
          sx={{
            minHeight: 0,
            overflow: "hidden auto",
            flexGrow: 1,
            display: "flex",
            flexDirection: "column",
            [`& .${listItemButtonClasses.root}`]: {
              gap: 1.5,
            },
          }}
        >
          <List
            size="sm"
            sx={{
              gap: 1,
              "--List-nestedInsetStart": "30px",
              "--ListItem-radius": (theme) => theme.vars.radius.sm,
            }}
          >
            {tabs?.map((ins: any, index: number) => {
              const { IconComponent, name, key, path } = ins;
              return (
                <ListItem key={`dashboard-tab-${index}`}>
                  <ListItemButton
                    selected={activeTab === key}
                    onClick={() => {
                      setActiveTab(key);
                      navigate(path);
                    }}
                  >
                    <IconComponent />
                    <ListItemContent>
                      <Typography level="title-sm">{name}</Typography>
                    </ListItemContent>
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </Box>
        <Divider />
        <Box sx={{ display: "flex", gap: 1, alignItems: "center", pl: 1 }}>
          <Avatar variant="outlined" size="sm" src={avatar_url || ""} />
          <Box sx={{ minWidth: 0, flex: 1 }}>
            <Typography level="title-sm">{user?.user_name || ""}</Typography>
            <Typography level="body-xs">{user?.email || ""}</Typography>
          </Box>
          <IconButton
            size="sm"
            variant="soft"
            color="danger"
            onClick={handleLogout}
          >
            <LogoutRoundedIcon />
          </IconButton>
        </Box>
      </Sheet>
    </>
  );
};
