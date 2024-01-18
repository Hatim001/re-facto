import {
  Autocomplete,
  Box,
  Breadcrumbs,
  FormHelperText,
  Typography,
  Card,
  Stack,
  Grid,
  Alert,
} from "@mui/joy";
import { indexOf } from "lodash";
import Input from "@mui/joy/Input";
import Button from "@mui/joy/Button";
import Divider from "@mui/joy/Divider";
import FormLabel from "@mui/joy/FormLabel";
import { HashLoader } from "react-spinners";
import CardActions from "@mui/joy/CardActions";
import FormControl from "@mui/joy/FormControl";
import CardOverflow from "@mui/joy/CardOverflow";
import RadarIcon from "@mui/icons-material/Radar";
import React, { useEffect, useState } from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import HomeRoundedIcon from "@mui/icons-material/HomeRounded";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import KeyboardArrowRightIcon from "@mui/icons-material/KeyboardArrowRight";
import ChevronRightRoundedIcon from "@mui/icons-material/ChevronRightRounded";
import KeyboardDoubleArrowRightIcon from "@mui/icons-material/KeyboardDoubleArrowRight";

import { POST, GET } from "../../utils/axios";

type Props = {};

let configs = [
  {
    interval: "null",
    maxLines: "null",
    repo: "null",
    config_trackedBranch: ["null"],
    targetBranch: "",
  },
];

const Settings = (props: Props) => {
  const inputRef = React.useRef<HTMLInputElement | null>(null);
  let [trgBranchValue, setTrgBranchValue] = React.useState<string>();
  let [trkedBranchValue, setTrkedBranchValue] = React.useState<any>([]);
  const [selectedRepo, setSelectedRepo] = React.useState<string | null>(null);
  const [repoData, setRepoData] = React.useState<any>([]);
  let [targetBranch, setTargetBranch] = React.useState<any>([]);
  let [trackedBranch, setTrackedBranch] = React.useState<any>([]);
  let [loading, setLoading] = useState(true);
  let [repoSelected, setRepoSelected] = useState(false);
  let [commit_interval, setCommitInterval] = useState("null");
  let [minLines, setMinLines] = useState("null");
  let [alertOpen, setAlertOpen] = useState(false);
  let [errorAlert, setErrorAlert] = useState(false);

  const fetchAPI = async () => {
    const apiResponse = await GET("api/account/github/configurations/");

    configs[0].interval = apiResponse.data.commit_interval;
    configs[0].maxLines = apiResponse.data.max_lines;
    setCommitInterval(apiResponse.data.commit_interval);
    setMinLines(apiResponse.data.max_lines);
    setLoading(false);
    await setRepoData(
      apiResponse.data.repositories.map((repo: any) => ({
        reponame: repo.name,
        id: repo.repo_id,
        targetBranches: repo.target_branches,
        trackedBranches: repo.source_branches,
      }))
    );
  };

  const targetBranchOnchange = (newValue: any) => {
    setTrgBranchValue(newValue);
    configs[0].targetBranch = newValue as string;
  };

  const trackedBranchOnchange = (newValue: any) => {
    setTrkedBranchValue(newValue);
    configs[0].config_trackedBranch = newValue as string[];
  };

  const repoOnchange = (newValue: any) => {
    setSelectedRepo(newValue);
    configs[0].repo = newValue as string;
    let defaultTargetBranch = "";
    let defaultTrackedBranch = ["null"];

    if (indexOf(repoOptions, newValue) !== -1) {
      defaultTrackedBranch = [];
      setRepoSelected(true);
      setTargetBranch(repoData[indexOf(repoOptions, newValue)].targetBranches);
      setTrackedBranch(
        repoData[indexOf(repoOptions, newValue)].trackedBranches
      );
      repoData[indexOf(repoOptions, newValue)].targetBranches.map(
        (branch: any) => {
          if (branch.is_selected) {
            defaultTargetBranch = branch.name;
          }
        }
      );
      repoData[indexOf(repoOptions, newValue)].trackedBranches.map(
        (branch: any) => {
          if (branch.is_selected) {
            defaultTrackedBranch.push(branch.name);
          }
        }
      );
    } else {
      setRepoSelected(false);
      setTrackedBranch([]);
      setTargetBranch([]);
    }
    configs[0].targetBranch = defaultTargetBranch;
    configs[0].config_trackedBranch = defaultTrackedBranch;
    setTrkedBranchValue(defaultTrackedBranch);
    setTrgBranchValue(defaultTargetBranch);
  };

  const postAPI = async () => {
    setLoading(true);
    const apiPostResponse = await GET("api/account/github/configurations/");
    let tempResponse = apiPostResponse.data;
    let repoJson = tempResponse.repositories;
    tempResponse.commit_interval = Number(commit_interval);
    tempResponse.max_lines = Number(minLines);
    repoJson.map((repo: any) => {
      if (repo.name === configs[0].repo) {
        repo.target_branches.map((branch: any) => {
          if (branch.name === configs[0].targetBranch) {
            branch.is_selected = true;
          } else {
            branch.is_selected = false;
          }
        });
      }
    });
    repoJson.map((repo: any) => {
      if (repo.name === configs[0].repo) {
        repo.source_branches.map((branch: any) => {
          if (configs[0].config_trackedBranch.includes(branch.name)) {
            branch.is_selected = true;
          } else {
            branch.is_selected = false;
          }
        });
      }
    });

    tempResponse.repositories = repoJson;
    let postResponse = await POST(
      "api/account/github/configurations/",
      tempResponse
    ).catch(function (error) {
      setLoading(false);
      setErrorAlert(true);
      console.error("Error:", error);
      return;
    });
    setLoading(false);
    setAlertOpen(true);
  };

  useEffect(() => {
    fetchAPI();
  }, []);

  let repoOptions: any =
    repoData.length > 0 ? repoData?.map((option: any) => option.reponame) : [];
  return (
    <React.Fragment>
      <Box
        sx={{
          flex: 1,
          width: "100%",
          alignContent: "center",
        }}
      >
        <Box
          sx={{
            position: "sticky",
            top: {
              sm: -100,
              md: -110,
            },
            bgcolor: "background.body",
            zIndex: 9995,
          }}
        >
          <Box
            sx={{
              px: {
                xs: 2,
                md: 6,
              },
            }}
          >
            <Breadcrumbs
              size="sm"
              aria-label="breadcrumbs"
              separator={<ChevronRightRoundedIcon fontSize="small" />}
              sx={{ pl: 0 }}
            >
              <HomeRoundedIcon />
              <Typography color="neutral" fontSize={12} fontWeight={500}>
                Configurations
              </Typography>
            </Breadcrumbs>
          </Box>
        </Box>
        <Box
          sx={{
            display: "contents",
            flexDirection: "column",
            alignItems: "center",
            height: 1,
            position: "absolute",
            width: 1,
          }}
        >
          <HashLoader loading={loading} color="#0D6EFD" />
        </Box>
        <Stack
          visibility={loading ? "hidden" : "visible"}
          spacing={4}
          sx={{
            display: "flex",
            maxWidth: "800px",
            mx: "auto",
            px: {
              xs: 2,
              md: 6,
            },
            py: {
              xs: 2,
              md: 3,
            },
          }}
        >
          <Card>
            <Box sx={{ mb: 1 }}>
              <Typography
                level="h2"
                sx={{
                  mt: 1,
                  mb: 1,
                }}
              >
                Configurations
              </Typography>
              <Typography level="body-sm">
                Configure the behaviour of the bot.
              </Typography>
            </Box>
            <Divider />
            {/*---------- Desktop UI Render ----------*/}
            <Stack
              direction="row"
              spacing={3}
              sx={{ display: { xs: "none", md: "flex" }, my: 1 }}
            >
              <Stack spacing={2} sx={{ flexGrow: 1 }}>
                <Stack spacing={1} direction="row">
                  <Stack direction="column" flex="1">
                    <FormLabel>Commit Interval</FormLabel>
                    <Input
                      size="md"
                      type="number"
                      value={commit_interval}
                      onChange={(e) => {
                        setCommitInterval(e.target.value);
                      }}
                      slotProps={{
                        input: {
                          ref: inputRef,
                          min: 1,
                          step: 1,
                        },
                      }}
                    />
                    <FormHelperText>
                      No. of commits after which bot should trigger.
                    </FormHelperText>
                  </Stack>
                  <Stack direction="column" flex="1">
                    <FormLabel>Minimum Lines</FormLabel>
                    <Input
                      type="number"
                      size="md"
                      value={minLines}
                      onChange={(e) => {
                        setMinLines(e.target.value);
                      }}
                      slotProps={{
                        input: {
                          ref: inputRef,
                          min: 1,
                          step: 1,
                        },
                      }}
                    />
                    <FormHelperText>
                      Minimum Changed Lines to trigger the Bot.
                    </FormHelperText>
                  </Stack>
                </Stack>
                <Stack direction="column" flex="1" spacing={1}>
                  <FormLabel>Select Repository</FormLabel>
                  <Autocomplete
                    id="repoAutocomplete"
                    size="md"
                    placeholder="Select Repo"
                    openOnFocus={true}
                    options={repoOptions}
                    value={selectedRepo}
                    onChange={(event, newValue) => {
                      repoOnchange(newValue);
                    }}
                    startDecorator={<KeyboardDoubleArrowRightIcon />}
                  />
                </Stack>
                <Stack direction="row" spacing={2}>
                  <FormControl sx={{ flexGrow: 1 }}>
                    <FormLabel>Select Branch to Track</FormLabel>
                    <Autocomplete
                      id="trkedBranchAutocomplete"
                      multiple
                      size="md"
                      placeholder="Select the branches to track for refactoring."
                      openOnFocus={true}
                      options={trackedBranch.map((e: any) => e.name)}
                      value={repoSelected ? trkedBranchValue : []}
                      onChange={(event, newValue) => {
                        trackedBranchOnchange(newValue);
                      }}
                      startDecorator={<RadarIcon />}
                    />
                  </FormControl>
                </Stack>
                <Stack direction="row" spacing={2}>
                  <FormControl sx={{ flexGrow: 1 }}>
                    <FormLabel>Select your Target Branch</FormLabel>
                    <Autocomplete
                      id="trgBranchAutocomplete"
                      size="md"
                      placeholder="Select Target Branch to merge to."
                      openOnFocus={true}
                      options={targetBranch.map((e: any) => e.name)}
                      value={repoSelected ? trgBranchValue : ""}
                      onChange={(event, newValue) => {
                        targetBranchOnchange(newValue);
                      }}
                      startDecorator={<KeyboardArrowRightIcon />}
                    />
                  </FormControl>
                </Stack>
              </Stack>
            </Stack>
            {/*---------- Responsive UI Render ----------*/}
            <Stack
              direction="column"
              spacing={2}
              sx={{ display: { xs: "flex", md: "none" }, my: 1 }}
            >
              <Stack spacing={2} sx={{ flexGrow: 1 }}>
                <Stack spacing={1} direction="row">
                  <Stack direction="column" flex="1">
                    <FormLabel>Commit Interval</FormLabel>
                    <Input
                      size="md"
                      type="number"
                      value={commit_interval}
                      onChange={(e) => {
                        setCommitInterval(e.target.value);
                      }}
                      slotProps={{
                        input: {
                          ref: inputRef,
                          min: 1,
                          step: 1,
                        },
                      }}
                    />
                    <FormHelperText>
                      No. of commits after which bot should trigger.
                    </FormHelperText>
                  </Stack>
                  <Stack direction="column" flex="1">
                    <FormLabel>Minimum Lines</FormLabel>
                    <Input
                      type="number"
                      size="md"
                      value={minLines}
                      onChange={(e) => {
                        setMinLines(e.target.value);
                      }}
                      slotProps={{
                        input: {
                          ref: inputRef,
                          min: 1,
                          step: 1,
                        },
                      }}
                    />
                    <FormHelperText>
                      Minimum Changed Lines to trigger the Bot.
                    </FormHelperText>
                  </Stack>
                </Stack>
                <Stack direction="column" flex="1" spacing={1}>
                  <FormLabel>Select Repository</FormLabel>
                  <Autocomplete
                    id="repoAutocomplete"
                    size="md"
                    placeholder="Select Repo"
                    openOnFocus={true}
                    options={repoOptions}
                    value={selectedRepo}
                    onChange={(event, newValue) => {
                      repoOnchange(newValue);
                    }}
                    startDecorator={<KeyboardDoubleArrowRightIcon />}
                  />
                </Stack>
                <Stack direction="row" spacing={2}>
                  <FormControl sx={{ flexGrow: 1 }}>
                    <FormLabel>Select Branch to Track</FormLabel>
                    <Autocomplete
                      id="trkedBranchAutocomplete"
                      multiple
                      size="md"
                      placeholder="Select the branches to track for refactoring."
                      openOnFocus={true}
                      options={trackedBranch.map((e: any) => e.name)}
                      value={repoSelected ? trkedBranchValue : []}
                      onChange={(event, newValue) => {
                        trackedBranchOnchange(newValue);
                      }}
                      startDecorator={<RadarIcon />}
                    />
                  </FormControl>
                </Stack>
                <Stack direction="row" spacing={2}>
                  <FormControl sx={{ flexGrow: 1 }}>
                    <FormLabel>Select your Target Branch</FormLabel>
                    <Autocomplete
                      id="trgBranchAutocomplete"
                      size="md"
                      placeholder="Select Target Branch to merge to."
                      openOnFocus={true}
                      options={targetBranch.map((e: any) => e.name)}
                      value={repoSelected ? trgBranchValue : ""}
                      onChange={(event, newValue) => {
                        targetBranchOnchange(newValue);
                      }}
                      startDecorator={<KeyboardArrowRightIcon />}
                    />
                  </FormControl>
                </Stack>
              </Stack>
            </Stack>

            {/*---------- Common UI Render ----------*/}

            <CardOverflow
              sx={{ borderTop: "1px solid", borderColor: "divider" }}
            >
              <CardActions sx={{ alignSelf: "flex-end", pt: 2 }}>
                <Button
                  size="sm"
                  variant="outlined"
                  color="neutral"
                  onClick={() => {
                    setRepoSelected(false);
                    setSelectedRepo(null);
                    setTrgBranchValue("");
                    setTrkedBranchValue([]);
                    configs[0].repo = "null";
                    configs[0].config_trackedBranch = ["null"];
                    configs[0].targetBranch = "";
                  }}
                >
                  Discard
                </Button>
                <Button
                  size="sm"
                  variant="solid"
                  onClick={() => {
                    if (
                      configs[0].repo === "null" ||
                      configs[0].config_trackedBranch[0] === undefined ||
                      configs[0].targetBranch === null ||
                      configs[0].targetBranch === "null"
                    ) {
                      setErrorAlert(true);
                      return;
                    }
                    postAPI();
                  }}
                >
                  Save
                </Button>
              </CardActions>
            </CardOverflow>
            <Grid xs={6} md={8}></Grid>
          </Card>
          <Alert
            variant="soft"
            color="success"
            startDecorator={<CheckCircleIcon />}
            endDecorator={
              <Button
                size="sm"
                variant="solid"
                color="success"
                onClick={() => {
                  setAlertOpen(false);
                }}
              >
                Close
              </Button>
            }
            sx={{
              visibility: alertOpen ? "visible" : "hidden",
              position: "fixed",
              alignSelf: "center",
              bottom: 20,
              m: 3,
              zIndex: 9999,
              width: "auto",
            }}
          >
            Your Configurations are saved successfully.
          </Alert>
          <Alert
            variant="soft"
            color="danger"
            startDecorator={<CancelIcon />}
            endDecorator={
              <Button
                size="sm"
                variant="solid"
                color="danger"
                onClick={() => {
                  setErrorAlert(false);
                }}
              >
                Close
              </Button>
            }
            sx={{
              visibility: errorAlert ? "visible" : "hidden",
              position: "fixed",
              alignSelf: "center",
              bottom: 20,
              m: 3,
              zIndex: 9999,
              width: "auto",
            }}
          >
            Something went wrong, Configurations weren't saved.
          </Alert>
        </Stack>
      </Box>
    </React.Fragment>
  );
};

export default Settings;
