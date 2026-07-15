import React from 'react';
import {
  ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts';
import type { ActualVsPredicted, ForecastDay } from '../../types';

interface ForecastChartProps {
  actualVsPredicted: ActualVsPredicted[];
  forecasts?: Record<string, ForecastDay>;
  height?: number;
}

const ForecastChart: React.FC<ForecastChartProps> = ({
  actualVsPredicted,
  forecasts,
  height = 400,
}) => {
  if (!actualVsPredicted.length) return null;

  // Build forecast extension data
  const forecastData: any[] = [];
  if (forecasts) {
    const dayForecast = forecasts['7_day'] || forecasts['1_day'];
    if (dayForecast?.daily_predictions) {
      const lastDate = new Date(actualVsPredicted[actualVsPredicted.length - 1].date);
      dayForecast.daily_predictions.forEach((pred, i) => {
        const date = new Date(lastDate);
        date.setDate(date.getDate() + i + 1);
        // Skip weekends
        while (date.getDay() === 0 || date.getDay() === 6) {
          date.setDate(date.getDate() + 1);
        }
        forecastData.push({
          date: date.toISOString().split('T')[0],
          forecast: pred,
          confidenceRange: [dayForecast.confidence_lower, dayForecast.confidence_upper],
        });
      });
    }
  }

  const combined = [
    ...actualVsPredicted.map(d => ({
      date: d.date,
      actual: d.actual,
      predicted: d.predicted,
    })),
    ...forecastData,
  ];

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={combined} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10, fill: '#94a3b8' }}
          interval={Math.floor(combined.length / 6)}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 10, fill: '#94a3b8' }}
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
          formatter={(value: any, name: any) => [`$${value?.toFixed(2)}`, name]}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Line type="monotone" dataKey="actual" stroke="#94a3b8" dot={false} strokeWidth={1.5} name="Actual" />
        <Line type="monotone" dataKey="predicted" stroke="#3b82f6" dot={false} strokeWidth={2} name="Predicted" />
        <Line type="monotone" dataKey="forecast" stroke="#8b5cf6" dot={false} strokeWidth={2} strokeDasharray="6 3" name="Forecast" />
        <Area type="monotone" dataKey="confidenceRange" stroke="none" fill="url(#forecastGrad)" name="Confidence" />
      </ComposedChart>
    </ResponsiveContainer>
  );
};

export default ForecastChart;
