import { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import {
  Typography,
  Box,
  Paper,
  Grid,
  Button,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Divider,
} from "@mui/material";
import {
  Download,
  TrendingUp,
  TrendingDown,
  Assessment,
  Schedule,
  CheckCircle,
} from "@mui/icons-material";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { RootState } from "../store";
import { feedbackAPI } from "../api";

export default function Reports() {
  const { dashboard } = useSelector((state: RootState) => state.analytics);
  const [loading, setLoading] = useState(true);
  const [topFeedback, setTopFeedback] = useState<any[]>([]);

  useEffect(() => {
    loadReportData();
  }, []);

  const loadReportData = async () => {
    setLoading(true);
    try {
      // Fetch top priority feedback
      const response = await feedbackAPI.getAll();
      const feedbacks = response.data;

      // Sort by priority score and take top 10
      const sorted = feedbacks
        .filter(
          (f: any) =>
            f.priority_score !== null && f.priority_score !== undefined
        )
        .sort((a: any, b: any) => b.priority_score - a.priority_score)
        .slice(0, 10);

      console.log("Total feedbacks:", feedbacks.length);
      console.log("Feedbacks with priority_score:", sorted.length);
      console.log("Sample feedback:", sorted[0]);

      setTopFeedback(sorted);
    } catch (error) {
      console.error("Failed to load report data:", error);
    } finally {
      setLoading(false);
    }
  };

  const generatePDFReport = () => {
    alert(
      "PDF report generation would be implemented here. This would include all analytics, charts, and insights."
    );
  };

  const generateCSVExport = () => {
    alert(
      "CSV export would be implemented here. This would export all feedback data with analysis results."
    );
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

  // Prepare trend analysis
  const sentimentTrend = dashboard.sentiment_trend || [];
  const latestDay = sentimentTrend[sentimentTrend.length - 1];
  const previousDay = sentimentTrend[sentimentTrend.length - 2];

  const sentimentChange =
    latestDay && previousDay
      ? ((latestDay.positive - previousDay.positive) /
          (previousDay.positive || 1)) *
        100
      : 0;

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
            Reports & Insights
          </Typography>
          <Typography variant="body1" color="textSecondary">
            AI-generated insights and exportable reports
          </Typography>
        </Box>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={generateCSVExport}
            sx={{ mr: 2 }}
          >
            Export CSV
          </Button>
          <Button
            variant="contained"
            startIcon={<Assessment />}
            onClick={generatePDFReport}
          >
            Generate PDF Report
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Analyzed
              </Typography>
              <Typography variant="h4">{dashboard.total_feedback}</Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <CheckCircle color="success" fontSize="small" />
                <Typography variant="body2" color="success.main" ml={0.5}>
                  100% Complete
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Sentiment Trend
              </Typography>
              <Typography variant="h4">
                {sentimentChange > 0 ? "+" : ""}
                {sentimentChange.toFixed(1)}%
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                {sentimentChange >= 0 ? (
                  <TrendingUp color="success" fontSize="small" />
                ) : (
                  <TrendingDown color="error" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={sentimentChange >= 0 ? "success.main" : "error.main"}
                  ml={0.5}
                >
                  vs Yesterday
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Critical Issues
              </Typography>
              <Typography variant="h4">
                {(dashboard.urgency_distribution as any)?.critical || 0}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <Schedule color="error" fontSize="small" />
                <Typography variant="body2" color="error.main" ml={0.5}>
                  Needs Attention
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Action Items
              </Typography>
              <Typography variant="h4">
                {dashboard.feature_requests + dashboard.bug_reports}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <Typography variant="body2" color="textSecondary">
                  {dashboard.feature_requests} Features +{" "}
                  {dashboard.bug_reports} Bugs
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Key Insights */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Key Insights
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box>
              <Box mb={2}>
                <Typography variant="subtitle2" color="primary" gutterBottom>
                  📊 Sentiment Overview
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {(
                    ((dashboard.sentiment_distribution as any)?.positive /
                      dashboard.total_feedback) *
                    100
                  ).toFixed(1)}
                  % of feedback is positive, with an average sentiment score of{" "}
                  {dashboard.avg_sentiment.toFixed(2)}.
                  {dashboard.avg_sentiment > 0
                    ? " Overall customer satisfaction is good."
                    : " There's room for improvement in customer satisfaction."}
                </Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="subtitle2" color="error" gutterBottom>
                  🚨 Urgent Matters
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {(dashboard.urgency_distribution as any)?.critical || 0}{" "}
                  critical issues identified.
                  {(dashboard.urgency_distribution as any)?.high || 0}{" "}
                  high-priority items also require attention. Immediate action
                  recommended for critical items.
                </Typography>
              </Box>

              <Box mb={2}>
                <Typography
                  variant="subtitle2"
                  color="success.main"
                  gutterBottom
                >
                  💡 Feature Requests
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboard.feature_requests} feature requests detected. This
                  represents{" "}
                  {(
                    (dashboard.feature_requests / dashboard.total_feedback) *
                    100
                  ).toFixed(1)}
                  % of all feedback, indicating active user engagement and
                  product interest.
                </Typography>
              </Box>

              <Box>
                <Typography
                  variant="subtitle2"
                  color="warning.main"
                  gutterBottom
                >
                  🐛 Bug Reports
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {dashboard.bug_reports} bug reports identified.
                  {dashboard.bug_reports > 5
                    ? " Consider prioritizing bug fixes to improve user experience."
                    : " Bug count is manageable and within normal range."}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Sentiment Distribution Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Sentiment Breakdown
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart
                data={[
                  {
                    name: "Positive",
                    count:
                      (dashboard.sentiment_distribution as any)?.positive || 0,
                    percentage: (
                      ((dashboard.sentiment_distribution as any)?.positive /
                        dashboard.total_feedback) *
                      100
                    ).toFixed(1),
                  },
                  {
                    name: "Neutral",
                    count:
                      (dashboard.sentiment_distribution as any)?.neutral || 0,
                    percentage: (
                      ((dashboard.sentiment_distribution as any)?.neutral /
                        dashboard.total_feedback) *
                      100
                    ).toFixed(1),
                  },
                  {
                    name: "Negative",
                    count:
                      (dashboard.sentiment_distribution as any)?.negative || 0,
                    percentage: (
                      ((dashboard.sentiment_distribution as any)?.negative /
                        dashboard.total_feedback) *
                      100
                    ).toFixed(1),
                  },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#2196f3" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Top Priority Feedback */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Top Priority Feedback (Highest to Lowest)
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Priority</TableCell>
                    <TableCell>Feedback Text</TableCell>
                    <TableCell>Sentiment</TableCell>
                    <TableCell>Urgency</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {topFeedback.map((feedback, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Chip
                          label={`${
                            feedback.priority_score?.toFixed(0) || 0
                          }/100`}
                          color={
                            feedback.priority_score > 70
                              ? "error"
                              : feedback.priority_score > 40
                              ? "warning"
                              : "default"
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ maxWidth: 400 }}>
                        {feedback.text?.substring(0, 100)}...
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={feedback.sentiment || "N/A"}
                          color={
                            feedback.sentiment === "positive"
                              ? "success"
                              : feedback.sentiment === "negative"
                              ? "error"
                              : "default"
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={
                            feedback.urgency_level?.split(".").pop() || "N/A"
                          }
                          color={
                            feedback.urgency_level?.includes("critical")
                              ? "error"
                              : feedback.urgency_level?.includes("high")
                              ? "warning"
                              : "default"
                          }
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {feedback.is_bug_report && (
                          <Chip
                            label="Bug"
                            color="error"
                            size="small"
                            sx={{ mr: 0.5 }}
                          />
                        )}
                        {feedback.is_feature_request && (
                          <Chip label="Feature" color="info" size="small" />
                        )}
                      </TableCell>
                      <TableCell>
                        {new Date(feedback.created_at).toLocaleDateString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12}>
          <Paper
            sx={{ p: 3, bgcolor: "info.light", color: "info.contrastText" }}
          >
            <Typography variant="h6" gutterBottom>
              📋 AI Recommendations
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" gutterBottom>
                  Immediate Actions
                </Typography>
                <Typography variant="body2">
                  • Address{" "}
                  {(dashboard.urgency_distribution as any)?.critical || 0}{" "}
                  critical issues
                  <br />• Review {dashboard.bug_reports} bug reports
                  <br />• Respond to negative feedback
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" gutterBottom>
                  Short-term Goals
                </Typography>
                <Typography variant="body2">
                  • Evaluate {dashboard.feature_requests} feature requests
                  <br />
                  • Improve response time for high-priority items
                  <br />• Monitor sentiment trends
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" gutterBottom>
                  Long-term Strategy
                </Typography>
                <Typography variant="body2">
                  • Build features from top requests
                  <br />
                  • Reduce bug report frequency
                  <br />• Increase positive sentiment ratio
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
