<template>
  <div class="user-management">
    <PageHeader
      title="用户管理"
      subtitle="USER MANAGEMENT"
      :icon="pageIcon"
    />

    <div class="toolbar">
      <button class="btn-primary" @click="showCreateModal = true">
        <span class="btn-icon">+</span>
        新建用户
      </button>
      <button class="btn-secondary" @click="fetchUsers">
        <span class="btn-icon">↻</span>
        刷新
      </button>
    </div>

    <div class="card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="users.length === 0" class="empty">
        暂无用户数据
      </div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>用户名</th>
            <th>姓名</th>
            <th>角色</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.username">
            <td>{{ user.username }}</td>
            <td>{{ user.name }}</td>
            <td>
              <span class="role-badge" :class="user.role">
                {{ roleLabels[user.role] || user.role }}
              </span>
            </td>
            <td>
              <button class="btn-text" @click="openPasswordModal(user)">修改密码</button>
              <button
                v-if="user.username !== currentUsername"
                class="btn-text danger"
                @click="handleDelete(user)"
              >删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 创建用户弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h3>新建用户</h3>
        <form @submit.prevent="handleCreate">
          <div class="form-item">
            <label>用户名</label>
            <input v-model="createForm.username" required minlength="2" />
          </div>
          <div class="form-item">
            <label>姓名</label>
            <input v-model="createForm.name" required />
          </div>
          <div class="form-item">
            <label>角色</label>
            <select v-model="createForm.role" required>
              <option value="admin">管理员</option>
              <option value="maintenance">维修人员</option>
              <option value="operator">操作员</option>
            </select>
          </div>
          <div class="form-item">
            <label>密码</label>
            <input v-model="createForm.password" type="password" required minlength="4" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="showCreateModal = false">取消</button>
            <button type="submit" class="btn-primary" :disabled="creating">{{ creating ? '创建中...' : '创建' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
      <div class="modal">
        <h3>修改密码 - {{ passwordTarget?.name }}</h3>
        <form @submit.prevent="handlePasswordChange">
          <div class="form-item">
            <label>新密码</label>
            <input v-model="passwordForm.newPassword" type="password" required minlength="4" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="showPasswordModal = false">取消</button>
            <button type="submit" class="btn-primary" :disabled="updatingPassword">{{ updatingPassword ? '修改中...' : '确认修改' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { UserInfo } from '../types'
import { getUsers, createUser, deleteUser, updateUserPassword } from '../api'
import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'
import PageHeader from '../components/PageHeader.vue'

const pageIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`

const authStore = useAuthStore()
const toast = useToastStore()
const currentUsername = authStore.user?.username || ''

const users = ref<UserInfo[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const creating = ref(false)
const showPasswordModal = ref(false)
const updatingPassword = ref(false)
const passwordTarget = ref<UserInfo | null>(null)

const roleLabels: Record<string, string> = {
  admin: '管理员',
  maintenance: '维修人员',
  operator: '操作员',
}

const createForm = ref({
  username: '',
  name: '',
  role: 'operator',
  password: '',
})

const passwordForm = ref({
  newPassword: '',
})

async function fetchUsers() {
  loading.value = true
  try {
    const res = await getUsers()
    if (res.code === 0) {
      users.value = res.data || []
    } else {
      toast.show('获取用户列表失败: ' + res.message, 'error')
    }
  } catch (err) {
    toast.show('获取用户列表失败', 'error')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  creating.value = true
  try {
    const res = await createUser(createForm.value)
    if (res.code === 0) {
      toast.show('创建成功', 'success')
      showCreateModal.value = false
      createForm.value = { username: '', name: '', role: 'operator', password: '' }
      fetchUsers()
    } else {
      toast.show('创建失败: ' + res.message, 'error')
    }
  } catch (err) {
    toast.show('创建失败: ' + (err instanceof Error ? err.message : '未知错误'), 'error')
  } finally {
    creating.value = false
  }
}

function openPasswordModal(user: UserInfo) {
  passwordTarget.value = user
  passwordForm.value.newPassword = ''
  showPasswordModal.value = true
}

async function handlePasswordChange() {
  if (!passwordTarget.value) return
  updatingPassword.value = true
  try {
    const res = await updateUserPassword(passwordTarget.value.username, passwordForm.value.newPassword)
    if (res.code === 0) {
      toast.show('密码修改成功', 'success')
      showPasswordModal.value = false
    } else {
      toast.show('修改失败: ' + res.message, 'error')
    }
  } catch (err) {
    toast.show('修改失败: ' + (err instanceof Error ? err.message : '未知错误'), 'error')
  } finally {
    updatingPassword.value = false
  }
}

async function handleDelete(user: UserInfo) {
  if (!confirm(`确定要删除用户 "${user.name}" (${user.username}) 吗？`)) return
  try {
    const res = await deleteUser(user.username)
    if (res.code === 0) {
      toast.show('删除成功', 'success')
      fetchUsers()
    } else {
      toast.show('删除失败: ' + res.message, 'error')
    }
  } catch (err) {
    toast.show('删除失败: ' + (err instanceof Error ? err.message : '未知错误'), 'error')
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
.user-management {
  max-width: 1200px;
  margin: 0 auto;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.data-table th {
  background: var(--industrial-bg);
}

.data-table td {
  font-size: 14px;
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin {
  background: rgba(220, 38, 38, 0.10);
  color: var(--color-danger);
}

.role-badge.maintenance {
  background: rgba(245, 158, 11, 0.10);
  color: var(--color-warning);
}

.role-badge.operator {
  background: rgba(22, 163, 74, 0.10);
  color: var(--color-success);
}

.btn-text {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 13px;
  padding: 4px 8px;
  margin-right: 8px;
}

.btn-text:hover {
  text-decoration: underline;
}

.btn-text.danger {
  color: var(--color-danger);
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-muted);
}

.modal-overlay {
  background: rgba(11, 29, 51, 0.5);
  backdrop-filter: blur(3px);
}

.modal {
  border-radius: 14px;
}

.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-item input,
.form-item select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--industrial-bg);
  color: var(--text-primary);
  font-size: 14px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, #2563EB 100%);
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid var(--border-color);
  background: var(--industrial-bg);
  color: var(--text-primary);
}

@media (max-width: 640px) {
  .user-management {
    max-width: 100%;
  }

  .toolbar {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;
  }

  .toolbar button {
    width: 100%;
    justify-content: center;
  }

  .card {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .data-table {
    min-width: 620px;
  }

  .modal-overlay {
    align-items: flex-end;
    padding: 12px;
  }

  .modal {
    width: 100%;
    max-height: calc(100svh - 24px);
    overflow-y: auto;
    border-radius: 22px;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }

  .modal-actions button {
    width: 100%;
  }
}
</style>
