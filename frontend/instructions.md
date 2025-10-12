# Auth Store Implementation Plan

Based on the Vue 3 + TypeScript architecture with Pinia for state management, here's a detailed plan for implementing authentication store functionality:

## Implementation Steps

### Step 1: Create Auth Store

Create a new file `stores/auth.ts` to implement the authentication store using Pinia:

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AuthService, UsersService } from '../api/sdk.gen'
import type { User } from '../api/types.gen'
import { ApiError } from '../api/core/ApiError'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<User | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<Error | null>(null)

  // Computed
  const isAuthenticated = computed(() => !!token.value)

  // Actions
  async function login(username: string, password: string) {
    loading.value = true
    error.value = null

    try {
      const response = await AuthService.login({ username, password })
      token.value = response.access_token
      localStorage.setItem('access_token', response.access_token)

      // Fetch user profile after successful login
      await fetchUserProfile()

      return user.value
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Login failed')
      token.value = null
      localStorage.removeItem('access_token')
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function fetchUserProfile() {
    if (!token.value) return null

    loading.value = true
    try {
      user.value = await UsersService.readUserMe()
      return user.value
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        // Token is invalid or expired
        logout()
      }
      error.value = err instanceof Error ? err : new Error('Failed to fetch user profile')
      throw error.value
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
  }

  async function register(userData: any) {
    loading.value = true
    error.value = null

    try {
      await UsersService.registerUser({ requestBody: userData })
      // Login after registration if your API supports it
      // or redirect to login
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Registration failed')
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(userData: any) {
    if (!isAuthenticated.value) return null

    loading.value = true
    error.value = null

    try {
      user.value = await UsersService.updateUserMe({ requestBody: userData })
      return user.value
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Profile update failed')
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function changePassword(oldPassword: string, newPassword: string) {
    if (!isAuthenticated.value) return false

    loading.value = true
    error.value = null

    try {
      await UsersService.updatePasswordMe({
        requestBody: {
          current_password: oldPassword,
          new_password: newPassword,
        },
      })
      return true
    } catch (err) {
      error.value = err instanceof Error ? err : new Error('Password change failed')
      throw error.value
    } finally {
      loading.value = false
    }
  }

  // Initialize - try to load user profile if token exists
  if (token.value) {
    fetchUserProfile().catch(() => {
      // Silent fail - will be handled by fetchUserProfile
    })
  }

  return {
    // State
    user,
    loading,
    error,

    // Computed
    isAuthenticated,

    // Actions
    login,
    logout,
    register,
    fetchUserProfile,
    updateProfile,
    changePassword,
  }
})
```

### Step 2: Update code to use auth store

Update necessary files like the router or the main.ts to activate the usage of the new store.

### Step 3: Update Router with Navigation Guards

Modify your router configuration to protect routes and handle authentication states:

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true },
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
      meta: { requiresAuth: true },
    },
    // Add other routes here
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const isGuestRoute = to.matched.some((record) => record.meta.guest)

  if (requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login if trying to access protected route
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (isGuestRoute && authStore.isAuthenticated) {
    // Redirect to home if logged in user tries to access guest route
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
```

### Step 4: Update useAuth Composable to Use the Store

Update your existing `useAuth.ts` composable to leverage the Pinia store:

```typescript
// composables/useAuth.ts
import { useAuthStore } from '../stores/auth'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()

  // Helper functions to make consuming the store easier in components
  const login = async (username: string, password: string) => {
    await authStore.login(username, password)
    // Get redirect from query params or default to home
    const redirectPath = (router.currentRoute.value.query.redirect as string) || '/'
    router.push(redirectPath)
  }

  const logout = () => {
    authStore.logout()
    router.push('/login')
  }

  // You can add additional helper methods here
  const isLoggedIn = computed(() => authStore.isAuthenticated)
  const currentUser = computed(() => authStore.user)
  const isLoading = computed(() => authStore.loading)
  const authError = computed(() => authStore.error)

  return {
    login,
    logout,
    isLoggedIn,
    currentUser,
    isLoading,
    authError,
    // Expose other methods as needed
    register: authStore.register,
    updateProfile: authStore.updateProfile,
    changePassword: authStore.changePassword,
  }
}
```

### Step 5: Create or Update Login Component

Update your `LoginView.vue` to use the auth composable:

```vue
<script setup lang="ts">
import { ref } from 'vue'
import useAuth from '../composables/useAuth'

const { login, isLoading, authError } = useAuth()

const credentials = ref({
  username: '',
  password: '',
})

const submitLogin = async () => {
  try {
    await login(credentials.value.username, credentials.value.password)
  } catch (error) {
    // Error handling is already in the store
    // Additional UI error handling can be done here
  }
}
</script>

<template>
  <div class="login-container">
    <h1>Login</h1>

    <form @submit.prevent="submitLogin" class="login-form">
      <div class="field">
        <label for="username">Username</label>
        <input id="username" v-model="credentials.username" type="text" required autofocus />
      </div>

      <div class="field">
        <label for="password">Password</label>
        <input id="password" v-model="credentials.password" type="password" required />
      </div>

      <div v-if="authError" class="error-message">
        {{ authError.message }}
      </div>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
/* Add your styling here */
</style>
```

### Step 6: Update App.vue to Use Authentication State

Update your `App.vue` to reflect authentication status and handle layout changes based on login state:

```vue
<script setup lang="ts">
import { RouterView } from 'vue-router'
import useAuth from './composables/useAuth'

const { isLoggedIn, currentUser } = useAuth()
</script>

<template>
  <header v-if="isLoggedIn">
    <!-- Navigation for authenticated users -->
    <nav>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
      <!-- Other navigation links -->
    </nav>

    <div v-if="currentUser" class="user-info">Welcome, {{ currentUser.name }}</div>
  </header>

  <RouterView />
</template>
```

## Explanation of Key Components

1. **Auth Store (`stores/auth.ts`)**:

   - Central place for authentication state
   - Handles login, logout, user profile operations
   - Manages token storage and retrieval
   - Provides reactive state via Pinia

2. **API Configuration (`main.ts`)**:

   - Sets up OpenAPI configuration
   - Configures token retrieval
   - Sets up global error handling for auth errors

3. **Router Guards (`router/index.ts`)**:

   - Protect routes that require authentication
   - Redirect authenticated users away from guest routes
   - Handle redirect after login

4. **Auth Composable (`composables/useAuth.ts`)**:

   - Provides a convenient interface to the auth store
   - Adds router integration
   - Makes component integration cleaner

5. **Login Component (`LoginView.vue`)**:
   - Uses the auth composable
   - Handles form submission
   - Shows loading and error states

