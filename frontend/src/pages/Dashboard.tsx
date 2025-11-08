import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  ThumbUp,
  ThumbDown,
  BugReport,
  Lightbulb,
} from "@mui/icons-material";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { RootState, AppDispatch } from "../store";
import { setDashboardStats, setLoading } from "../store/slices/analyticsSlice";
import { analyticsAPI } from "../api";

const COLORS = ["#4caf50", "#f44336", "#ff9800", "#2196f3"];

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  trend?: number;
}

function StatCard({ title, value, icon, color, trend }: StatCardProps) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
            {trend !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                {trend >= 0 ? (
                  <TrendingUp color="success" fontSize="small" />
                ) : (
                  <TrendingDown color="error" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={trend >= 0 ? "success.main" : "error.main"}
                >
                  {Math.abs(trend)}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              backgroundColor: color,
              borderRadius: "50%",
              p: 2,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const dispatch = useDispatch<AppDispatch>();
  const { dashboard, loading } = useSelector(
    (state: RootState) => state.analytics
  );

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    dispatch(setLoading(true));
    try {
      const response = await analyticsAPI.getDashboard(30);
      dispatch(setDashboardStats(response.data));
    } catch (error) {
      console.error("Failed to load dashboard:", error);
    } finally {
      dispatch(setLoading(false));
    }
  };

  if (loading || !dashboard) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="60vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  const sentimentData = Object.entries(dashboard.sentiment_distribution).map(
    ([key, value]) => ({
      name: key.charAt(0).toUpperCase() + key.slice(1),
      value,
    })
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard Overview
      </Typography>
      <Typography
        variant="body1"
        color="textSecondary"
        gutterBottom
        sx={{ mb: 3 }}
      >
        Real-time insights from your customer feedback
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Feedback"
            value={dashboard.total_feedback.toLocaleString()}
            icon={<ThumbUp sx={{ color: "white" }} />}
            color="#2196f3"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Sentiment"
            value={dashboard.avg_sentiment.toFixed(2)}
            icon={<TrendingUp sx={{ color: "white" }} />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Feature Requests"
            value={dashboard.feature_requests}
            icon={<Lightbulb sx={{ color: "white" }} />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Bug Reports"
            value={dashboard.bug_reports}
            icon={<BugReport sx={{ color: "white" }} />}
            color="#f44336"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Sentiment Trend */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Sentiment Trend (Last 7 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={dashboard.sentiment_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="positive"
                  stackId="1"
                  stroke="#4caf50"
                  fill="#4caf50"
                />
                <Area
                  type="monotone"
                  dataKey="neutral"
                  stackId="1"
                  stroke="#ff9800"
                  fill="#ff9800"
                />
                <Area
                  type="monotone"
                  dataKey="negative"
                  stackId="1"
                  stroke="#f44336"
                  fill="#f44336"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Sentiment Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Sentiment Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
