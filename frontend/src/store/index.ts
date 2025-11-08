import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";
import feedbackReducer from "./slices/feedbackSlice";
import analyticsReducer from "./slices/analyticsSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    feedback: feedbackReducer,
    analytics: analyticsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
