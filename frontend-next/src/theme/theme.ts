import { createTheme, PaletteMode } from "@mui/material";

/**
 * Professional theme configuration for Server Monitor
 * Supports both light and dark modes with modern design
 */
export const createAppTheme = (mode: PaletteMode) =>
  createTheme({
    palette: {
      mode,
      ...(mode === "light"
        ? {
            // Light mode colors
            primary: {
              main: "#1976d2",
              light: "#42a5f5",
              dark: "#1565c0",
              contrastText: "#fff",
            },
            secondary: {
              main: "#9c27b0",
              light: "#ba68c8",
              dark: "#7b1fa2",
              contrastText: "#fff",
            },
            background: {
              default: "#f5f7fa",
              paper: "#ffffff",
            },
            text: {
              primary: "rgba(0, 0, 0, 0.87)",
              secondary: "rgba(0, 0, 0, 0.6)",
            },
            divider: "rgba(0, 0, 0, 0.12)",
            success: {
              main: "#2e7d32",
              light: "#4caf50",
              dark: "#1b5e20",
            },
            error: {
              main: "#d32f2f",
              light: "#ef5350",
              dark: "#c62828",
            },
            warning: {
              main: "#ed6c02",
              light: "#ff9800",
              dark: "#e65100",
            },
            info: {
              main: "#0288d1",
              light: "#03a9f4",
              dark: "#01579b",
            },
          }
        : {
            // Dark mode colors
            primary: {
              main: "#90caf9",
              light: "#e3f2fd",
              dark: "#42a5f5",
              contrastText: "rgba(0, 0, 0, 0.87)",
            },
            secondary: {
              main: "#ce93d8",
              light: "#f3e5f5",
              dark: "#ab47bc",
              contrastText: "rgba(0, 0, 0, 0.87)",
            },
            background: {
              default: "#0a1929",
              paper: "#132f4c",
            },
            text: {
              primary: "#fff",
              secondary: "rgba(255, 255, 255, 0.7)",
            },
            divider: "rgba(194, 224, 255, 0.08)",
            success: {
              main: "#66bb6a",
              light: "#81c784",
              dark: "#388e3c",
            },
            error: {
              main: "#f44336",
              light: "#e57373",
              dark: "#d32f2f",
            },
            warning: {
              main: "#ffa726",
              light: "#ffb74d",
              dark: "#f57c00",
            },
            info: {
              main: "#29b6f6",
              light: "#4fc3f7",
              dark: "#0288d1",
            },
          }),
    },
    typography: {
      fontFamily: [
        "-apple-system",
        "BlinkMacSystemFont",
        '"Segoe UI"',
        "Roboto",
        '"Helvetica Neue"',
        "Arial",
        "sans-serif",
        '"Apple Color Emoji"',
        '"Segoe UI Emoji"',
        '"Segoe UI Symbol"',
      ].join(","),
      h1: {
        fontWeight: 700,
        fontSize: "2.5rem",
        lineHeight: 1.2,
      },
      h2: {
        fontWeight: 700,
        fontSize: "2rem",
        lineHeight: 1.3,
      },
      h3: {
        fontWeight: 600,
        fontSize: "1.75rem",
        lineHeight: 1.4,
      },
      h4: {
        fontWeight: 600,
        fontSize: "1.5rem",
        lineHeight: 1.4,
      },
      h5: {
        fontWeight: 600,
        fontSize: "1.25rem",
        lineHeight: 1.5,
      },
      h6: {
        fontWeight: 600,
        fontSize: "1rem",
        lineHeight: 1.5,
      },
      body1: {
        fontSize: "1rem",
        lineHeight: 1.6,
      },
      body2: {
        fontSize: "0.875rem",
        lineHeight: 1.6,
      },
      button: {
        textTransform: "none",
        fontWeight: 600,
      },
    },
    shape: {
      borderRadius: 12,
    },
    shadows: [
      "none",
      mode === "light"
        ? "0px 2px 4px rgba(0,0,0,0.05)"
        : "0px 2px 4px rgba(0,0,0,0.3)",
      mode === "light"
        ? "0px 4px 8px rgba(0,0,0,0.08)"
        : "0px 4px 8px rgba(0,0,0,0.4)",
      mode === "light"
        ? "0px 8px 16px rgba(0,0,0,0.1)"
        : "0px 8px 16px rgba(0,0,0,0.5)",
      mode === "light"
        ? "0px 12px 24px rgba(0,0,0,0.12)"
        : "0px 12px 24px rgba(0,0,0,0.6)",
      mode === "light"
        ? "0px 16px 32px rgba(0,0,0,0.14)"
        : "0px 16px 32px rgba(0,0,0,0.7)",
      ...Array(19).fill(
        mode === "light"
          ? "0px 20px 40px rgba(0,0,0,0.16)"
          : "0px 20px 40px rgba(0,0,0,0.8)",
      ),
    ] as any,
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            padding: "8px 20px",
            fontSize: "0.9375rem",
            fontWeight: 600,
          },
          contained: {
            boxShadow:
              mode === "light"
                ? "0 2px 8px rgba(0,0,0,0.15)"
                : "0 2px 8px rgba(0,0,0,0.5)",
            "&:hover": {
              boxShadow:
                mode === "light"
                  ? "0 4px 12px rgba(0,0,0,0.2)"
                  : "0 4px 12px rgba(0,0,0,0.6)",
            },
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            boxShadow:
              mode === "light"
                ? "0 2px 8px rgba(0,0,0,0.08)"
                : "0 2px 8px rgba(0,0,0,0.4)",
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
          },
          elevation1: {
            boxShadow:
              mode === "light"
                ? "0 2px 4px rgba(0,0,0,0.05)"
                : "0 2px 4px rgba(0,0,0,0.3)",
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
            backgroundColor: mode === "light" ? "#ffffff" : "#132f4c",
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundImage: "none",
            backgroundColor: mode === "light" ? "#ffffff" : "#0a1929",
            borderRight:
              mode === "light"
                ? "1px solid rgba(0,0,0,0.12)"
                : "1px solid rgba(194,224,255,0.08)",
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            "&.Mui-selected": {
              backgroundColor:
                mode === "light"
                  ? "rgba(25, 118, 210, 0.08)"
                  : "rgba(144, 202, 249, 0.16)",
              "&:hover": {
                backgroundColor:
                  mode === "light"
                    ? "rgba(25, 118, 210, 0.12)"
                    : "rgba(144, 202, 249, 0.24)",
              },
            },
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            "& .MuiOutlinedInput-root": {
              borderRadius: 8,
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 8,
          },
        },
      },
    },
  });
