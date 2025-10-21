import React from 'react'

type Props = {
  data: number[]
  height?: number
  color?: string
}

const SimpleChart = ({ data, height = 120, color = '#4f46e5' }: Props) => {
  const width = 300
  const max = Math.max(...data, 1)
  const min = Math.min(...data)
  const points = data.map((d, i) => {
    const x = (i / (data.length - 1 || 1)) * width
    const y = height - ((d - min) / (max - min || 1)) * height
    return `${x},${y}`
  }).join(' ')

  const areaPoints = `0,${height} ${points} ${width},${height}`

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} preserveAspectRatio="none">
      <defs>
        <linearGradient id="grad" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.15" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polyline points={points} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
      <polygon points={areaPoints} fill="url(#grad)" />
    </svg>
  )
}

export default SimpleChart
