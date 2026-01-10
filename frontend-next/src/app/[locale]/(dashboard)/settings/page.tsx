"use client";

import { apiFetch } from "@/lib/api-client";
import SaveIcon from "@mui/icons-material/Save";
import LanguageIcon from "@mui/icons-material/Language";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import StorageIcon from "@mui/icons-material/Storage";
import CategoryIcon from "@mui/icons-material/Category";
import PublicIcon from "@mui/icons-material/Public";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  LinearProgress,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
  Tabs,
  Tab,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import Link from "next/link";

type SettingsResponse = Record<string, string>;

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const [tabValue, setTabValue] = useState(0);
  const [localSettings, setLocalSettings] = useState<Record<string, string>>({
    default_language: "en",
    date_format: "YYYY-MM-DD",
    time_format: "24h",
    number_format: "1,234.56",
    timezone: "UTC",
    currency: "USD",
  });

  const { data: settings, isLoading, error } = useQuery<SettingsResponse>({
    queryKey: ["settings"],
    queryFn: async () => {
      try {
        const data = await apiFetch<SettingsResponse>("/api/settings");
        return data || {};
      } catch (err) {
        return {};
      }
    },
  });

  const mutation = useMutation({
    mutationFn: async ({ key, value }: { key: string; value: string }) => {
      await apiFetch(`/api/settings/${key}`, {
        method: "POST",
        body: JSON.stringify({ value }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["settings"] });
    },
  });

  const handleSave = (key: string) => {
    mutation.mutate({ key, value: localSettings[key] });
  };

  const handleSaveAll = () => {
    Object.entries(localSettings).forEach(([key, value]) => {
      mutation.mutate({ key, value });
    });
  };

  const updateSetting = (key: string, value: string) => {
    setLocalSettings((prev) => ({ ...prev, [key]: value }));
  };

  if (isLoading) return <LinearProgress />;

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" fontWeight={700}>
          System Settings
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Configure system preferences, localization, and management settings
        </Typography>
      </Box>

      {error && (
        <Alert severity="warning">
          Unable to load some settings. Using default values.
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="General" icon={<PublicIcon />} iconPosition="start" />
          <Tab label="Localization" icon={<LanguageIcon />} iconPosition="start" />
          <Tab label="Database" icon={<StorageIcon />} iconPosition="start" />
          <Tab label="Groups" icon={<CategoryIcon />} iconPosition="start" />
        </Tabs>
      </Box>

      {/* General Settings */}
      <TabPanel value={tabValue} index={0}>
        <Card>
          <CardContent>
            <Stack spacing={3}>
              <Typography variant="h6">General Settings</Typography>
              <Divider />
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="System Name"
                    value={localSettings.system_name || "Server Monitor"}
                    onChange={(e) => updateSetting("system_name", e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Admin Email"
                    type="email"
                    value={localSettings.admin_email || ""}
                    onChange={(e) => updateSetting("admin_email", e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Timezone</InputLabel>
                    <Select
                      value={localSettings.timezone || "UTC"}
                      label="Timezone"
                      onChange={(e) => updateSetting("timezone", e.target.value)}
                    >
                      <MenuItem value="UTC">UTC</MenuItem>
                      <MenuItem value="America/New_York">America/New York (EST)</MenuItem>
                      <MenuItem value="America/Los_Angeles">America/Los Angeles (PST)</MenuItem>
                      <MenuItem value="Europe/London">Europe/London (GMT)</MenuItem>
                      <MenuItem value="Europe/Paris">Europe/Paris (CET)</MenuItem>
                      <MenuItem value="Asia/Tokyo">Asia/Tokyo (JST)</MenuItem>
                      <MenuItem value="Asia/Ho_Chi_Minh">Asia/Ho Chi Minh (ICT)</MenuItem>
                      <MenuItem value="Asia/Shanghai">Asia/Shanghai (CST)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Session Timeout (minutes)"
                    type="number"
                    value={localSettings.session_timeout || "480"}
                    onChange={(e) => updateSetting("session_timeout", e.target.value)}
                  />
                </Grid>
              </Grid>
              
              <Box display="flex" justifyContent="flex-end">
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveAll}
                  disabled={mutation.isPending}
                >
                  Save General Settings
                </Button>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Localization Settings */}
      <TabPanel value={tabValue} index={1}>
        <Card>
          <CardContent>
            <Stack spacing={3}>
              <Typography variant="h6">Localization Settings</Typography>
              <Divider />
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Default Language</InputLabel>
                    <Select
                      value={localSettings.default_language || "en"}
                      label="Default Language"
                      onChange={(e) => updateSetting("default_language", e.target.value)}
                    >
                      <MenuItem value="en">English</MenuItem>
                      <MenuItem value="vi">Tiếng Việt</MenuItem>
                      <MenuItem value="fr">Français</MenuItem>
                      <MenuItem value="es">Español</MenuItem>
                      <MenuItem value="de">Deutsch</MenuItem>
                      <MenuItem value="ja">日本語</MenuItem>
                      <MenuItem value="ko">한국어</MenuItem>
                      <MenuItem value="zh-CN">简体中文</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Date Format</InputLabel>
                    <Select
                      value={localSettings.date_format || "YYYY-MM-DD"}
                      label="Date Format"
                      onChange={(e) => updateSetting("date_format", e.target.value)}
                    >
                      <MenuItem value="YYYY-MM-DD">YYYY-MM-DD (2026-01-10)</MenuItem>
                      <MenuItem value="DD/MM/YYYY">DD/MM/YYYY (10/01/2026)</MenuItem>
                      <MenuItem value="MM/DD/YYYY">MM/DD/YYYY (01/10/2026)</MenuItem>
                      <MenuItem value="DD-MM-YYYY">DD-MM-YYYY (10-01-2026)</MenuItem>
                      <MenuItem value="YYYY年MM月DD日">YYYY年MM月DD日 (2026年01月10日)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Time Format</InputLabel>
                    <Select
                      value={localSettings.time_format || "24h"}
                      label="Time Format"
                      onChange={(e) => updateSetting("time_format", e.target.value)}
                    >
                      <MenuItem value="24h">24-hour (23:59)</MenuItem>
                      <MenuItem value="12h">12-hour (11:59 PM)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Number Format</InputLabel>
                    <Select
                      value={localSettings.number_format || "1,234.56"}
                      label="Number Format"
                      onChange={(e) => updateSetting("number_format", e.target.value)}
                    >
                      <MenuItem value="1,234.56">1,234.56 (Comma thousand, dot decimal)</MenuItem>
                      <MenuItem value="1.234,56">1.234,56 (Dot thousand, comma decimal)</MenuItem>
                      <MenuItem value="1 234,56">1 234,56 (Space thousand, comma decimal)</MenuItem>
                      <MenuItem value="1234.56">1234.56 (No separator)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Currency</InputLabel>
                    <Select
                      value={localSettings.currency || "USD"}
                      label="Currency"
                      onChange={(e) => updateSetting("currency", e.target.value)}
                    >
                      <MenuItem value="USD">USD ($)</MenuItem>
                      <MenuItem value="EUR">EUR (€)</MenuItem>
                      <MenuItem value="GBP">GBP (£)</MenuItem>
                      <MenuItem value="VND">VND (₫)</MenuItem>
                      <MenuItem value="JPY">JPY (¥)</MenuItem>
                      <MenuItem value="CNY">CNY (¥)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>First Day of Week</InputLabel>
                    <Select
                      value={localSettings.first_day_of_week || "monday"}
                      label="First Day of Week"
                      onChange={(e) => updateSetting("first_day_of_week", e.target.value)}
                    >
                      <MenuItem value="sunday">Sunday</MenuItem>
                      <MenuItem value="monday">Monday</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
              
              <Box display="flex" justifyContent="flex-end">
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveAll}
                  disabled={mutation.isPending}
                >
                  Save Localization Settings
                </Button>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Database Management */}
      <TabPanel value={tabValue} index={2}>
        <Card>
          <CardContent>
            <Stack spacing={3}>
              <Box>
                <Typography variant="h6">Database Management</Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage database backups, restore, and health monitoring
                </Typography>
              </Box>
              <Divider />
              
              <Alert severity="info">
                Database management features are available in a dedicated page.
              </Alert>
              
              <Box>
                <Button
                  variant="contained"
                  component={Link}
                  href="/settings/database"
                  startIcon={<StorageIcon />}
                >
                  Go to Database Management
                </Button>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Groups Management */}
      <TabPanel value={tabValue} index={3}>
        <Card>
          <CardContent>
            <Stack spacing={3}>
              <Box>
                <Typography variant="h6">Groups Management</Typography>
                <Typography variant="body2" color="text.secondary">
                  Organize servers, notes, snippets, and inventory items into groups
                </Typography>
              </Box>
              <Divider />
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Stack spacing={2}>
                        <CategoryIcon color="primary" sx={{ fontSize: 40 }} />
                        <Typography variant="h6">Server Groups</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Organize servers by environment, location, or function
                        </Typography>
                        <Button
                          variant="outlined"
                          component={Link}
                          href="/settings/groups?type=servers"
                          fullWidth
                        >
                          Manage
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Stack spacing={2}>
                        <CategoryIcon color="success" sx={{ fontSize: 40 }} />
                        <Typography variant="h6">Note Groups</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Categorize server notes by topic or priority
                        </Typography>
                        <Button
                          variant="outlined"
                          component={Link}
                          href="/settings/groups?type=notes"
                          fullWidth
                        >
                          Manage
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Stack spacing={2}>
                        <CategoryIcon color="warning" sx={{ fontSize: 40 }} />
                        <Typography variant="h6">Command Snippets</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Group terminal commands by category or use case
                        </Typography>
                        <Button
                          variant="outlined"
                          component={Link}
                          href="/settings/groups?type=snippets"
                          fullWidth
                        >
                          Manage
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Stack spacing={2}>
                        <CategoryIcon color="info" sx={{ fontSize: 40 }} />
                        <Typography variant="h6">Inventory Groups</Typography>
                        <Typography variant="body2" color="text.secondary">
                          Classify inventory items by type or category
                        </Typography>
                        <Button
                          variant="outlined"
                          component={Link}
                          href="/settings/groups?type=inventory"
                          fullWidth
                        >
                          Manage
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Stack>
          </CardContent>
        </Card>
      </TabPanel>

      {mutation.isSuccess && (
        <Alert severity="success">Settings saved successfully!</Alert>
      )}
      {mutation.isError && (
        <Alert severity="error">Failed to save settings. Please try again.</Alert>
      )}
    </Stack>
  );
}

