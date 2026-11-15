
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

export const getDashboardStats = async () => {
  const response = await api.get("/api/dashboard/stats");
  return response.data;
};

export const getCalls = async ({
  limit = 10,
  offset = 0,
  status = "",
  language = "",
  search = "",
  sort = "newest",
} = {}) => {
  const response = await api.get("/api/calls", {
    params: {
      limit,
      offset,
      status: status || undefined,
      language: language || undefined,
      search: search.trim() || undefined,
      sort,
    },
  });

  return response.data;
};

export const getBackendHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};


export const getCallHistory = async (callId) => {
  const response = await api.get(
    `/api/calls/${encodeURIComponent(callId)}/history`
  );

  return response.data;
};


export const getDashboardAnalytics = async () => {
  const response = await api.get("/api/dashboard/analytics");
  return response.data;
};

export default api;
