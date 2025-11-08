import { Routes, Route, Navigate } from "react-router-dom";
import { Box } from "@mui/material";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";
import Dashboard from "./pages/Dashboard";
import FeedbackList from "./pages/FeedbackList";
import Analytics from "./pages/Analytics";
import Integrations from "./pages/Integrations";
import Reports from "./pages/Reports";
import Profile from "./pages/Profile";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import AdminManagement from "./pages/AdminManagement";
import { useAuth } from "./hooks/useAuth";

function App() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
      >
        Loading...
      </Box>
    );
  }

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/feedback" element={<FeedbackList />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route
          path="/integrations"
          element={
            <ProtectedRoute allowedRoles={["admin", "analyst"]}>
              <Integrations />
            </ProtectedRoute>
          }
        />
        <Route path="/reports" element={<Reports />} />
        <Route path="/profile" element={<Profile />} />
        <Route
          path="/admin"
          element={
            <ProtectedRoute allowedRoles={["admin"]}>
              <AdminManagement />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
