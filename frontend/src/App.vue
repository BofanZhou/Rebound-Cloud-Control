<template>
  <div class="app-shell">
    <template v-if="!isBareLayout">
      <header class="topbar">
        <div class="topbar-inner">
          <div class="brand">
            <div class="brand-mark" aria-hidden="true">
              <svg viewBox="-2 -4 77 71" width="36" height="32">
                <rect x="0" y="0" width="32" height="32" rx="1.5" ry="1.5" fill="#0B1D33"/>
                <g transform="rotate(6 54.585 14.415)"><rect x="38.585" y="-1.585" width="32" height="32" rx="1.5" ry="1.5" fill="#1A6DFF"/></g>
                <rect x="0" y="35" width="32" height="32" rx="1.5" ry="1.5" fill="#0B1D33"/>
                <rect x="37" y="35" width="32" height="32" rx="1.5" ry="1.5" fill="#6B7280"/>
              </svg>
            </div>
            <div class="brand-text">
              <span class="brand-title">ZIKOI</span>
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

    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import ToastContainer from './components/ToastContainer.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isBareLayout = computed(() => route.name === 'login' || !!route.meta.bareLayout)
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

const menuItems = computed(() => {
  const items = [
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
    {
      key: 'training',
      label: 'Training',
      path: '/training',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',
    },
  ]
  if (authStore.userRole === 'admin') {
    items.push({
      key: 'users',
      label: 'Users',
      path: '/users',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    })
    items.push({
      key: 'logs',
      label: 'Logs',
      path: '/logs',
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    })
  }
  return items
})

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
  --color-primary: #0071e3;
  --color-primary-light: #2997ff;
  --color-primary-glow: rgba(0, 113, 227, 0.18);
  --color-success: #248a3d;
  --color-success-light: #30d158;
  --color-success-glow: rgba(36, 138, 61, 0.16);
  --color-warning: #b76e00;
  --color-warning-glow: rgba(183, 110, 0, 0.14);
  --color-danger: #d70015;
  --color-danger-light: #ff453a;

  --industrial-bg: #f5f5f7;
  --industrial-bg-secondary: #fbfbfd;
  --industrial-bg-card: rgba(255, 255, 255, 0.86);

  --metal-dark: #eef1f5;
  --metal-mid: #e5e8ee;
  --metal-light: #f5f5f7;
  --metal-bright: #c7c7cc;

  --industrial-blue: var(--color-primary);
  --industrial-blue-glow: var(--color-primary-glow);
  --industrial-green: var(--color-success);
  --industrial-green-glow: var(--color-success-glow);
  --industrial-red: var(--color-danger);
  --industrial-amber: var(--color-warning);
  --industrial-amber-glow: var(--color-warning-glow);
  --industrial-yellow: var(--color-primary);
  --industrial-yellow-glow: var(--color-primary-glow);

  --input-border: rgba(60, 60, 67, 0.16);
  --surface-line: rgba(60, 60, 67, 0.12);

  --text-primary: #1d1d1f;
  --text-secondary: #3a3a3c;
  --text-muted: #86868b;

  --border-color: rgba(60, 60, 67, 0.12);
  --border-bright: rgba(0, 113, 227, 0.28);

  --font-display: 'SF Mono', 'Cascadia Mono', 'Consolas', monospace;
  --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  min-height: 100vh;
  background:
    linear-gradient(180deg, #fbfbfd 0%, #f5f5f7 48%, #eef2f7 100%);
  color: var(--text-primary);
  font-family: var(--font-body);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
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
  border-bottom: 1px solid rgba(60, 60, 67, 0.10);
  background: rgba(251, 251, 253, 0.78);
  backdrop-filter: saturate(180%) blur(24px);
}

.topbar-inner {
  max-width: 1360px;
  margin: 0 auto;
  padding: 12px 28px;
  display: grid;
  grid-template-columns: minmax(220px, 1fr) auto minmax(220px, 1fr);
  gap: 20px;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border: 1px solid rgba(60, 60, 67, 0.10);
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.08);
}

.brand-mark svg {
  width: 25px;
  height: 25px;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.brand-title {
  font-size: 15px;
  font-weight: 700;
  line-height: 1.15;
}

.brand-sub {
  max-width: 260px;
  overflow: hidden;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.primary-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 4px;
  border: 1px solid rgba(60, 60, 67, 0.10);
  border-radius: 999px;
  background: rgba(118, 118, 128, 0.08);
}

.nav-chip {
  min-height: 34px;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 12px;
  border: 0;
  border-radius: 999px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  line-height: 1;
  text-decoration: none;
  transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

.nav-chip:hover {
  background: rgba(255, 255, 255, 0.72);
  color: var(--text-primary);
}

.nav-chip.active {
  background: #fff;
  color: var(--color-primary);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.chip-icon {
  width: 15px;
  height: 15px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.chip-icon svg {
  width: 100%;
  height: 100%;
  stroke-linecap: round;
  stroke-linejoin: round;
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
  padding: 4px 9px;
  background: rgba(118, 118, 128, 0.10);
  color: var(--text-secondary);
  font-size: 11px;
  font-weight: 700;
}

.role-badge.admin { color: var(--color-danger); }
.role-badge.maintenance { color: var(--color-warning); }
.role-badge.operator { color: var(--color-success); }
.role-badge.machine { color: var(--color-primary); }

.account-name {
  max-width: 160px;
  overflow: hidden;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.icon-btn {
  width: 34px;
  height: 34px;
  padding: 0;
  border: 1px solid rgba(60, 60, 67, 0.14);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.86);
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

.icon-btn:hover {
  background: #fff;
  border-color: rgba(0, 113, 227, 0.32);
  color: var(--color-primary);
  transform: translateY(-1px);
}

.icon-btn.danger {
  color: var(--color-danger);
}

.icon-btn svg {
  width: 16px;
  height: 16px;
  stroke: currentColor;
  fill: none;
  stroke-width: 2.1;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.app-main {
  flex: 1;
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  padding: 32px 28px 36px;
}

.status-footer {
  border-top: 1px solid rgba(60, 60, 67, 0.10);
  background: rgba(251, 251, 253, 0.78);
  backdrop-filter: saturate(180%) blur(18px);
}

.status-inner {
  max-width: 1360px;
  margin: 0 auto;
  padding: 10px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-muted);
  font-size: 12px;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-success);
  font-weight: 600;
}

.status-pulse {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-success-light);
}

.card {
  position: relative;
  border: 1px solid rgba(60, 60, 67, 0.10);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.05);
  padding: 24px;
  backdrop-filter: blur(20px);
}

.card h3 {
  margin-bottom: 18px;
  color: var(--text-primary);
  font-size: 17px;
  font-weight: 700;
  line-height: 1.25;
}

.form-item label {
  display: block;
  margin-bottom: 7px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 600;
}

.form-item input,
.form-item select,
input,
select {
  border: 1px solid var(--input-border);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.92);
  color: var(--text-primary);
  font: inherit;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.form-item input,
.form-item select {
  width: 100%;
  padding: 11px 12px;
  font-size: 14px;
}

.form-item input:focus,
.form-item select:focus,
input:focus,
select:focus {
  outline: none;
  border-color: rgba(0, 113, 227, 0.52);
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.12);
  background: #fff;
}

button {
  min-height: 38px;
  border: 1px solid rgba(60, 60, 67, 0.14);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--text-primary);
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  font-weight: 600;
  padding: 9px 16px;
  transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

button:hover:not(:disabled) {
  background: #fff;
  border-color: rgba(0, 113, 227, 0.26);
  transform: translateY(-1px);
}

button:active:not(:disabled) {
  transform: translateY(0);
}

button:focus-visible {
  outline: 0;
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.15);
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.48;
}

.btn-primary {
  border: 0;
  background: var(--color-primary);
  color: #fff;
  box-shadow: 0 10px 24px rgba(0, 113, 227, 0.20);
}

.btn-primary:hover:not(:disabled) {
  background: #0077ed;
  box-shadow: 0 14px 28px rgba(0, 113, 227, 0.24);
}

.btn-secondary {
  background: rgba(118, 118, 128, 0.10);
  color: var(--text-primary);
}

.btn-danger {
  color: var(--color-danger);
}

.btn-icon,
.title-icon svg,
.chip-icon svg {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.tag {
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
}

@media (max-width: 1180px) {
  .topbar-inner {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .primary-nav {
    justify-content: flex-start;
    overflow-x: auto;
  }

  .account-panel {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .topbar-inner {
    padding: 10px 16px;
    gap: 10px;
  }

  .app-main {
    padding: 20px 16px 28px;
  }

  .chip-label,
  .account-name,
  .status-center {
    display: none;
  }

  .nav-chip {
    padding: 8px 10px;
  }

  .status-inner {
    padding: 10px 16px;
  }
}

@media (max-width: 640px) {
  .topbar {
    position: sticky;
  }

  .topbar-inner {
    padding: 10px 12px 8px;
  }

  .brand {
    gap: 10px;
  }

  .brand-mark {
    width: 34px;
    height: 34px;
    border-radius: 10px;
  }

  .brand-mark svg {
    width: 23px;
    height: 23px;
  }

  .brand-title {
    font-size: 14px;
  }

  .brand-sub {
    max-width: 210px;
    font-size: 11px;
  }

  .primary-nav {
    width: 100%;
    justify-content: flex-start;
    overflow-x: auto;
    overscroll-behavior-x: contain;
    scrollbar-width: none;
    scroll-snap-type: x proximity;
  }

  .primary-nav::-webkit-scrollbar {
    display: none;
  }

  .nav-chip {
    min-width: 42px;
    flex: 0 0 auto;
    scroll-snap-align: start;
  }

  .chip-icon {
    width: 17px;
    height: 17px;
  }

  .account-panel {
    width: 100%;
    justify-content: space-between;
  }

  .role-badge {
    padding: 4px 8px;
  }

  .app-main {
    padding: 18px 12px 28px;
  }

  .card {
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 12px 34px rgba(0, 0, 0, 0.05);
  }

  .card h3 {
    margin-bottom: 14px;
    font-size: 16px;
  }

  button {
    min-height: 42px;
    padding: 10px 14px;
  }

  .form-item input,
  .form-item select,
  input,
  select {
    min-height: 44px;
    font-size: 16px;
  }

  .status-footer {
    display: none;
  }
}
</style>
