"use client";

import {
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  Stack,
  TextField,
  Typography,
  Alert,
  IconButton,
  InputAdornment,
} from "@mui/material";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api-client";
import EditIcon from "@mui/icons-material/Edit";
import SaveIcon from "@mui/icons-material/Save";
import CancelIcon from "@mui/icons-material/Cancel";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import LockIcon from "@mui/icons-material/Lock";
import PersonIcon from "@mui/icons-material/Person";

interface UserProfile {
  id: number;
  username: string;
  email: string;
  role: string;
  created_at: string;
}

interface PasswordChange {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [editedEmail, setEditedEmail] = useState("");
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordData, setPasswordData] = useState<PasswordChange>({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const { data: profile, isLoading } = useQuery<UserProfile>({
    queryKey: ["profile"],
    queryFn: () => apiFetch<UserProfile>("/api/users/me"),
  });

  const updateProfileMutation = useMutation({
    mutationFn: (data: { email: string }) =>
      apiFetch(`/api/users/${profile?.id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
      setIsEditing(false);
      setSuccess("Profile updated successfully");
      setTimeout(() => setSuccess(""), 3000);
    },
    onError: (err: Error) => {
      setError(err.message || "Failed to update profile");
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: (data: PasswordChange) =>
      apiFetch("/api/users/me/password", {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      setShowPasswordForm(false);
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
      setSuccess("Password changed successfully");
      setTimeout(() => setSuccess(""), 3000);
    },
    onError: (err: Error) => {
      setError(err.message || "Failed to change password");
    },
  });

  const handleEditProfile = () => {
    if (isEditing) {
      setIsEditing(false);
      setEditedEmail(profile?.email || "");
    } else {
      setIsEditing(true);
      setEditedEmail(profile?.email || "");
    }
  };

  const handleSaveProfile = () => {
    if (!editedEmail.trim()) {
      setError("Email cannot be empty");
      return;
    }
    setError("");
    updateProfileMutation.mutate({ email: editedEmail });
  };

  const handleChangePassword = () => {
    setError("");
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError("New passwords do not match");
      return;
    }
    if (passwordData.new_password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    changePasswordMutation.mutate(passwordData);
  };

  const getRoleColor = (role: string) => {
    switch (role.toLowerCase()) {
      case "admin":
        return "error";
      case "operator":
        return "warning";
      case "viewer":
        return "info";
      default:
        return "default";
    }
  };

  const getInitials = (username: string) => {
    return username
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!profile) {
    return (
      <Box>
        <Alert severity="error">Failed to load profile</Alert>
      </Box>
    );
  }

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" fontWeight={700}>
          Profile Settings
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Manage your account information and security
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" onClose={() => setError("")}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess("")}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ textAlign: "center", borderRadius: 2, boxShadow: 2 }}>
            <CardContent>
              <Avatar
                sx={{
                  width: 120,
                  height: 120,
                  margin: "0 auto 16px",
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  fontSize: "2.5rem",
                  fontWeight: 700,
                }}
              >
                {getInitials(profile.username)}
              </Avatar>
              <Typography variant="h5" fontWeight={700} gutterBottom>
                {profile.username}
              </Typography>
              <Chip
                label={profile.role}
                color={getRoleColor(profile.role)}
                size="small"
                sx={{ fontWeight: 600, mb: 2 }}
              />
              <Typography variant="body2" color="text.secondary">
                Member since {new Date(profile.created_at).toLocaleDateString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Stack spacing={3}>
            <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <PersonIcon color="primary" />
                    <Typography variant="h6" fontWeight={600}>
                      Account Information
                    </Typography>
                  </Box>
                  {!isEditing ? (
                    <Button
                      startIcon={<EditIcon />}
                      onClick={handleEditProfile}
                      variant="outlined"
                      size="small"
                    >
                      Edit
                    </Button>
                  ) : (
                    <Stack direction="row" spacing={1}>
                      <Button
                        startIcon={<CancelIcon />}
                        onClick={handleEditProfile}
                        variant="outlined"
                        size="small"
                        color="inherit"
                      >
                        Cancel
                      </Button>
                      <Button
                        startIcon={<SaveIcon />}
                        onClick={handleSaveProfile}
                        variant="contained"
                        size="small"
                        disabled={updateProfileMutation.isPending}
                      >
                        Save
                      </Button>
                    </Stack>
                  )}
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Username"
                      value={profile.username}
                      fullWidth
                      disabled
                      helperText="Username cannot be changed"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Email"
                      value={isEditing ? editedEmail : profile.email}
                      onChange={(e) => setEditedEmail(e.target.value)}
                      fullWidth
                      disabled={!isEditing}
                      type="email"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Role"
                      value={profile.role}
                      fullWidth
                      disabled
                      helperText="Contact admin to change role"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="User ID"
                      value={profile.id}
                      fullWidth
                      disabled
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>

            <Card sx={{ borderRadius: 2, boxShadow: 2 }}>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <LockIcon color="primary" />
                    <Typography variant="h6" fontWeight={600}>
                      Security
                    </Typography>
                  </Box>
                  {!showPasswordForm && (
                    <Button
                      startIcon={<LockIcon />}
                      onClick={() => setShowPasswordForm(true)}
                      variant="outlined"
                      size="small"
                    >
                      Change Password
                    </Button>
                  )}
                </Box>

                {showPasswordForm ? (
                  <Stack spacing={2}>
                    <TextField
                      label="Current Password"
                      type={showCurrentPassword ? "text" : "password"}
                      value={passwordData.current_password}
                      onChange={(e) =>
                        setPasswordData({ ...passwordData, current_password: e.target.value })
                      }
                      fullWidth
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                              edge="end"
                            >
                              {showCurrentPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />
                    <TextField
                      label="New Password"
                      type={showNewPassword ? "text" : "password"}
                      value={passwordData.new_password}
                      onChange={(e) =>
                        setPasswordData({ ...passwordData, new_password: e.target.value })
                      }
                      fullWidth
                      helperText="At least 8 characters"
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowNewPassword(!showNewPassword)}
                              edge="end"
                            >
                              {showNewPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />
                    <TextField
                      label="Confirm New Password"
                      type={showConfirmPassword ? "text" : "password"}
                      value={passwordData.confirm_password}
                      onChange={(e) =>
                        setPasswordData({ ...passwordData, confirm_password: e.target.value })
                      }
                      fullWidth
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                              edge="end"
                            >
                              {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                    />
                    <Stack direction="row" spacing={2} justifyContent="flex-end">
                      <Button
                        onClick={() => {
                          setShowPasswordForm(false);
                          setPasswordData({
                            current_password: "",
                            new_password: "",
                            confirm_password: "",
                          });
                        }}
                        variant="outlined"
                        color="inherit"
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={handleChangePassword}
                        variant="contained"
                        disabled={changePasswordMutation.isPending}
                      >
                        Update Password
                      </Button>
                    </Stack>
                  </Stack>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Keep your account secure by using a strong password
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Stack>
        </Grid>
      </Grid>
    </Stack>
  );
}
