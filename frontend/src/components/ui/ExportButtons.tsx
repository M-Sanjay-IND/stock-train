import React from 'react';
import { Download } from 'lucide-react';
import { exportToCSV } from '../../lib/utils';

interface ExportButtonsProps {
  data: Record<string, any>[];
  filename: string;
}

const ExportButtons: React.FC<ExportButtonsProps> = ({ data, filename }) => {
  return (
    <div className="flex gap-2">
      <button
        onClick={() => exportToCSV(data, filename)}
        disabled={!data.length}
        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-secondary hover:bg-accent text-foreground transition-colors disabled:opacity-50"
      >
        <Download className="w-3.5 h-3.5" />
        Export CSV
      </button>
    </div>
  );
};

export default ExportButtons;
