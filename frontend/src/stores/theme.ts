import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'

/** 主题色 */
export type ThemeColor = 'blue' | 'green' | 'red' | 'yellow' | 'purple'
/** 明暗模式 */
export type ThemeMode = 'light' | 'dark'
/** 侧边栏主题 */
export type SidebarTheme = 'dark' | 'light' | 'deep'

export const THEME_COLORS: { value: ThemeColor; label: string; color: string }[] = [
  { value: 'blue', label: '蓝色系', color: '#3c8dbc' },
  { value: 'green', label: '绿色系', color: '#00a65a' },
  { value: 'red', label: '红色系', color: '#dd4b39' },
  { value: 'yellow', label: '黄色系', color: '#f39c12' },
  { value: 'purple', label: '紫色系', color: '#605ca8' },
]

const STORAGE_KEY = 'temperature_theme'

interface ThemeState {
  color: ThemeColor
  mode: ThemeMode
  sidebar: SidebarTheme
}

const DEFAULT_STATE: ThemeState = {
  color: 'blue',
  mode: 'light',
  sidebar: 'dark',
}

function loadState(): ThemeState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...DEFAULT_STATE }
    const parsed = JSON.parse(raw) as Partial<ThemeState>
    return {
      color: parsed.color ?? DEFAULT_STATE.color,
      mode: parsed.mode ?? DEFAULT_STATE.mode,
      sidebar: parsed.sidebar ?? DEFAULT_STATE.sidebar,
    }
  } catch {
    return { ...DEFAULT_STATE }
  }
}

/** 把主题写入 html 的 data 属性，由 CSS 变量接管 */
function applyState(state: ThemeState): void {
  const root = document.documentElement
  root.dataset.theme = state.color
  root.dataset.themeMode = state.mode
  root.dataset.sidebar = state.sidebar
}

export const useThemeStore = defineStore('theme', () => {
  const state = ref<ThemeState>(loadState())

  const color = computed(() => state.value.color)
  const mode = computed(() => state.value.mode)
  const sidebar = computed(() => state.value.sidebar)

  function setColor(value: ThemeColor): void {
    state.value = { ...state.value, color: value }
  }

  function setMode(value: ThemeMode): void {
    state.value = { ...state.value, mode: value }
  }

  function setSidebar(value: SidebarTheme): void {
    state.value = { ...state.value, sidebar: value }
  }

  function toggleMode(): void {
    setMode(state.value.mode === 'light' ? 'dark' : 'light')
  }

  watch(
    state,
    (value) => {
      applyState(value)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
    },
    { immediate: true, deep: true },
  )

  return { color, mode, sidebar, setColor, setMode, setSidebar, toggleMode }
})
