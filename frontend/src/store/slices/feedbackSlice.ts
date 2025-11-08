import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface Feedback {
  id: string;
  text: string;
  sentiment: string;
  sentiment_score: number;
  emotion: string;
  urgency_level: string;
  urgency_score: number;
  priority_score: number;
  created_at: string;
  customer_name?: string;
  customer_email?: string;
  main_category?: string;
  keywords?: string[];
}

interface FeedbackState {
  items: Feedback[];
  selectedFeedback: Feedback | null;
  loading: boolean;
  total: number;
  filters: {
    sentiment?: string;
    urgency_level?: string;
    status?: string;
  };
}

const initialState: FeedbackState = {
  items: [],
  selectedFeedback: null,
  loading: false,
  total: 0,
  filters: {},
};

const feedbackSlice = createSlice({
  name: "feedback",
  initialState,
  reducers: {
    setFeedback: (state, action: PayloadAction<Feedback[]>) => {
      state.items = action.payload;
    },
    addFeedback: (state, action: PayloadAction<Feedback>) => {
      state.items.unshift(action.payload);
      state.total += 1;
    },
    updateFeedback: (state, action: PayloadAction<Feedback>) => {
      const index = state.items.findIndex((f) => f.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    },
    setSelectedFeedback: (state, action: PayloadAction<Feedback | null>) => {
      state.selectedFeedback = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setFilters: (state, action: PayloadAction<typeof initialState.filters>) => {
      state.filters = action.payload;
    },
    setTotal: (state, action: PayloadAction<number>) => {
      state.total = action.payload;
    },
  },
});

export const {
  setFeedback,
  addFeedback,
  updateFeedback,
  setSelectedFeedback,
  setLoading,
  setFilters,
  setTotal,
} = feedbackSlice.actions;

export default feedbackSlice.reducer;
