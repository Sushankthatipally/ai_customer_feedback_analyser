import { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import type { RootState } from "../store";
import {
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  IconButton,
  Tabs,
  Tab,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  CircularProgress,
} from "@mui/material";
import {
  CheckCircle,
  Cancel,
  Block,
  CheckCircleOutline,
  Refresh,
  Security,
} from "@mui/icons-material";
import { useSnackbar } from "notistack";
import api from "../api/client";

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string | null;
  role: string;
  requested_role: string | null;
  role_approved: boolean;
  is_active: boolean;
  created_at: string;
}

export default function AdminManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [pendingRequests, setPendingRequests] = useState<User[]>([]);
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    userId?: string;
    action?: "approve" | "reject" | "activate" | "deactivate";
    username?: string;
  }>({ open: false });
  const { enqueueSnackbar } = useSnackbar();
  const { user } = useSelector((state: RootState) => state.auth);

  const isSuperAdmin = user?.is_super_admin || false;

  useEffect(() => {
    loadData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      loadData();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [usersRes, pendingRes] = await Promise.all([
        api.get("/admin/users"),
        api.get("/admin/pending-requests"),
      ]);
      setUsers(usersRes.data);
      setPendingRequests(pendingRes.data);
    } catch (error: any) {
      enqueueSnackbar(error.response?.data?.detail || "Failed to load data", {
        variant: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApproveRole = async (userId: string, approved: boolean) => {
    try {
      const response = await api.post("/admin/approve-role", {
        user_id: userId,
        approved,
      });
      enqueueSnackbar(response.data.message, { variant: "success" });
      loadData();
    } catch (error: any) {
      enqueueSnackbar(error.response?.data?.detail || "Failed to update role", {
        variant: "error",
      });
    }
    setConfirmDialog({ open: false });
  };

  const handleToggleUserStatus = async (userId: string, isActive: boolean) => {
    try {
      const response = await api.patch(`/admin/users/${userId}/status`, null, {
        params: { is_active: isActive },
      });
      enqueueSnackbar(response.data.message, { variant: "success" });
      loadData();
    } catch (error: any) {
      enqueueSnackbar(
        error.response?.data?.detail || "Failed to update user status",
        { variant: "error" }
      );
    }
    setConfirmDialog({ open: false });
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case "admin":
        return "error";
      case "analyst":
        return "warning";
      case "viewer":
        return "info";
      default:
        return "default";
    }
  };

  const renderUsersTable = (usersList: User[], showApprovalActions = false) => (
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Username</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Full Name</TableCell>
            <TableCell>Current Role</TableCell>
            {showApprovalActions && <TableCell>Requested Role</TableCell>}
            <TableCell>Status</TableCell>
            <TableCell>Created</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {usersList.length === 0 ? (
            <TableRow>
              <TableCell colSpan={showApprovalActions ? 8 : 7} align="center">
                <Typography color="textSecondary">
                  {showApprovalActions
                    ? "No pending requests"
                    : "No users found"}
                </Typography>
              </TableCell>
            </TableRow>
          ) : (
            usersList.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.full_name || "-"}</TableCell>
                <TableCell>
                  <Chip
                    label={user.role.toUpperCase()}
                    color={getRoleColor(user.role)}
                    size="small"
                  />
                </TableCell>
                {showApprovalActions && (
                  <TableCell>
                    <Chip
                      label={user.requested_role?.toUpperCase() || "-"}
                      color={getRoleColor(user.requested_role || "")}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                )}
                <TableCell>
                  <Chip
                    label={user.is_active ? "Active" : "Disabled"}
                    color={user.is_active ? "success" : "default"}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(user.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {showApprovalActions ? (
                    <Box>
                      <IconButton
                        color="success"
                        size="small"
                        onClick={() =>
                          setConfirmDialog({
                            open: true,
                            userId: user.id,
                            action: "approve",
                            username: user.username,
                          })
                        }
                        title="Approve"
                      >
                        <CheckCircle />
                      </IconButton>
                      <IconButton
                        color="error"
                        size="small"
                        onClick={() =>
                          setConfirmDialog({
                            open: true,
                            userId: user.id,
                            action: "reject",
                            username: user.username,
                          })
                        }
                        title="Reject"
                      >
                        <Cancel />
                      </IconButton>
                    </Box>
                  ) : (
                    <IconButton
                      color={user.is_active ? "error" : "success"}
                      size="small"
                      onClick={() =>
                        setConfirmDialog({
                          open: true,
                          userId: user.id,
                          action: user.is_active ? "deactivate" : "activate",
                          username: user.username,
                        })
                      }
                      title={user.is_active ? "Deactivate" : "Activate"}
                    >
                      {user.is_active ? <Block /> : <CheckCircleOutline />}
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );

  const handleConfirm = () => {
    if (!confirmDialog.userId) return;

    if (confirmDialog.action === "approve") {
      handleApproveRole(confirmDialog.userId, true);
    } else if (confirmDialog.action === "reject") {
      handleApproveRole(confirmDialog.userId, false);
    } else if (confirmDialog.action === "activate") {
      handleToggleUserStatus(confirmDialog.userId, true);
    } else if (confirmDialog.action === "deactivate") {
      handleToggleUserStatus(confirmDialog.userId, false);
    }
  };

  return (
    <Box>
      <Box
        mb={3}
        display="flex"
        justifyContent="space-between"
        alignItems="center"
      >
        <Box>
          <Typography variant="h4" gutterBottom>
            User Management
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage users, approve role requests, and monitor user activity
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={loading ? <CircularProgress size={20} /> : <Refresh />}
          onClick={loadData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {isSuperAdmin && (
        <Alert severity="info" icon={<Security />} sx={{ mb: 3 }}>
          <strong>Super Admin Access:</strong> You can view and manage users
          across all tenants.
        </Alert>
      )}

      {pendingRequests.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          You have {pendingRequests.length} pending admin role request
          {pendingRequests.length > 1 ? "s" : ""} to review
        </Alert>
      )}

      <Paper>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          sx={{ borderBottom: 1, borderColor: "divider" }}
        >
          <Tab label={`All Users (${users.length})`} />
          <Tab
            label={`Pending Requests (${pendingRequests.length})`}
            icon={
              pendingRequests.length > 0 ? (
                <Chip
                  label={pendingRequests.length}
                  color="warning"
                  size="small"
                />
              ) : undefined
            }
            iconPosition="end"
          />
        </Tabs>

        <Box p={3}>
          {tabValue === 0 && renderUsersTable(users, false)}
          {tabValue === 1 && renderUsersTable(pendingRequests, true)}
        </Box>
      </Paper>

      {/* Confirmation Dialog */}
      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ open: false })}
      >
        <DialogTitle>Confirm Action</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {confirmDialog.action === "approve" &&
              `Are you sure you want to approve ${confirmDialog.username}'s admin role request?`}
            {confirmDialog.action === "reject" &&
              `Are you sure you want to reject ${confirmDialog.username}'s admin role request?`}
            {confirmDialog.action === "activate" &&
              `Are you sure you want to activate ${confirmDialog.username}'s account?`}
            {confirmDialog.action === "deactivate" &&
              `Are you sure you want to deactivate ${confirmDialog.username}'s account?`}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog({ open: false })}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} variant="contained" color="primary">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
