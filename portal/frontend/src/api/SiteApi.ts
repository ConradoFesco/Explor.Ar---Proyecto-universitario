// portal/frontend/src/apis/siteApi.ts
import axios from "axios";

const API_BASE = "http://localhost:5000/api";
// Ajustalo si tu backend inicia con /api o no

export const siteApi = {
  async getBestRated() {
    return axios.get(`${API_BASE}/sites`, {
      params: { order_by: "rating", per_page: 10 }
    }).then(res => res.data);
  },

  async getMostVisited() {
    return axios.get(`${API_BASE}/sites`, {
      params: { order_by: "visits", per_page: 10 }
    }).then(res => res.data);
  },

  async getRecentlyAdded() {
    return axios.get(`${API_BASE}/sites`, {
      params: { order_by: "created_at", per_page: 10 }
    }).then(res => res.data);
  }
};
