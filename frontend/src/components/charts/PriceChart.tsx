import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';
import type { StockHistory } from '../../types';

interface PriceChartProps {
  data: StockHistory[];
  height?: number;
}

const PriceChart: React.FC<PriceChartProps> = ({ data, height = 400 }) => {
  if (!data.length) return null;

  const isPositive = data.length > 1 && data[data.length - 1].close >= data[0].close;
  const color = isPositive ? '#10b981' : '#ef4444';

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11, fill: '#94a3b8' }}
          tickFormatter={(v) => new Date(v).toLocaleDateString('en-US', { month: 'short', year: '2-digit' })}
          interval={Math.floor(data.length / 6)}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 11, fill: '#94a3b8' }}
          domain={['auto', 'auto']}
          axisLine={false}
          tickLine={false}
          tickFormatter={(v) => `$${v.toFixed(0)}`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(228, 63%, 8%)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            color: '#f1f5f9',
            fontSize: 12,
          }}
          labelFormatter={(v) => new Date(v).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
          formatter={(value: number) => [`$${value.toFixed(2)}`, 'Close']}
        />
        <Area
          type="monotone"
          dataKey="close"
          stroke={color}
          strokeWidth={2}
          fill="url(#priceGradient)"
          dot={false}
          activeDot={{ r: 4, fill: color }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export default PriceChart;
