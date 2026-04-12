<template>
  <div class="app-shell">
    <template v-if="!isLoginPage">
      <header class="topbar">
        <div class="topbar-inner">
          <div class="brand">
            <div class="brand-mark" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>
            <div class="brand-text">
              <span class="brand-title">Rebound Cloud Control</span>
              <span class="brand-sub">{{ currentMachineName }}</span>
            </div>
          </div>

          <nav class="primary-nav">
            <router-link
              v-for="item in menuItems"
              :key="item.key"
              :to="item.path"
              :class="['nav-chip', { active: $route.name === item.key }]"
            >
              <span class="chip-icon" v-html="item.icon"></span>
              <span class="chip-label">{{ item.label }}</span>
            </router-link>
          </nav>

          <div class="account-panel">
            <span v-if="userRole" class="role-badge" :class="userRole">{{ roleLabel }}</span>
            <span class="account-name">{{ displayName }}</span>

            <button
              v-if="!isMachineLogin && isLoggedIn"
              class="icon-btn switch-btn"
              @click="switchMachine"
              title="Switch machine"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
            </button>

            <button class="icon-btn danger logout-btn" @click="handleLogout" title="Logout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
            </button>
          </div>
        </div>
      </header>

      <main class="app-main">
        <router-view />
      </main>

      <footer class="status-footer">
        <div class="status-inner">
          <div class="status-left">
            <span class="status-pulse"></span>
            <span>System Online</span>
          </div>
          <div class="status-center">Prototype v2.1 | Multi-Machine Mode</div>
          <div class="status-right">{{ authMode }}</div>
        </div>
      </footer>
    </template>

    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isLoginPage = computed(() => route.name === 'login')
const isLoggedIn = computed(() => authStore.isLoggedIn)
const isMachineLogin = computed(() => authStore.isMachineLogin)
const userRole = computed(() => authStore.userRole)
const displayName = computed(() => authStore.displayName)

const currentMachineName = computed(() => authStore.currentMachine?.name || 'Industrial Control Interface')

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    admin: 'ADMIN',
    maintenance: 'MAINT',
    operator: 'OP',
    machine: 'MACHINE',
  }
  return labels[userRole.value || ''] || 'USER'
})

const authMode = computed(() => (isMachineLogin.value ? 'Machine Login' : 'User Login'))

const menuItems = [
  {
    key: 'dashboard',
    label: 'Dashboard',
    path: '/',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
  },
  {
    key: 'device',
    label: 'Device',
    path: '/device',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>',
  },
  {
    key: 'history',
    label: 'History',
    path: '/history',
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
  },
]

function switchMachine() {
  router.push('/machines')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
:root {
  --industrial-bg: #f2f5f9;
  --industrial-bg-secondary: #ffffff;
  --industrial-bg-card: #ffffff;

  --metal-dark: #e8edf3;
  --metal-mid: #d9e1ea;
  --metal-light: #c8d2de;
  --metal-bright: #8b99aa;

  --industrial-yellow: #f59e0b;
  --industrial-yellow-glow: rgba(245, 158, 11, 0.28);
  --industrial-orange: #f97316;
  --industrial-red: #dc2626;
  --industrial-green: #16a34a;
  --industrial-green-glow: rgba(22, 163, 74, 0.3);
  --industrial-blue: #0ea5e9;
  --industrial-blue-glow: rgba(14, 165, 233, 0.28);

  --text-primary: #0f172a;
  --text-secondary: #334155;
  --text-muted: #64748b;

  --border-color: #d9e1ea;
  --border-bright: #b8c4d3;

  --font-display: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
  --font-body: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-body);
  color: var(--text-primary);
  background:
    radial-gradient(circle at 10% 10%, rgba(14, 165, 233, 0.1), transparent 40%),
    radial-gradient(circle at 90% 10%, rgba(245, 158, 11, 0.12), transparent 45%),
    linear-gradient(180deg, #f8fafc 0%, #eef3f8 100%);
  min-height: 100vh;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(185, 197, 212, 0.7);
}

.topbar-inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: 12px 24px;
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  gap: 12px;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%);
  box-shadow: 0 10px 24px rgba(14, 165, 233, 0.3);
}

.brand-mark svg {
  width: 24px;
  height: 24px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.brand-sub {
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-display);
}

.primary-nav {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.nav-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  text-decoration: none;
  color: var(--text-secondary);
  border: 1px solid transparent;
  transition: 0.22s ease;
}

.nav-chip:hover {
  background: rgba(14, 165, 233, 0.1);
  color: #0369a1;
}

.nav-chip.active {
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 10px 20px rgba(2, 132, 199, 0.25);
}

.chip-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chip-icon svg {
  width: 100%;
  height: 100%;
}

.chip-label {
  font-size: 13px;
  font-weight: 600;
}

.account-panel {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}

.role-badge {
  border-radius: 999px;
  padding: 3px 9px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.6px;
}

.role-badge.admin {
  background: rgba(245, 158, 11, 0.14);
  color: #92400e;
}

.role-badge.maintenance {
  background: rgba(14, 165, 233, 0.12);
  color: #075985;
}

.role-badge.operator {
  background: rgba(22, 163, 74, 0.12);
  color: #166534;
}

.role-badge.machine {
  background: rgba(51, 65, 85, 0.12);
  color: #334155;
}

.account-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  background: #fff;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: 0.24s ease;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.06);
  color: #1f2937;
}

.icon-btn:hover {
  border-color: #7dd3fc;
  color: #0369a1;
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 12px 22px rgba(14, 165, 233, 0.2);
}

.icon-btn.danger:hover {
  border-color: #fca5a5;
  color: #b91c1c;
  box-shadow: 0 12px 20px rgba(220, 38, 38, 0.18);
}

.icon-btn svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2.2;
  stroke-linecap: round;
  stroke-linejoin: round;
  position: relative;
  z-index: 1;
  opacity: 0.35;
}

.switch-btn::after,
.logout-btn::after {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
  line-height: 1;
  z-index: 2;
  pointer-events: none;
}

.switch-btn::after {
  content: '⇄';
  color: #0f172a;
}

.logout-btn::after {
  content: '⎋';
  color: #b91c1c;
}

.icon-btn.danger {
  border-color: #fecaca;
  color: #b91c1c;
  background: linear-gradient(180deg, #fff 0%, #fff5f5 100%);
}

.icon-btn.danger:hover {
  background: linear-gradient(180deg, #fff 0%, #ffe8e8 100%);
}

.app-main {
  flex: 1;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px;
}

.status-footer {
  border-top: 1px solid rgba(185, 197, 212, 0.7);
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(10px);
}

.status-inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: 10px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-muted);
  font-family: var(--font-display);
  font-size: 11px;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #166534;
}

.status-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
  animation: pulse 1.8s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.35);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
  }
}

.card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.9));
  border: 1px solid rgba(185, 197, 212, 0.72);
  border-radius: 18px;
  padding: 22px;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.07);
  position: relative;
  transition: transform 0.26s ease, box-shadow 0.26s ease;
}

.card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 18px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.18), rgba(245, 158, 11, 0.18));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.card h3 {
  margin-bottom: 14px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.6px;
  color: #0f172a;
  text-transform: uppercase;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 22px 42px rgba(15, 23, 42, 0.1);
}

.form-item label {
  color: #475569;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 7px;
}

.form-item input,
.form-item select {
  width: 100%;
  background: #fff;
  border: 1px solid #d7e0ea;
  border-radius: 12px;
  color: #0f172a;
  padding: 11px 12px;
  transition: 0.2s ease;
}

.form-item input:focus,
.form-item select:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.18);
}

button {
  border-radius: 12px;
  border: 1px solid #d7e0ea;
  background: #fff;
  color: #1e293b;
  font-weight: 600;
  padding: 10px 16px;
  transition: transform 0.22s ease, box-shadow 0.22s ease, filter 0.22s ease;
  position: relative;
  overflow: hidden;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.09);
  filter: saturate(1.08);
}

button:active:not(:disabled) {
  transform: translateY(0);
}

button:focus-visible {
  outline: 0;
  box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.2);
}

.btn-primary {
  border: 0;
  color: #fff;
  background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 12px 26px rgba(14, 165, 233, 0.35);
}

.btn-primary::before,
.btn-danger::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(112deg, transparent 0%, rgba(255,255,255,0.34) 50%, transparent 100%);
  transform: translateX(-130%);
  transition: transform 0.45s ease;
}

.btn-primary:hover::before,
.btn-danger:hover::before {
  transform: translateX(130%);
}

.btn-danger {
  background: #fff;
  border-color: #fecaca;
  color: #b91c1c;
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-icon svg,
.title-icon svg,
.chip-icon svg {
  stroke-linecap: round;
  stroke-linejoin: round;
}

.tag {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
}

@media (max-width: 1200px) {
  .topbar-inner {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .primary-nav {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .account-panel {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .app-main {
    padding: 16px;
  }

  .chip-label,
  .account-name,
  .status-center {
    display: none;
  }

  .primary-nav {
    gap: 6px;
  }

  .nav-chip {
    padding: 8px;
  }

  .status-inner {
    justify-content: space-between;
  }
}
</style>
