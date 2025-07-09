import React from 'react';

interface SeparatorProps {
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}

export const Separator: React.FC<SeparatorProps> = ({
  className = '',
  orientation = 'horizontal'
}) => {
  const orientationClasses = {
    horizontal: 'h-px w-full',
    vertical: 'w-px h-full'
  };

  return (
    <div
      className={`bg-gray-200 ${orientationClasses[orientation]} ${className}`}
    />
  );
};