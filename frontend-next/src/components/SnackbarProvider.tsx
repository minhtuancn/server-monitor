"use client";

import { Alert, Snackbar } from "@mui/material";
import React, { createContext, useContext, useState, useCallback } from "react";

type SnackbarSeverity = "success" | "info" | "warning" | "error";

interface SnackbarContextType {
  showSnackbar: (message: string, severity?: SnackbarSeverity) => void;
  showSuccess: (message: string) => void;
  showError: (message: string) => void;
  showInfo: (message: string) => void;
  showWarning: (message: string) => void;
}

const SnackbarContext = createContext<SnackbarContextType | undefined>(undefined);

export function useSnackbar() {
  const context = useContext(SnackbarContext);
  if (!context) {
    throw new Error("useSnackbar must be used within a SnackbarProvider");
  }
  return context;
}

interface SnackbarState {
  open: boolean;
  message: string;
  severity: SnackbarSeverity;
}

export function SnackbarProvider({ children }: { children: React.ReactNode }) {
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    message: "",
    severity: "info",
  });

  const showSnackbar = useCallback((message: string, severity: SnackbarSeverity = "info") => {
    setSnackbar({ open: true, message, severity });
  }, []);

  const showSuccess = useCallback((message: string) => {
    showSnackbar(message, "success");
  }, [showSnackbar]);

  const showError = useCallback((message: string) => {
    showSnackbar(message, "error");
  }, [showSnackbar]);

  const showInfo = useCallback((message: string) => {
    showSnackbar(message, "info");
  }, [showSnackbar]);

  const showWarning = useCallback((message: string) => {
    showSnackbar(message, "warning");
  }, [showSnackbar]);

  const handleClose = useCallback((event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === "clickaway") {
      return;
    }
    setSnackbar((prev) => ({ ...prev, open: false }));
  }, []);

  return (
    <SnackbarContext.Provider
      value={{ showSnackbar, showSuccess, showError, showInfo, showWarning }}
    >
      {children}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert onClose={handleClose} severity={snackbar.severity} sx={{ width: "100%" }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
}
