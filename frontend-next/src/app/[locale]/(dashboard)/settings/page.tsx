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
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          sx={{
            "& .MuiTab-root": {
              textTransform: "none",
              fontWeight: 600,
              fontSize: "0.95rem",
            },
          }}
        >
          <Tab label="General" icon={<PublicIcon />} iconPosition="start" />
          <Tab label="Localization" icon={<LanguageIcon />} iconPosition="start" />
          <Tab label="Database" icon={<StorageIcon />} iconPosition="start" />
          <Tab label="Groups" icon={<CategoryIcon />} iconPosition="start" />
        </Tabs>
      </Box>

      {/* General Settings */}
      <TabPanel value={tabValue} index={0}>
        <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
          <CardContent>
            <Stack spacing={3}>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  General Settings
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Configure basic system preferences and behavior
                </Typography>
              </Box>
              <Divider />
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="System Name"
                    value={localSettings.system_name || "Server Monitor"}
                    onChange={(e) => updateSetting("system_name", e.target.value)}
                    helperText="Display name for your monitoring system"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Admin Email"
                    type="email"
                    value={localSettings.admin_email || ""}
                    onChange={(e) => updateSetting("admin_email", e.target.value)}
                    helperText="Primary contact email for system notifications"
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
                    helperText="Auto-logout after inactivity (default: 8 hours)"
                  />
                </Grid>
              </Grid>
              
              <Divider />
              
              <Box display="flex" justifyContent="flex-end">
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveAll}
                  disabled={mutation.isPending}
                  size="large"
                >
                  {mutation.isPending ? "Saving..." : "Save General Settings"}
                </Button>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Localization Settings */}
      <TabPanel value={tabValue} index={1}>
        <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
          <CardContent>
            <Stack spacing={3}>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  Localization Settings
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Configure language, date/time formats, and regional preferences
                </Typography>
              </Box>
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
                      <MenuItem value="en">🇬🇧 English</MenuItem>
                      <MenuItem value="vi">🇻🇳 Tiếng Việt</MenuItem>
                      <MenuItem value="fr">🇫🇷 Français</MenuItem>
                      <MenuItem value="es">🇪🇸 Español</MenuItem>
                      <MenuItem value="de">🇩🇪 Deutsch</MenuItem>
                      <MenuItem value="ja">🇯🇵 日本語</MenuItem>
                      <MenuItem value="ko">🇰🇷 한국어</MenuItem>
                      <MenuItem value="zh-CN">🇨🇳 简体中文</MenuItem>
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
                      <MenuItem value="1,234.56">1,234.56 (Comma, dot decimal)</MenuItem>
                      <MenuItem value="1.234,56">1.234,56 (Dot, comma decimal)</MenuItem>
                      <MenuItem value="1 234,56">1 234,56 (Space, comma decimal)</MenuItem>
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
                      <MenuItem value="USD">USD - $ (US Dollar)</MenuItem>
                      <MenuItem value="EUR">EUR - € (Euro)</MenuItem>
                      <MenuItem value="GBP">GBP - £ (British Pound)</MenuItem>
                      <MenuItem value="VND">VND - ₫ (Vietnamese Dong)</MenuItem>
                      <MenuItem value="JPY">JPY - ¥ (Japanese Yen)</MenuItem>
                      <MenuItem value="CNY">CNY - ¥ (Chinese Yuan)</MenuItem>
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
              
              <Divider />
              
              <Box display="flex" justifyContent="flex-end">
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveAll}
                  disabled={mutation.isPending}
                  size="large"
                >
                  {mutation.isPending ? "Saving..." : "Save Localization Settings"}
                </Button>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Database Management */}
      <TabPanel value={tabValue} index={2}>
        <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
          <CardContent>
            <Stack spacing={3}>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  Database Management
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Manage database backups, restore, and health monitoring
                </Typography>
              </Box>
              <Divider />
              
              <Box
                sx={{
                  p: 4,
                  textAlign: "center",
                  bgcolor: "action.hover",
                  borderRadius: 2,
                }}
              >
                <StorageIcon sx={{ fontSize: 64, color: "primary.main", mb: 2 }} />
                <Typography variant="body1" gutterBottom>
                  Database management features are available on a dedicated page
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={3}>
                  Backup, restore, and monitor your database health
                </Typography>
                <Button
                  variant="contained"
                  component={Link}
                  href="/settings/database"
                  startIcon={<StorageIcon />}
                  size="large"
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
        <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
          <CardContent>
            <Stack spacing={3}>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  Groups Management
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Organize servers, notes, snippets, and inventory items into groups
                </Typography>
              </Box>
              <Divider />
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={3}>
                  <Card
                    variant="outlined"
                    sx={{
                      height: "100%",
                      transition: "all 0.3s",
                      "&:hover": {
                        boxShadow: 4,
                        transform: "translateY(-4px)",
                        borderColor: "primary.main",
                      },
                    }}
                  >
                    <CardContent>
                      <Stack spacing={2} alignItems="center">
                        <Box
                          sx={{
                            width: 64,
                            height: 64,
                            borderRadius: "50%",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
                          }}
                        >
                          <CategoryIcon sx={{ fontSize: 32, color: "white" }} />
                        </Box>
                        <Typography variant="h6" fontWeight={600}>
                          Server Groups
                        </Typography>
                        <Typography variant="body2" color="text.secondary" textAlign="center">
                          Organize servers by environment, location, or function
                        </Typography>
                        <Button
                          variant="contained"
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
                  <Card
                    variant="outlined"
                    sx={{
                      height: "100%",
                      transition: "all 0.3s",
                      "&:hover": {
                        boxShadow: 4,
                        transform: "translateY(-4px)",
                        borderColor: "success.main",
                      },
                    }}
                  >
                    <CardContent>
                      <Stack spacing={2} alignItems="center">
                        <Box
                          sx={{
                            width: 64,
                            height: 64,
                            borderRadius: "50%",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                          }}
                        >
                          <CategoryIcon sx={{ fontSize: 32, color: "white" }} />
                        </Box>
                        <Typography variant="h6" fontWeight={600}>
                          Note Groups
                        </Typography>
                        <Typography variant="body2" color="text.secondary" textAlign="center">
                          Categorize server notes by topic or priority
                        </Typography>
                        <Button
                          variant="contained"
                          component={Link}
                          href="/settings/groups?type=notes"
                          fullWidth
                          color="success"
                        >
                          Manage
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Card
                    variant="outlined"
                    sx={{
                      height: "100%",
                      transition: "all 0.3s",
                      "&:hover": {
                        boxShadow: 4,
                        transform: "translateY(-4px)",
                        borderColor: "warning.main",
                      },
                    }}
                  >
                    <CardContent>
                      <Stack spacing={2} alignItems="center">
                        <Box
                          sx={{
                            width: 64,
                            height: 64,
                            borderRadius: "50%",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
                          }}
                        >
                          <CategoryIcon sx={{ fontSize: 32, color: "white" }} />
                        </Box>
                        <Typography variant="h6" fontWeight={600}>
                          Command Snippets
                        </Typography>
                        <Typography variant="body2" color="text.secondary" textAlign="center">
                          Group terminal commands by category or use case
                        </Typography>
                        <Button
                          variant="contained"
                          component={Link}
                          href="/settings/groups?type=snippets"
                          fullWidth
                          color="warning"
                        >
                          Manage
                        </Button>
                      </Stack>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Card
                    variant="outlined"
                    sx={{
                      height: "100%",
                      transition: "all 0.3s",
                      "&:hover": {
                        boxShadow: 4,
                        transform: "translateY(-4px)",
                        borderColor: "info.main",
                      },
                    }}
                  >
                    <CardContent>
                      <Stack spacing={2} alignItems="center">
                        <Box
                          sx={{
                            width: 64,
                            height: 64,
                            borderRadius: "50%",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            background: "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)",
                          }}
                        >
                          <CategoryIcon sx={{ fontSize: 32, color: "white" }} />
                        </Box>
                        <Typography variant="h6" fontWeight={600}>
                          Inventory Groups
                        </Typography>
                        <Typography variant="body2" color="text.secondary" textAlign="center">
                          Classify inventory items by type or category
                        </Typography>
                        <Button
                          variant="contained"
                          component={Link}
                          href="/settings/groups?type=inventory"
                          fullWidth
                          color="info"
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
        <Alert severity="success" sx={{ borderRadius: 2 }}>
          Settings saved successfully!
        </Alert>
      )}
      {mutation.isError && (
        <Alert severity="error" sx={{ borderRadius: 2 }}>
          Failed to save settings. Please try again.
        </Alert>
      )}
    </Stack>
  );
}

