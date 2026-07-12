import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import type { StockHistory } from '../../types';

interface CandlestickChartProps {
  data: StockHistory[];
  height?: number;
}

const CandlestickChart: React.FC<CandlestickChartProps> = ({ data, height = 450 }) => {
  const chartData = useMemo(() => {
    const sliced = data.slice(-120); // Last 120 days
    return [{
      type: 'candlestick' as const,
      x: sliced.map(d => d.date),
      open: sliced.map(d => d.open),
      high: sliced.map(d => d.high),
      low: sliced.map(d => d.low),
      close: sliced.map(d => d.close),
      increasing: { line: { color: '#10b981' }, fillcolor: 'rgba(16,185,129,0.3)' },
      decreasing: { line: { color: '#ef4444' }, fillcolor: 'rgba(239,68,68,0.3)' },
    }];
  }, [data]);

  const layout = useMemo(() => ({
    height,
    margin: { l: 50, r: 20, t: 20, b: 40 },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    xaxis: {
      gridcolor: 'rgba(255,255,255,0.05)',
      color: '#94a3b8',
      rangeslider: { visible: false },
    },
    yaxis: {
      gridcolor: 'rgba(255,255,255,0.05)',
      color: '#94a3b8',
      side: 'right' as const,
    },
    font: { family: 'Inter', size: 11, color: '#94a3b8' },
    dragmode: 'zoom' as const,
  }), [height]);

  if (!data.length) return null;

  return (
    <Plot
      data={chartData}
      layout={layout}
      config={{ displayModeBar: true, displaylogo: false, responsive: true }}
      style={{ width: '100%' }}
    />
  );
};

export default CandlestickChart;
