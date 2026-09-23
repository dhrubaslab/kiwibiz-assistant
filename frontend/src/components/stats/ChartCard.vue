<template>
  <div class="chart-card">
    <h3 class="chart-card__title">{{ title }}</h3>
    <p v-if="subtitle" class="chart-card__subtitle">{{ subtitle }}</p>
    <div class="chart-card__body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
});
</script>

<style scoped>
.chart-card {
  background: var(--color-paper, #f7f5f0);
  border: 1px solid var(--color-sand, #dcd6c9);
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.chart-card__title {
  font-family: var(--font-display, 'Fraunces', serif);
  font-size: 1.05rem;
  color: var(--color-pine, #0f1e1c);
  margin: 0;
}

.chart-card__subtitle {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.8rem;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.6;
  margin: 0.2rem 0 0;
}

.chart-card__body {
  margin-top: 1rem;
  position: relative;
  height: 16rem;
}
</style>