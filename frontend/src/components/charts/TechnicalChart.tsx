import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
  AreaChart, Area, BarChart, Bar, ComposedChart, ReferenceLine,
} from 'recharts';
import type { TechnicalSeries } from '../../types';

interface TechnicalChartProps {
  data: TechnicalSeries[];
  height?: number;
}

type ChartType = 'sma' | 'bollinger' | 'rsi' | 'macd';

const TechnicalChart: React.FC<TechnicalChartProps> = ({ data, height = 350 }) => {
  const [activeChart, setActiveChart] = useState<ChartType>('sma');

  if (!data.length) return null;

  const tabs: { key: ChartType; label: string }[] = [
    { key: 'sma', label: 'SMA / EMA' },
    { key: 'bollinger', label: 'Bollinger' },
    { key: 'rsi', label: 'RSI' },
    { key: 'macd', label: 'MACD' },
  ];

  const tooltipStyle = {
    backgroundColor: 'hsl(228, 63%, 8%)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '12px',
    color: '#f1f5f9',
    fontSize: 12,
  };

  const recent = data.slice(-100);

  return (
    <div>
      {/* Tabs */}
      <div className="flex gap-1 mb-4 p-1 bg-secondary/50 rounded-lg w-fit">
        {tabs.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveChart(key)}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
              activeChart === key
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* SMA / EMA */}
      {activeChart === 'sma' && (
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={recent} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={Math.floor(recent.length / 5)} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} domain={['auto', 'auto']} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line type="monotone" dataKey="close" stroke="#94a3b8" dot={false} strokeWidth={1.5} name="Close" />
            <Line type="monotone" dataKey="sma_20" stroke="#3b82f6" dot={false} strokeWidth={1.5} name="SMA 20" strokeDasharray="4 2" />
            <Line type="monotone" dataKey="sma_50" stroke="#8b5cf6" dot={false} strokeWidth={1.5} name="SMA 50" strokeDasharray="4 2" />
            <Line type="monotone" dataKey="ema_20" stroke="#06b6d4" dot={false} strokeWidth={1.5} name="EMA 20" />
            <Line type="monotone" dataKey="ema_50" stroke="#f59e0b" dot={false} strokeWidth={1.5} name="EMA 50" />
          </LineChart>
        </ResponsiveContainer>
      )}

      {/* Bollinger Bands */}
      {activeChart === 'bollinger' && (
        <ResponsiveContainer width="100%" height={height}>
          <AreaChart data={recent} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={Math.floor(recent.length / 5)} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} domain={['auto', 'auto']} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Area type="monotone" dataKey="bb_upper" stroke="#8b5cf6" fill="rgba(139,92,246,0.05)" strokeWidth={1} name="Upper Band" dot={false} />
            <Area type="monotone" dataKey="bb_lower" stroke="#8b5cf6" fill="rgba(139,92,246,0.05)" strokeWidth={1} name="Lower Band" dot={false} />
            <Line type="monotone" dataKey="bb_middle" stroke="#8b5cf6" strokeDasharray="4 2" dot={false} strokeWidth={1} name="Middle" />
            <Line type="monotone" dataKey="close" stroke="#f1f5f9" dot={false} strokeWidth={2} name="Close" />
          </AreaChart>
        </ResponsiveContainer>
      )}

      {/* RSI */}
      {activeChart === 'rsi' && (
        <ResponsiveContainer width="100%" height={height}>
          <ComposedChart data={recent} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={Math.floor(recent.length / 5)} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} domain={[0, 100]} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={tooltipStyle} />
            <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 2" label={{ value: 'Overbought (70)', position: 'right', fill: '#ef4444', fontSize: 10 }} />
            <ReferenceLine y={30} stroke="#10b981" strokeDasharray="4 2" label={{ value: 'Oversold (30)', position: 'right', fill: '#10b981', fontSize: 10 }} />
            <Area type="monotone" dataKey="rsi" stroke="#3b82f6" fill="rgba(59,130,246,0.1)" strokeWidth={2} dot={false} name="RSI" />
          </ComposedChart>
        </ResponsiveContainer>
      )}

      {/* MACD */}
      {activeChart === 'macd' && (
        <ResponsiveContainer width="100%" height={height}>
          <ComposedChart data={recent} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={Math.floor(recent.length / 5)} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <ReferenceLine y={0} stroke="rgba(255,255,255,0.1)" />
            <Bar dataKey="macd_histogram" name="Histogram" fill="#3b82f6" opacity={0.4} />
            <Line type="monotone" dataKey="macd" stroke="#3b82f6" dot={false} strokeWidth={2} name="MACD" />
            <Line type="monotone" dataKey="macd_signal" stroke="#ef4444" dot={false} strokeWidth={1.5} name="Signal" />
          </ComposedChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default TechnicalChart;
