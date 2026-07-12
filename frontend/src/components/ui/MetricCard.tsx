import React from 'react';
import { motion } from 'framer-motion';
import { cn, getPriceColor, formatPercentRaw, formatCurrency } from '../../lib/utils';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string;
  change?: number | null;
  icon?: LucideIcon;
  className?: string;
  delay?: number;
}

const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  change,
  icon: Icon,
  className = '',
  delay = 0,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: delay * 0.1 }}
      className={cn('glass-card-hover p-5', className)}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="stat-label">{label}</p>
          <p className="stat-value text-foreground">{value}</p>
          {change !== null && change !== undefined && (
            <p className={cn('text-xs font-medium', getPriceColor(change))}>
              {formatPercentRaw(change)}
            </p>
          )}
        </div>
        {Icon && (
          <div className="p-2 rounded-lg bg-primary/10">
            <Icon className="w-4 h-4 text-primary" />
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default MetricCard;
