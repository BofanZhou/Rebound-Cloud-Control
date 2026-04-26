<template>
  <div v-if="show" class="modal-overlay" @click.self="closeOnOverlay && $emit('close')">
    <div class="modal-content" :style="{ maxWidth: maxWidth }">
      <h3 v-if="title">{{ title }}</h3>
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  show: boolean
  title?: string
  maxWidth?: string
  closeOnOverlay?: boolean
}>(), {
  maxWidth: '420px',
  closeOnOverlay: true,
})

defineEmits<{
  close: []
}>()
</script>
