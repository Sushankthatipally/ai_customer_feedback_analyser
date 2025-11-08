import api from "./client";

// Auth API
export const authAPI = {
  login: (email: string, password: string) => {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);
    return api.post("/auth/login", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  register: (data: any) => api.post("/auth/register", data),
  getCurrentUser: () => api.get("/users/me"),
};

// Users API
export const usersAPI = {
  getCurrentUser: () => api.get("/users/me"),
  updateProfile: (data: any) => api.patch("/users/me", data),
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post("/users/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    }),
};

// Feedback API
export const feedbackAPI = {
  getAll: (params?: any) => api.get("/feedback/", { params }),
  getById: (id: string) => api.get(`/feedback/${id}`),
  create: (data: any) => api.post("/feedback/", data),
  update: (id: string, data: any) => api.patch(`/feedback/${id}`, data),
  delete: (id: string) => api.delete(`/feedback/${id}`),
  bulkUpload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/feedback/bulk", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  reanalyze: (id: string) => api.post(`/feedback/${id}/analyze`),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: (days?: number) =>
    api.get("/analytics/dashboard", { params: { days } }),
  getSentimentTrends: (days?: number) =>
    api.get("/analytics/trends/sentiment", { params: { days } }),
  getTopicDistribution: () => api.get("/analytics/topics/distribution"),
};

// Reports API
export const reportsAPI = {
  generate: (data: any) => api.post("/reports/generate", data),
  getExecutiveSummary: (days?: number) =>
    api.get("/reports/executive-summary", { params: { days } }),
};

// Integrations API
export const integrationsAPI = {
  syncZendesk: (config: any) => api.post("/integrations/zendesk/sync", config),
  syncIntercom: (config: any) =>
    api.post("/integrations/intercom/sync", config),
  notifySlack: (message: any) =>
    api.post("/integrations/slack/notify", message),
};

export default {
  auth: authAPI,
  users: usersAPI,
  feedback: feedbackAPI,
  analytics: analyticsAPI,
  reports: reportsAPI,
  integrations: integrationsAPI,
};
