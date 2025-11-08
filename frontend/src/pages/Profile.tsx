import { useState } from "react";
import { useSelector } from "react-redux";
import {
  Typography,
  Box,
  Paper,
  Grid,
  TextField,
  Button,
  Avatar,
  Divider,
  Alert,
  Card,
  CardContent,
} from "@mui/material";
import { Save, Edit, Person } from "@mui/icons-material";
import type { RootState } from "../store";
import { usersAPI } from "../api";

export default function Profile() {
  const { user } = useSelector((state: RootState) => state.auth);
  const [editing, setEditing] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  const [formData, setFormData] = useState({
    name: user?.full_name || user?.username || "User",
    email: user?.email || "user@example.com",
    company: "My Company",
    role: user?.role || "viewer",
  });

  const hasPendingAdminRequest =
    user?.requested_role === "admin" && !user?.role_approved;

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const handleSave = async () => {
    try {
      setError("");
      await usersAPI.updateProfile(formData);
      setEditing(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update profile");
    }
  };

  const handlePasswordChange = async () => {
    try {
      setPasswordError("");
      setPasswordSuccess(false);

      if (passwordData.newPassword !== passwordData.confirmPassword) {
        setPasswordError("New passwords do not match");
        return;
      }

      if (passwordData.newPassword.length < 6) {
        setPasswordError("Password must be at least 6 characters");
        return;
      }

      await usersAPI.changePassword(
        passwordData.currentPassword,
        passwordData.newPassword
      );

      setPasswordSuccess(true);
      setPasswordData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err: any) {
      setPasswordError(
        err.response?.data?.detail || "Failed to change password"
      );
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Profile Settings
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        Manage your account settings and preferences
      </Typography>

      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Profile updated successfully!
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {passwordSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Password changed successfully!
        </Alert>
      )}

      {passwordError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {passwordError}
        </Alert>
      )}

      {hasPendingAdminRequest && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Your admin role request is pending approval. You currently have viewer
          access.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Profile Information */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, textAlign: "center" }}>
            <Avatar
              sx={{
                width: 120,
                height: 120,
                margin: "0 auto",
                mb: 2,
                bgcolor: "primary.main",
                fontSize: 48,
              }}
            >
              {formData.name.charAt(0).toUpperCase()}
            </Avatar>
            <Typography variant="h5" gutterBottom>
              {formData.name}
            </Typography>
            <Typography variant="body2" color="textSecondary" gutterBottom>
              {formData.role}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {formData.company}
            </Typography>
            <Button
              variant="outlined"
              startIcon={<Edit />}
              sx={{ mt: 2 }}
              onClick={() => setEditing(!editing)}
            >
              {editing ? "Cancel Edit" : "Edit Profile"}
            </Button>
          </Paper>

          {/* Account Stats */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Account Stats
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2" color="textSecondary">
                  Member Since
                </Typography>
                <Typography variant="body2">
                  {new Date().toLocaleDateString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2" color="textSecondary">
                  Total Feedback
                </Typography>
                <Typography variant="body2">25</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="textSecondary">
                  Account Type
                </Typography>
                <Typography variant="body2">Professional</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Profile Form */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Personal Information
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Full Name"
                  value={formData.name}
                  onChange={(e) => handleChange("name", e.target.value)}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange("email", e.target.value)}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Company"
                  value={formData.company}
                  onChange={(e) => handleChange("company", e.target.value)}
                  disabled={!editing}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Role"
                  value={formData.role}
                  onChange={(e) => handleChange("role", e.target.value)}
                  disabled={!editing}
                />
              </Grid>
            </Grid>

            {editing && (
              <Box mt={3} display="flex" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<Save />}
                  onClick={handleSave}
                >
                  Save Changes
                </Button>
                <Button variant="outlined" onClick={() => setEditing(false)}>
                  Cancel
                </Button>
              </Box>
            )}
          </Paper>

          {/* Security Settings */}
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Security
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Current Password"
                  type="password"
                  placeholder="Enter current password"
                  value={passwordData.currentPassword}
                  onChange={(e) =>
                    setPasswordData({
                      ...passwordData,
                      currentPassword: e.target.value,
                    })
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="New Password"
                  type="password"
                  placeholder="Enter new password"
                  value={passwordData.newPassword}
                  onChange={(e) =>
                    setPasswordData({
                      ...passwordData,
                      newPassword: e.target.value,
                    })
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Confirm New Password"
                  type="password"
                  placeholder="Confirm new password"
                  value={passwordData.confirmPassword}
                  onChange={(e) =>
                    setPasswordData({
                      ...passwordData,
                      confirmPassword: e.target.value,
                    })
                  }
                />
              </Grid>
            </Grid>

            <Box mt={3}>
              <Button
                variant="outlined"
                color="primary"
                onClick={handlePasswordChange}
                disabled={
                  !passwordData.currentPassword ||
                  !passwordData.newPassword ||
                  !passwordData.confirmPassword
                }
              >
                Update Password
              </Button>
            </Box>
          </Paper>

          {/* Preferences */}
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Preferences
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Language"
                  select
                  SelectProps={{ native: true }}
                  defaultValue="en"
                  disabled={!editing}
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Timezone"
                  select
                  SelectProps={{ native: true }}
                  defaultValue="utc"
                  disabled={!editing}
                >
                  <option value="utc">UTC</option>
                  <option value="est">EST</option>
                  <option value="pst">PST</option>
                  <option value="cet">CET</option>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email Notifications"
                  select
                  SelectProps={{ native: true }}
                  defaultValue="all"
                  disabled={!editing}
                >
                  <option value="all">All Notifications</option>
                  <option value="important">Important Only</option>
                  <option value="none">None</option>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Date Format"
                  select
                  SelectProps={{ native: true }}
                  defaultValue="mm/dd/yyyy"
                  disabled={!editing}
                >
                  <option value="mm/dd/yyyy">MM/DD/YYYY</option>
                  <option value="dd/mm/yyyy">DD/MM/YYYY</option>
                  <option value="yyyy-mm-dd">YYYY-MM-DD</option>
                </TextField>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
