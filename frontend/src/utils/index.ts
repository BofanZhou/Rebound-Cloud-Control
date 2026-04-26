export function formatTime(time: string | undefined): string {
  if (!time) return '---'
  return new Date(time).toLocaleString('zh-CN')
}

export function formatDeviation(deviation: number | undefined): string {
  if (deviation === undefined || deviation === null) return '0.00'
  const sign = deviation >= 0 ? '+' : ''
  return `${sign}${deviation.toFixed(2)}`
}
