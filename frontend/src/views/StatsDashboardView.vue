<template>
  <AppShell>
    <div class="stats-page">
      <header class="stats-page__header">
        <h1 class="stats-page__title">Usage overview</h1>
        <p class="stats-page__subtitle">Documents, uploads, and Q&A activity for your company</p>
      </header>

      <div v-if="statsStore.isLoading" class="stats-page__loading">Loading stats…</div>

      <div v-else class="stats-page__grid">
        <ChartCard title="Documents by category">
          <Bar :data="categoryChartData" :options="barOptions" />
        </ChartCard>

        <ChartCard title="Upload activity" subtitle="Last 30 days">
          <Line :data="uploadChartData" :options="lineOptions" />
        </ChartCard>

        <ChartCard title="Q&A usage" subtitle="Questions asked per day">
          <Line :data="qaChartData" :options="lineOptions" />
        </ChartCard>
      </div>
    </div>
  </AppShell>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { Bar, Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';
import AppShell from '@/layouts/AppShell.vue';
import ChartCard from '../components/stats/ChartCard.vue';
import { useStatsStore } from '../stores/stats';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Tooltip, Legend);

const statsStore = useStatsStore();

onMounted(() => {
  statsStore.fetchStats();
});

// Design-system colours for chart series
const TEAL = '#1b6f63';
const AMBER = '#e8a33d';

const categoryChartData = computed(() => ({
  labels: statsStore.categoryLabels,
  datasets: [
    {
      label: 'Documents',
      data: statsStore.categoryCounts,
      backgroundColor: TEAL,
      borderRadius: 4,
    },
  ],
}));

const uploadChartData = computed(() => ({
  labels: statsStore.uploadDates,
  datasets: [
    {
      label: 'Uploads',
      data: statsStore.uploadCounts,
      borderColor: TEAL,
      backgroundColor: 'transparent',
      tension: 0.3,
    },
  ],
}));

const qaChartData = computed(() => ({
  labels: statsStore.qaDates,
  datasets: [
    {
      label: 'Questions asked',
      data: statsStore.qaCounts,
      borderColor: AMBER,
      backgroundColor: 'transparent',
      tension: 0.3,
    },
  ],
}));

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
};

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
};
</script>

<style scoped>
.stats-page {
  padding: 1.5rem;
}

.stats-page__title {
  font-family: var(--font-display, 'Fraunces', serif);
  font-size: 1.6rem;
  color: var(--color-pine, #0f1e1c);
  margin: 0;
}

.stats-page__subtitle {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.9rem;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.6;
  margin: 0.25rem 0 1.5rem;
}

.stats-page__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr));
  gap: 1.25rem;
}

.stats-page__loading {
  font-family: var(--font-body, 'Inter', sans-serif);
  color: var(--color-pine, #0f1e1c);
  opacity: 0.6;
}
</style>