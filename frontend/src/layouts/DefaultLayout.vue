<script setup lang="ts">
import { ref } from 'vue'
import type { MenuItem } from 'primevue/menuitem'
import Button from 'primevue/button'

// Default layout for authenticated users
const isSidebarCollapsed = ref(false)

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const menuItems = ref<MenuItem[]>([
  {
    label: 'Overview',
    items: [
      {
        label: 'Balance Sheet',
        icon: 'pi pi-wallet',
        to: '/balance-sheet'
      },
      {
        label: 'Monthly Overview',
        icon: 'pi pi-chart-bar',
        to: '/monthly-overview'
      }
    ]
  },
  {
    label: 'Finances',
    items: [
      {
        label: 'Reports',
        icon: 'pi pi-file-export',
        to: '/reports'
      },
      {
        label: 'Queries',
        icon: 'pi pi-search',
        to: '/queries'
      }
    ]
  },
  {
    label: 'Investments',
    items: [
      {
        label: 'Investment Performance',
        icon: 'pi pi-chart-line',
        to: '/investment-performance'
      },
      {
        label: 'FIRE & Simulations',
        icon: 'pi pi-flag',
        to: '/fire-simulations'
      }
    ]
  },
  {
    label: 'Settings',
    items: [
      {
        label: 'Data Sync',
        icon: 'pi pi-sync',
        to: '/data-sync'
      },
      {
        label: 'Preferences',
        icon: 'pi pi-cog',
        to: '/preferences'
      }
    ]
  }
])
</script>

<template>
  <div class="default-layout">
    <header class="header">
      <!-- Placeholder for Navbar -->
      <p>FinDash</p>
    </header>
    <div class="main-container">
      <aside class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
        <Button
          :icon="isSidebarCollapsed ? 'pi pi-angle-double-right' : 'pi pi-angle-double-left'"
          @click="toggleSidebar"
          class="p-button-rounded p-button-text sidebar-toggle-button"
        />
        <div class="menu-wrapper">
          <div v-for="section in menuItems" :key="section.label" class="menu-section">
            <p class="section-header" :class="{ 'label-hidden': isSidebarCollapsed }">{{ section.label }}</p>
            <ul>
              <li v-for="item in section.items" :key="item.label">
                <router-link :to="item.to" class="menu-item-link">
                  <i :class="item.icon" class="menu-item-icon"></i>
                  <span :class="{ 'label-hidden': isSidebarCollapsed }">{{ item.label }}</span>
                </router-link>
              </li>
            </ul>
          </div>
        </div>
      </aside>
      <main class="content">
        <router-view></router-view>
        <!-- Slot for the actual view -->
      </main>
    </div>
  </div>
</template>

<style scoped>
.default-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--surface-ground);
}

.header {
  background-color: var(--surface-card);
  padding: 1rem;
  border-bottom: 1px solid var(--surface-border);
  color: var(--text-color);
  /* Add styles for header content alignment, etc. */
}

.main-container {
  display: flex;
  flex-grow: 1;
}

.sidebar {
  width: 280px;
  background-color: var(--surface-a);
  padding: 1rem;
  border-right: 1px solid var(--surface-border);
  transition: width 0.3s ease;
  position: relative;
  overflow-x: hidden;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-toggle-button {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  z-index: 10;
}

.sidebar.collapsed .sidebar-toggle-button {
  right: 0.25rem;
}

.content {
  flex-grow: 1;
  padding: 2rem;
  transition: margin-left 0.3s ease;
}

.menu-wrapper {
  margin-top: 3.5rem; /* Pushes menu content down to avoid toggle button */
}

/* Custom menu styles */
.menu-section {
  margin-bottom: 0.15rem;
}

.section-header {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-color-secondary);
  text-transform: uppercase;
  padding: 0 0.75rem 0.75rem 0.75rem;
  margin: 0;
  white-space: nowrap;
  transition: all 0.2s ease-out;
}

.menu-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item-link {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 6px;
  color: var(--text-color);
  text-decoration: none;
  transition: background-color 0.2s;
  font-size: 0.95rem;
  white-space: nowrap;
}

.menu-item-link:hover {
  background-color: var(--surface-hover);
}

.menu-item-icon {
  margin-right: 0.75rem;
  font-size: 1.2rem;
}

.sidebar.collapsed .menu-item-link {
  justify-content: center;
}

.sidebar.collapsed .menu-item-icon {
  margin-right: 0;
}

.sidebar.collapsed .section-header {
  height: 0;
  padding: 0;
  margin: 0;
  overflow: hidden;
}

.sidebar.collapsed .menu-section {
  margin-bottom: 0;
}

.router-link-exact-active {
  background-color: var(--surface-card);
  color: var(--primary-color);
}

.router-link-exact-active .menu-item-icon {
  color: var(--primary-color);
}

.label-hidden {
  opacity: 0;
  width: 0;
  overflow: hidden;
  transition: opacity 0.1s ease, width 0.1s ease;
}
</style>
