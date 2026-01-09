"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Alert, Box, Button, Card, CardContent, Stack, TextField, Typography } from "@mui/material";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

const SetupSchema = z
  .object({
    username: z.string().min(3, "Minimum 3 characters"),
    email: z.string().email("Invalid email"),
    password: z
      .string()
      .min(8, "At least 8 characters")
      .regex(/[A-Z]/, "Include an uppercase letter")
      .regex(/[a-z]/, "Include a lowercase letter")
      .regex(/[0-9]/, "Include a number"),
    confirm: z.string().min(1, "Confirm your password"),
  })
  .refine((vals) => vals.password === vals.confirm, {
    path: ["confirm"],
    message: "Passwords do not match",
  });

export default function SetupPage() {
  const { locale } = useParams();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<z.infer<typeof SetupSchema>>({ resolver: zodResolver(SetupSchema) });

  const onSubmit = async (values: z.infer<typeof SetupSchema>) => {
    setError(null);
    setLoading(true);
    try {
      const res = await fetch("/api/auth/setup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: values.username.trim(),
          email: values.email.trim(),
          password: values.password,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Setup failed");
      }
      router.replace(`/${locale}/dashboard`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Setup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", p: 2 }}>
      <Card sx={{ maxWidth: 520, width: "100%", boxShadow: 6 }}>
        <CardContent>
          <Stack spacing={2}>
            <Box>
              <Typography variant="h5" fontWeight={700}>Welcome to Server Monitor</Typography>
              <Typography variant="body2" color="text.secondary">Create the first administrator account</Typography>
            </Box>

            {error && <Alert severity="error">{error}</Alert>}

            <TextField label="Username" fullWidth {...register("username")} error={!!errors.username} helperText={errors.username?.message} />
            <TextField label="Email" fullWidth {...register("email")} error={!!errors.email} helperText={errors.email?.message} />
            <TextField label="Password" type="password" fullWidth {...register("password")} error={!!errors.password} helperText={errors.password?.message} />
            <TextField label="Confirm Password" type="password" fullWidth {...register("confirm")} error={!!errors.confirm} helperText={errors.confirm?.message} />
            <Button variant="contained" size="large" onClick={handleSubmit(onSubmit)} disabled={loading}>
              {loading ? "Creating account..." : "Create Admin Account"}
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
