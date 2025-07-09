import React from 'react';

interface ProgressProps {
  className?: string;
  value: number;
  max?: number;
}

export const Progress: React.FC<ProgressProps> = ({
  className = '',
  value,
  max = 100
}) => {
  const percentage = Math.min((value / max) * 100, 100);
  
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2.5 ${className}`}>
      <div
        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
};