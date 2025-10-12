<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
// Import PrimeVue components
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

// Form state variables
const username = ref('')
const password = ref('')
const formSubmitted = ref(false)

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Form validation
const isFormValid = computed(() => {
  return username.value.trim() !== '' && password.value.trim() !== ''
})

// Form submission handler
const handleSubmit = async () => {
  formSubmitted.value = true

  if (isFormValid.value) {
    try {
      await authStore.login({
        username: username.value,
        password: password.value
      })
      
      // Redirect to the originally requested URL or home
      const redirectPath = route.query.redirect as string || '/'
      router.push(redirectPath)
    } catch (err) {
      // Error is handled by the store
    }
  }
}
</script>

<template>
  <Card class="login-card">
        <template #header>
          <div class="card-header">
            <h2 class="title">Login</h2>
          </div>
        </template>

        <template #content>
          <form @submit.prevent="handleSubmit" class="form-container">
            <div class="form-field">
              <label for="username">Username</label>
              <div class="input-wrapper">
                <InputText
                  id="username"
                  v-model="username"
                  placeholder="Enter your username"
                  :class="{ invalid: formSubmitted && !username }"
                  autocomplete="username"
                  class="w-full"
                />
              </div>
              <small v-if="formSubmitted && !username" class="error-text">Username required</small>
            </div>

            <div class="form-field">
              <label for="password">Password</label>
              <div class="input-wrapper">
                <Password
                  id="password"
                  v-model="password"
                  placeholder="Enter your password"
                  :toggleMask="true"
                  :feedback="false"
                  :class="{ invalid: formSubmitted && !password }"
                  autocomplete="current-password"
                  class="w-full"
                />
              </div>
              <small v-if="formSubmitted && !password" class="error-text">Password required</small>
            </div>

            <div v-if="authStore.error" class="error-message">
              <Message severity="error">{{ authStore.error.message }}</Message>
            </div>

            <div class="button-container">
              <Button 
                type="submit" 
                label="Login" 
                icon="pi pi-sign-in" 
                :loading="authStore.loading"
                class="p-button-primary login-button"
              />
            </div>
          </form>
        </template>
  </Card>
</template>

<style scoped>
/* Card styles only - layout is handled by AuthLayout */
.login-card {
  max-width: 500px;
  width: 100%;
  margin: 0 auto;
}

/* Styles specific to the login card and its contents */
.login-card {
  width: 100%;
  background-color: var(--surface-card);
  border-radius: var(--border-radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 4rem;
}

.login-card :deep(.p-card-content) {
  padding: 1.5rem 2rem 2.5rem;
  display: flex;
  justify-content: center;
}

.form-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.form-field {
  margin-bottom: 2rem;
  width: 100%;
  max-width: 450px;
  margin-left: auto;
  margin-right: auto;
}

.input-wrapper {
  width: 100%;
}

.input-wrapper :deep(.p-password),
.input-wrapper :deep(.p-inputtext) {
  width: 100%;
}

.login-card :deep(.p-password-input) {
  width: 100%;
}

.card-header {
  padding: 1.5rem;
  text-align: center;
  background-color: var(--surface-section);
  border-radius: var(--border-radius) var(--border-radius) 0 0;
}

.title {
  margin: 0;
  color: var(--primary-color);
  font-weight: 600;
  font-size: 1.5rem;
}

.form-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  text-align: left;
}

.invalid {
  border-color: var(--red-500) !important;
}

.error-text {
  color: var(--red-500);
  display: block;
  margin-top: 0.25rem;
  text-align: left;
}

.error-message {
  margin: 1.5rem auto;
  width: 100%;
  max-width: 450px;
}

.button-container {
  margin: 2.5rem auto 0;
  width: 100%;
  max-width: 450px;
  display: flex;
  justify-content: center;
}

.login-button {
  width: 100%;
  min-height: 2.5rem;
}
</style>
