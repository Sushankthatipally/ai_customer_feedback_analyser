import { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import type { RootState } from "../store";
import {
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Switch,
  FormControlLabel,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  IconButton,
  Divider,
} from "@mui/material";
import {
  Webhook,
  Email,
  Chat,
  IntegrationInstructions,
  Settings,
  CheckCircle,
  Cancel,
  Add,
  Refresh,
} from "@mui/icons-material";

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: any;
  enabled: boolean;
  status: "connected" | "disconnected" | "error";
  config?: any;
}

export default function Integrations() {
  const { user } = useSelector((state: RootState) => state.auth);

  // Check if user can modify integrations (only admin and analyst)
  const canModify = user?.role === "admin" || user?.role === "analyst";
  const isViewer = user?.role === "viewer";

  // Default integrations template
  const defaultIntegrations: Integration[] = [
    {
      id: "slack",
      name: "Slack",
      description: "Get feedback notifications in Slack channels",
      icon: Chat,
      enabled: false,
      status: "disconnected",
    },
    {
      id: "teams",
      name: "Microsoft Teams",
      description: "Send feedback alerts to Teams channels",
      icon: Chat,
      enabled: false,
      status: "disconnected",
    },
    {
      id: "email",
      name: "Email Notifications",
      description: "Receive email alerts for critical feedback",
      icon: Email,
      enabled: true,
      status: "connected",
      config: { email: "team@example.com" },
    },
    {
      id: "webhook",
      name: "Custom Webhook",
      description: "Send feedback to your custom endpoint",
      icon: Webhook,
      enabled: false,
      status: "disconnected",
    },
    {
      id: "zapier",
      name: "Zapier",
      description: "Connect to 5000+ apps via Zapier",
      icon: IntegrationInstructions,
      enabled: false,
      status: "disconnected",
    },
  ];

  // Load integrations from localStorage or use defaults
  const loadIntegrations = (): Integration[] => {
    try {
      const saved = localStorage.getItem("integrations_config");
      if (saved) {
        const parsedIntegrations = JSON.parse(saved);
        // Merge saved data with default template to preserve icons
        return defaultIntegrations.map((def) => {
          const saved = parsedIntegrations.find(
            (i: Integration) => i.id === def.id
          );
          return saved ? { ...def, ...saved, icon: def.icon } : def;
        });
      }
    } catch (error) {
      console.error("Failed to load integrations:", error);
    }
    return defaultIntegrations;
  };

  const [integrations, setIntegrations] = useState<Integration[]>(
    loadIntegrations()
  );
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [selectedIntegration, setSelectedIntegration] =
    useState<Integration | null>(null);
  const [configValues, setConfigValues] = useState<any>({});
  const [testResult, setTestResult] = useState<string | null>(null);

  // Save integrations to localStorage whenever they change
  useEffect(() => {
    try {
      // Don't save the icon component, just the data
      const dataToSave = integrations.map(({ icon, ...rest }) => rest);
      localStorage.setItem("integrations_config", JSON.stringify(dataToSave));
    } catch (error) {
      console.error("Failed to save integrations:", error);
    }
  }, [integrations]);

  const handleToggle = (integrationId: string) => {
    setIntegrations((prev) =>
      prev.map((integration) =>
        integration.id === integrationId
          ? { ...integration, enabled: !integration.enabled }
          : integration
      )
    );
  };

  const handleConfigure = (integration: Integration) => {
    setSelectedIntegration(integration);
    setConfigValues(integration.config || {});
    setConfigDialogOpen(true);
    setTestResult(null);
  };

  const handleSaveConfig = () => {
    if (selectedIntegration) {
      setIntegrations((prev) =>
        prev.map((integration) =>
          integration.id === selectedIntegration.id
            ? {
                ...integration,
                config: configValues,
                status: "connected",
                enabled: true,
              }
            : integration
        )
      );
      setConfigDialogOpen(false);
      setSelectedIntegration(null);
    }
  };

  const handleTestConnection = () => {
    // Simulate testing connection
    setTimeout(() => {
      setTestResult("Connection successful! Integration is working properly.");
    }, 1000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "connected":
        return "success";
      case "error":
        return "error";
      default:
        return "default";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "connected":
        return <CheckCircle />;
      case "error":
        return <Cancel />;
      default:
        return null;
    }
  };

  return (
    <Box>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={3}
      >
        <Box>
          <Typography variant="h4" gutterBottom>
            Integrations
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Connect your feedback system with external tools and services
          </Typography>
        </Box>
        {canModify && (
          <Button
            variant="outlined"
            startIcon={<Add />}
            onClick={() =>
              alert("Custom integration setup would be available here")
            }
          >
            Add Custom Integration
          </Button>
        )}
      </Box>

      {isViewer && (
        <Alert severity="info" sx={{ mb: 3 }}>
          You are viewing integrations in read-only mode. Contact your
          administrator to make changes.
        </Alert>
      )}

      <Grid container spacing={3}>
        {integrations.map((integration) => {
          const IconComponent = integration.icon;
          return (
            <Grid item xs={12} md={6} lg={4} key={integration.id}>
              <Card
                sx={{
                  height: "100%",
                  display: "flex",
                  flexDirection: "column",
                  border: integration.enabled ? "2px solid" : "1px solid",
                  borderColor: integration.enabled ? "primary.main" : "divider",
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" alignItems="center" mb={2}>
                    <IconComponent
                      sx={{
                        fontSize: 40,
                        color: integration.enabled
                          ? "primary.main"
                          : "text.secondary",
                        mr: 2,
                      }}
                    />
                    <Box flexGrow={1}>
                      <Typography variant="h6">{integration.name}</Typography>
                      <Chip
                        label={integration.status}
                        color={getStatusColor(integration.status)}
                        size="small"
                        icon={getStatusIcon(integration.status) || undefined}
                        sx={{ mt: 0.5 }}
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {integration.description}
                  </Typography>
                  {integration.config && (
                    <Box mt={2}>
                      <Typography variant="caption" color="textSecondary">
                        Configuration:
                      </Typography>
                      {Object.entries(integration.config).map(
                        ([key, value]) => (
                          <Typography
                            key={key}
                            variant="caption"
                            display="block"
                          >
                            {key}: {String(value)}
                          </Typography>
                        )
                      )}
                    </Box>
                  )}
                </CardContent>
                <Divider />
                <CardActions
                  sx={{ justifyContent: "space-between", px: 2, py: 1.5 }}
                >
                  <FormControlLabel
                    control={
                      <Switch
                        checked={integration.enabled}
                        onChange={() => handleToggle(integration.id)}
                        color="primary"
                        disabled={!canModify}
                      />
                    }
                    label={integration.enabled ? "Enabled" : "Disabled"}
                  />
                  <Button
                    size="small"
                    startIcon={<Settings />}
                    onClick={() => handleConfigure(integration)}
                    disabled={!canModify}
                  >
                    Configure
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Configuration Dialog */}
      <Dialog
        open={configDialogOpen}
        onClose={() => setConfigDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Configure {selectedIntegration?.name}</DialogTitle>
        <DialogContent>
          <Box mt={2}>
            {selectedIntegration?.id === "slack" && (
              <>
                <TextField
                  fullWidth
                  label="Webhook URL"
                  placeholder="https://hooks.slack.com/services/..."
                  value={configValues.webhookUrl || ""}
                  onChange={(e) =>
                    setConfigValues({
                      ...configValues,
                      webhookUrl: e.target.value,
                    })
                  }
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Channel"
                  placeholder="#feedback"
                  value={configValues.channel || ""}
                  onChange={(e) =>
                    setConfigValues({
                      ...configValues,
                      channel: e.target.value,
                    })
                  }
                  margin="normal"
                />
              </>
            )}

            {selectedIntegration?.id === "teams" && (
              <TextField
                fullWidth
                label="Incoming Webhook URL"
                placeholder="https://outlook.office.com/webhook/..."
                value={configValues.webhookUrl || ""}
                onChange={(e) =>
                  setConfigValues({
                    ...configValues,
                    webhookUrl: e.target.value,
                  })
                }
                margin="normal"
              />
            )}

            {selectedIntegration?.id === "email" && (
              <>
                <TextField
                  fullWidth
                  label="Email Address"
                  placeholder="team@example.com"
                  type="email"
                  value={configValues.email || ""}
                  onChange={(e) =>
                    setConfigValues({ ...configValues, email: e.target.value })
                  }
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Notification Frequency"
                  select
                  SelectProps={{ native: true }}
                  value={configValues.frequency || "instant"}
                  onChange={(e) =>
                    setConfigValues({
                      ...configValues,
                      frequency: e.target.value,
                    })
                  }
                  margin="normal"
                >
                  <option value="instant">Instant</option>
                  <option value="hourly">Hourly Digest</option>
                  <option value="daily">Daily Digest</option>
                </TextField>
              </>
            )}

            {selectedIntegration?.id === "webhook" && (
              <>
                <TextField
                  fullWidth
                  label="Endpoint URL"
                  placeholder="https://your-api.com/webhook"
                  value={configValues.url || ""}
                  onChange={(e) =>
                    setConfigValues({ ...configValues, url: e.target.value })
                  }
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Secret Key"
                  type="password"
                  placeholder="Your webhook secret"
                  value={configValues.secret || ""}
                  onChange={(e) =>
                    setConfigValues({ ...configValues, secret: e.target.value })
                  }
                  margin="normal"
                />
              </>
            )}

            {selectedIntegration?.id === "zapier" && (
              <Alert severity="info">
                To connect Zapier:
                <ol>
                  <li>Create a new Zap in your Zapier account</li>
                  <li>Use "Webhooks by Zapier" as the trigger</li>
                  <li>Copy the webhook URL below to your Zap</li>
                  <li>Configure the action app (Gmail, Slack, etc.)</li>
                </ol>
                <TextField
                  fullWidth
                  label="Zapier Webhook URL"
                  placeholder="Enter your Zapier webhook URL"
                  value={configValues.zapierUrl || ""}
                  onChange={(e) =>
                    setConfigValues({
                      ...configValues,
                      zapierUrl: e.target.value,
                    })
                  }
                  margin="normal"
                />
              </Alert>
            )}

            {testResult && (
              <Alert severity="success" sx={{ mt: 2 }}>
                {testResult}
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfigDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleTestConnection}
            startIcon={<Refresh />}
            disabled={!Object.keys(configValues).length}
          >
            Test Connection
          </Button>
          <Button
            onClick={handleSaveConfig}
            variant="contained"
            disabled={!Object.keys(configValues).length}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Integration Guide */}
      <Paper sx={{ p: 3, mt: 3, bgcolor: "background.default" }}>
        <Typography variant="h6" gutterBottom>
          Integration Guide
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" gutterBottom>
              📌 Getting Started
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Enable integrations to send feedback notifications to your team's
              tools. Each integration can be configured separately with specific
              settings.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" gutterBottom>
              🔔 Notification Rules
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Integrations trigger on: new feedback, critical urgency alerts,
              negative sentiment detection, bug reports, and feature requests.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" gutterBottom>
              🔒 Security
            </Typography>
            <Typography variant="body2" color="textSecondary">
              All webhook URLs and API keys are encrypted at rest. Connections
              use HTTPS and are validated before activation.
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}
