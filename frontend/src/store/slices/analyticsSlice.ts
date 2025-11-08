import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface SentimentTrend {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
  avg_score: number;
}

interface TopicDistribution {
  topic: string;
  count: number;
  percentage: number;
  avg_sentiment: number;
}

interface DashboardStats {
  total_feedback: number;
  avg_sentiment: number;
  sentiment_distribution: Record<string, number>;
  urgency_distribution: Record<string, number>;
  top_topics: TopicDistribution[];
  sentiment_trend: SentimentTrend[];
  feature_requests: number;
  bug_reports: number;
}

interface AnalyticsState {
  dashboard: DashboardStats | null;
  loading: boolean;
  dateRange: {
    start: Date;
    end: Date;
  };
}

const initialState: AnalyticsState = {
  dashboard: null,
  loading: false,
  dateRange: {
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    end: new Date(),
  },
};

const analyticsSlice = createSlice({
  name: "analytics",
  initialState,
  reducers: {
    setDashboardStats: (state, action: PayloadAction<DashboardStats>) => {
      state.dashboard = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setDateRange: (
      state,
      action: PayloadAction<{ start: Date; end: Date }>
    ) => {
      state.dateRange = action.payload;
    },
  },
});

export const { setDashboardStats, setLoading, setDateRange } =
  analyticsSlice.actions;
export default analyticsSlice.reducer;
