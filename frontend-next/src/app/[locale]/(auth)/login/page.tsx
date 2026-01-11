"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Container,
  IconButton,
  InputAdornment,
  Stack,
  TextField,
  Typography,
  useTheme,
} from "@mui/material";
import StorageIcon from "@mui/icons-material/Storage";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import LoginIcon from "@mui/icons-material/Login";
import { useSearchParams, useParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

const LoginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof LoginSchema>;

export default function LoginPage() {
  const searchParams = useSearchParams();
  const { locale } = useParams();
  const router = useRouter();
  const theme = useTheme();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Security: Remove credentials from URL if present
  useEffect(() => {
    const hasUsername = searchParams.has("username");
    const hasPassword = searchParams.has("password");
    
    if (hasUsername || hasPassword) {
      // Remove sensitive params from URL
      const newParams = new URLSearchParams(searchParams.toString());
      newParams.delete("username");
      newParams.delete("password");
      newParams.delete("user");
      newParams.delete("pass");
      newParams.delete("pwd");
      
      // Clean URL without reloading page
      const newUrl = newParams.toString() 
        ? `/${locale}/login?${newParams.toString()}`
        : `/${locale}/login`;
      
      window.history.replaceState({}, "", newUrl);
      
      // Show security warning
      setError("⚠️ Security Warning: Never include credentials in URLs! Please use the login form below.");
    }
  }, [searchParams, locale]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(LoginSchema) });

  const onSubmit = async (values: LoginForm) => {
    setError(null);
    setLoading(true);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || "Login failed");
      }
      const redirectTo = searchParams.get("redirect") || `/${locale}/dashboard`;
      window.location.href = redirectTo;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        position: "relative",
        overflow: "hidden",
        background:
          theme.palette.mode === "dark"
            ? "linear-gradient(135deg, #0a1929 0%, #1a2332 50%, #0a1929 100%)"
            : "linear-gradient(135deg, #667eea 0%, #764ba2 50%, #667eea 100%)",
      }}
    >
      {/* Animated Background Elements */}
      <Box
        sx={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.1,
          background:
            "radial-gradient(circle at 20% 50%, rgba(255,255,255,0.3) 0%, transparent 50%)",
          animation: "pulse 4s ease-in-out infinite",
          "@keyframes pulse": {
            "0%, 100%": {
              opacity: 0.1,
            },
            "50%": {
              opacity: 0.2,
            },
          },
        }}
      />
      
      <Container maxWidth="sm">
        <Card
          elevation={10}
          sx={{
            borderRadius: 4,
            overflow: "hidden",
            backdropFilter: "blur(20px)",
            background:
              theme.palette.mode === "dark"
                ? "rgba(19, 47, 76, 0.8)"
                : "rgba(255, 255, 255, 0.95)",
            border: 1,
            borderColor:
              theme.palette.mode === "dark"
                ? "rgba(255,255,255,0.1)"
                : "rgba(0,0,0,0.05)",
          }}
        >
          {/* Header Section */}
          <Box
            sx={{
              background:
                theme.palette.mode === "dark"
                  ? "linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)"
                  : "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              py: 4,
              px: 3,
              textAlign: "center",
              position: "relative",
              overflow: "hidden",
            }}
          >
            <Box
              sx={{
                position: "absolute",
                top: -50,
                right: -50,
                width: 200,
                height: 200,
                borderRadius: "50%",
                background: "rgba(255,255,255,0.1)",
                filter: "blur(40px)",
              }}
            />
            <Box
              sx={{
                width: 80,
                height: 80,
                margin: "0 auto",
                borderRadius: 3,
                background:
                  theme.palette.mode === "dark"
                    ? "rgba(144, 202, 249, 0.2)"
                    : "rgba(255,255,255,0.2)",
                backdropFilter: "blur(10px)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                mb: 2,
                boxShadow: "0 8px 32px rgba(0,0,0,0.1)",
              }}
            >
              <StorageIcon
                sx={{
                  fontSize: 48,
                  color: theme.palette.mode === "dark" ? "#90caf9" : "white",
                }}
              />
            </Box>
            <Typography
              variant="h4"
              fontWeight={700}
              sx={{
                color: theme.palette.mode === "dark" ? "white" : "white",
                mb: 1,
                position: "relative",
              }}
            >
              Server Monitor
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: theme.palette.mode === "dark" ? "rgba(255,255,255,0.8)" : "rgba(255,255,255,0.9)",
                position: "relative",
              }}
            >
              Multi-server monitoring dashboard
            </Typography>
          </Box>

          {/* Form Section */}
          <CardContent sx={{ px: 4, py: 4 }}>
            <Stack spacing={3}>
              <Box>
                <Typography variant="h5" fontWeight={700} gutterBottom>
                  Welcome Back
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Sign in to access your server dashboard
                </Typography>
              </Box>

              {error && (
                <Alert
                  severity="error"
                  sx={{
                    borderRadius: 2,
                    "& .MuiAlert-icon": {
                      fontSize: 24,
                    },
                  }}
                >
                  {error}
                </Alert>
              )}

              <form onSubmit={handleSubmit(onSubmit)}>
                <Stack spacing={2.5}>
                  <TextField
                    label="Username"
                    fullWidth
                    autoComplete="username"
                    autoFocus
                    {...register("username")}
                    error={!!errors.username}
                    helperText={errors.username?.message}
                    InputProps={{
                      sx: {
                        borderRadius: 2,
                      },
                    }}
                  />
                  
                  <TextField
                    label="Password"
                    type={showPassword ? "text" : "password"}
                    fullWidth
                    autoComplete="current-password"
                    {...register("password")}
                    error={!!errors.password}
                    helperText={errors.password?.message}
                    InputProps={{
                      sx: {
                        borderRadius: 2,
                      },
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            aria-label="toggle password visibility"
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                          >
                            {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />

                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    fullWidth
                    disabled={loading}
                    startIcon={<LoginIcon />}
                    sx={{
                      py: 1.5,
                      borderRadius: 2,
                      fontSize: "1rem",
                      fontWeight: 600,
                      textTransform: "none",
                      boxShadow: theme.palette.mode === "dark" 
                        ? "0 4px 14px rgba(144, 202, 249, 0.3)"
                        : "0 4px 14px rgba(25, 118, 210, 0.4)",
                      "&:hover": {
                        boxShadow: theme.palette.mode === "dark"
                          ? "0 6px 20px rgba(144, 202, 249, 0.4)"
                          : "0 6px 20px rgba(25, 118, 210, 0.5)",
                      },
                    }}
                  >
                    {loading ? "Signing in..." : "Sign In"}
                  </Button>
                </Stack>
              </form>

              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  bgcolor:
                    theme.palette.mode === "dark"
                      ? "rgba(144, 202, 249, 0.05)"
                      : "rgba(25, 118, 210, 0.05)",
                  border: 1,
                  borderColor:
                    theme.palette.mode === "dark"
                      ? "rgba(144, 202, 249, 0.1)"
                      : "rgba(25, 118, 210, 0.1)",
                }}
              >
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ display: "block", mb: 0.5, fontWeight: 600 }}
                >
                  First time login?
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Default credentials: <strong>admin</strong> / <strong>admin123</strong>
                </Typography>
                <Typography
                  variant="caption"
                  color="warning.main"
                  sx={{ display: "block", mt: 0.5, fontWeight: 500 }}
                >
                  ⚠️ Change password after first login
                </Typography>
              </Box>
            </Stack>
          </CardContent>
        </Card>

        {/* Footer */}
        <Box sx={{ textAlign: "center", mt: 3 }}>
          <Typography
            variant="body2"
            sx={{
              color: theme.palette.mode === "dark" ? "rgba(255,255,255,0.7)" : "rgba(255,255,255,0.9)",
            }}
          >
            © 2026 Server Monitor Dashboard. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}
