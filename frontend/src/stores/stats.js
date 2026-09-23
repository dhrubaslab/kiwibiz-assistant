import { defineStore } from 'pinia';
import request from '../api/client';

export const useStatsStore = defineStore('stats', {
  state: () => ({
    isLoading: false,
    categoryLabels: [],
    categoryCounts: [],
    uploadDates: [],
    uploadCounts: [],
    qaDates: [],
    qaCounts: [],
  }),
  actions: {
    async fetchStats() {
      this.isLoading = true;
      try {
        const data = await request('/api/stats/dashboard', { method: 'GET', auth: true });
        this.categoryLabels = data.by_category.map((c) => c.category);
        this.categoryCounts = data.by_category.map((c) => c.count);
        this.uploadDates = data.upload_activity.map((d) => d.date);
        this.uploadCounts = data.upload_activity.map((d) => d.count);
        this.qaDates = data.qa_usage.map((d) => d.date);
        this.qaCounts = data.qa_usage.map((d) => d.count);
      } finally {
        this.isLoading = false;
      }
    },
  },
}); 