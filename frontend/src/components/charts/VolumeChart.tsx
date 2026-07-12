import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';
import type { StockHistory } from '../../types';

interface VolumeChartProps {
  data: StockHistory[];
  height?: number;
}

const VolumeChart: React.FC<VolumeChartProps> = ({ data, height = 200 }) => {
  if (!data.length) return null;

  const formatted = data.slice(-100).map((d, i, arr) => ({
    ...d,
    fill: i > 0 && d.close >= arr[i - 1].close ? '#10b981' : '#ef4444',
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={formatted} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10, fill: '#94a3b8' }}
          tickFormatter={(v) => new Date(v).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          interval={Math.floor(formatted.length / 5)}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 10, fill: '#94a3b8' }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => {
            if (v >= 1e6) return `${(v / 1e6).toFixed(0)}M`;
            if (v >= 1e3) return `${(v / 1e3).toFixed(0)}K`;
            return v.toString();
          }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(228, 63%, 8%)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            color: '#f1f5f9',
            fontSize: 12,
          }}
          formatter={(value: number) => [value.toLocaleString(), 'Volume']}
        />
        <Bar dataKey="volume" radius={[2, 2, 0, 0]} fill="#3b82f6" opacity={0.7} />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default VolumeChart;
