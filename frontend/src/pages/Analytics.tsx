import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import {
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
} from "@mui/material";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";
import {
  TrendingUp,
  Psychology,
  Speed,
  Category,
  Group,
} from "@mui/icons-material";
import type { RootState } from "../store";
import { analyticsAPI } from "../api";

const EMOTION_COLORS: Record<string, string> = {
  joy: "#4caf50",
  anger: "#f44336",
  sadness: "#2196f3",
  fear: "#9c27b0",
  surprise: "#ff9800",
  neutral: "#757575",
  disgust: "#795548",
};

const URGENCY_COLORS: Record<string, string> = {
  critical: "#d32f2f",
  high: "#f57c00",
  medium: "#fbc02d",
  low: "#388e3c",
};

export default function Analytics() {
  const { dashboard } = useSelector((state: RootState) => state.analytics);
  const [loading, setLoading] = useState(true);
  const [clusterInfo, setClusterInfo] = useState<any>(null);
  const [emotionData, setEmotionData] = useState<any[]>([]);
  const [topKeywords, setTopKeywords] = useState<any[]>([]);

  useEffect(() => {
    loadAdvancedAnalytics();
  }, []);

  const loadAdvancedAnalytics = async () => {
    setLoading(true);
    try {
      // Load clustering info
      const clusterResponse = await fetch("/api/v1/clustering/info", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (clusterResponse.ok) {
        const clusterData = await clusterResponse.json();
        setClusterInfo(clusterData);
      }

      // Simulate emotion data (in real app, this would come from API)
      setEmotionData([
        { emotion: "joy", count: 8, percentage: 32 },
        { emotion: "neutral", count: 7, percentage: 28 },
        { emotion: "sadness", count: 4, percentage: 16 },
        { emotion: "anger", count: 3, percentage: 12 },
        { emotion: "surprise", count: 2, percentage: 8 },
        { emotion: "fear", count: 1, percentage: 4 },
      ]);

      // Simulate top keywords
      setTopKeywords([
        { keyword: "feature", count: 12 },
        { keyword: "support", count: 10 },
        { keyword: "pricing", count: 8 },
        { keyword: "bug", count: 7 },
        { keyword: "great", count: 6 },
        { keyword: "mobile", count: 5 },
        { keyword: "export", count: 4 },
        { keyword: "customer", count: 4 },
      ]);
    } catch (error) {
      console.error("Failed to load advanced analytics:", error);
    } finally {
      setLoading(false);
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

  // Prepare urgency data
  const urgencyData = Object.entries(dashboard.urgency_distribution || {}).map(
    ([key, value]) => ({
      name: key.split(".").pop() || key,
      value,
      color: URGENCY_COLORS[key.split(".").pop() || key] || "#757575",
    })
  );

  // Prepare cluster data
  const clusterData = clusterInfo?.clusters
    ? Object.entries(clusterInfo.clusters).map(([name, count]) => ({
        name: name.replace("cluster_", "Topic "),
        value: count,
      }))
    : [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Advanced Analytics
      </Typography>
      <Typography
        variant="body1"
        color="textSecondary"
        gutterBottom
        sx={{ mb: 3 }}
      >
        Deep insights into sentiment, emotions, topics, and trends
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Psychology color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Emotions Detected</Typography>
              </Box>
              <Typography variant="h3">{emotionData.length}</Typography>
              <Typography variant="body2" color="textSecondary">
                Different emotion types
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Category color="secondary" sx={{ mr: 1 }} />
                <Typography variant="h6">Topic Clusters</Typography>
              </Box>
              <Typography variant="h3">{clusterData.length}</Typography>
              <Typography variant="body2" color="textSecondary">
                Feedback grouped by similarity
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Speed color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">High Priority</Typography>
              </Box>
              <Typography variant="h3">
                {(dashboard.urgency_distribution as any)?.high || 0}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Urgent items requiring attention
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Group color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Analyzed</Typography>
              </Box>
              <Typography variant="h3">
                {clusterInfo?.total_feedback || dashboard.total_feedback}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total feedback items processed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Emotion Distribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Emotion Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={emotionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.emotion}: ${entry.count}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {emotionData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={EMOTION_COLORS[entry.emotion] || "#757575"}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Urgency Levels */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Urgency Levels
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={urgencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" name="Count">
                  {urgencyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Topic Clusters */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Topic Clusters
            </Typography>
            {clusterData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={clusterData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" width={100} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#2196f3" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Box textAlign="center" py={5}>
                <Typography color="textSecondary">
                  No clustering data available
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Top Keywords */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Top Keywords
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Keyword</TableCell>
                    <TableCell align="right">Frequency</TableCell>
                    <TableCell>Distribution</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {topKeywords.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Chip label={item.keyword} size="small" />
                      </TableCell>
                      <TableCell align="right">{item.count}</TableCell>
                      <TableCell>
                        <LinearProgress
                          variant="determinate"
                          value={(item.count / topKeywords[0].count) * 100}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Sentiment vs Urgency Radar */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Multi-Dimensional Analysis
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart
                data={[
                  {
                    metric: "Positive Sentiment",
                    value:
                      ((dashboard.sentiment_distribution as any)?.positive ||
                        0) / dashboard.total_feedback,
                    fullMark: 1,
                  },
                  {
                    metric: "Negative Sentiment",
                    value:
                      ((dashboard.sentiment_distribution as any)?.negative ||
                        0) / dashboard.total_feedback,
                    fullMark: 1,
                  },
                  {
                    metric: "Critical Urgency",
                    value:
                      ((dashboard.urgency_distribution as any)?.critical || 0) /
                      dashboard.total_feedback,
                    fullMark: 1,
                  },
                  {
                    metric: "Feature Requests",
                    value:
                      dashboard.feature_requests / dashboard.total_feedback,
                    fullMark: 1,
                  },
                  {
                    metric: "Bug Reports",
                    value: dashboard.bug_reports / dashboard.total_feedback,
                    fullMark: 1,
                  },
                ]}
              >
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis angle={90} domain={[0, 1]} />
                <Radar
                  name="Metrics"
                  dataKey="value"
                  stroke="#2196f3"
                  fill="#2196f3"
                  fillOpacity={0.6}
                />
                <Tooltip
                  formatter={(value: any) => `${(value * 100).toFixed(1)}%`}
                />
              </RadarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
