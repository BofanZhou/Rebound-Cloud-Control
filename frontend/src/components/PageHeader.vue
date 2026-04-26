<template>
  <div class="page-header">
    <h2 class="page-title">
      <span class="title-icon" v-html="icon"></span>
      {{ title }}
    </h2>
    <span class="page-subtitle">{{ subtitle }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle: string
  icon: string
}>()
</script>
