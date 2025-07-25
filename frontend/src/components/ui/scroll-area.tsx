import React from 'react';

interface ScrollAreaProps {
  className?: string;
  children: React.ReactNode;
}

export const ScrollArea: React.FC<ScrollAreaProps> = ({
  className = '',
  children
}) => (
  <div className={`overflow-auto ${className}`}>
    {children}
  </div>
);