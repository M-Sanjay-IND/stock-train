import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts';

interface TrainingChartProps {
  trainingLoss: number[] | null;
  validationLoss: number[] | null;
  height?: number;
}

const TrainingChart: React.FC<TrainingChartProps> = ({
  trainingLoss,
  validationLoss,
  height = 300,
}) => {
  if (!trainingLoss) return null;

  const data = trainingLoss.map((loss, i) => ({
    epoch: i + 1,
    training: loss,
    validation: validationLoss?.[i] ?? null,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis
          dataKey="epoch"
          tick={{ fontSize: 10, fill: '#94a3b8' }}
          axisLine={false}
          tickLine={false}
          label={{ value: 'Epoch', position: 'bottom', fill: '#94a3b8', fontSize: 11 }}
        />
        <YAxis
          tick={{ fontSize: 10, fill: '#94a3b8' }}
          axisLine={false}
          tickLine={false}
          label={{ value: 'Loss (MSE)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(228, 63%, 8%)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            color: '#f1f5f9',
            fontSize: 12,
          }}
          formatter={(value: number) => [value?.toFixed(6), '']}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Line type="monotone" dataKey="training" stroke="#3b82f6" dot={false} strokeWidth={2} name="Training Loss" />
        <Line type="monotone" dataKey="validation" stroke="#f59e0b" dot={false} strokeWidth={2} name="Validation Loss" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TrainingChart;
