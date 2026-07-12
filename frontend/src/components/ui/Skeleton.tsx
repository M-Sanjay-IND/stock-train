import React from 'react';

interface SkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = '' }) => (
  <div className={`skeleton ${className}`} />
);

export const CardSkeleton: React.FC = () => (
  <div className="glass-card p-6 space-y-4">
    <Skeleton className="h-4 w-24" />
    <Skeleton className="h-8 w-32" />
    <Skeleton className="h-3 w-20" />
  </div>
);

export const ChartSkeleton: React.FC = () => (
  <div className="glass-card p-6 space-y-4">
    <Skeleton className="h-5 w-40" />
    <Skeleton className="h-64 w-full rounded-lg" />
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="glass-card p-6 space-y-3">
    <Skeleton className="h-5 w-48" />
    <Skeleton className="h-10 w-full rounded" />
    {Array.from({ length: rows }).map((_, i) => (
      <Skeleton key={i} className="h-8 w-full rounded" />
    ))}
  </div>
);
