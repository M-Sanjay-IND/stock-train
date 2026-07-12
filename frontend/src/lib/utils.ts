import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// --- Number Formatters ---

export function formatCurrency(value: number | null, currency = 'USD'): string {
  if (value === null || value === undefined) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatLargeNumber(value: number | null): string {
  if (value === null || value === undefined) return '—';
  if (Math.abs(value) >= 1e12) return `${(value / 1e12).toFixed(2)}T`;
  if (Math.abs(value) >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
  if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
  if (Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
  return value.toFixed(2);
}

export function formatPercent(value: number | null, decimals = 2): string {
  if (value === null || value === undefined) return '—';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${(value * 100).toFixed(decimals)}%`;
}

export function formatPercentRaw(value: number | null, decimals = 2): string {
  if (value === null || value === undefined) return '—';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

export function formatNumber(value: number | null, decimals = 2): string {
  if (value === null || value === undefined) return '—';
  return value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatVolume(value: number | null): string {
  if (value === null || value === undefined) return '—';
  return formatLargeNumber(value);
}

// --- Date Formatters ---

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function timeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(dateStr);
}

// --- CSV Export ---
export function exportToCSV(data: Record<string, any>[], filename: string) {
  if (!data.length) return;
  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map((row) =>
      headers.map((h) => {
        const val = row[h];
        if (typeof val === 'string' && val.includes(',')) return `"${val}"`;
        return val ?? '';
      }).join(',')
    ),
  ].join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${filename}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// --- Color Helpers ---
export function getPriceColor(value: number | null): string {
  if (value === null || value === undefined) return 'text-gray-400';
  return value >= 0 ? 'text-emerald-400' : 'text-red-400';
}

export function getTrendIcon(value: number | null): string {
  if (value === null || value === undefined) return '→';
  return value >= 0 ? '↑' : '↓';
}
