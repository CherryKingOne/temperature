import { onBeforeUnmount, ref } from 'vue'

/**
 * 倒计时（用于验证码重发等场景）
 * 倒计时由前端负责，服务端不做重发冷却
 */
export function useCountdown(seconds = 60) {
  /** 剩余秒数，0 表示可重新触发 */
  const remaining = ref(0)
  let timer: number | undefined

  function stop(): void {
    if (timer) {
      window.clearInterval(timer)
      timer = undefined
    }
  }

  function start(from: number = seconds): void {
    stop()
    remaining.value = from
    timer = window.setInterval(() => {
      remaining.value -= 1
      if (remaining.value <= 0) {
        stop()
        remaining.value = 0
      }
    }, 1000)
  }

  onBeforeUnmount(stop)

  return { remaining, start, stop }
}
