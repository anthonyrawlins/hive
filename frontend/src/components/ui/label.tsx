import React from 'react';

interface LabelProps {
  className?: string;
  htmlFor?: string;
  children: React.ReactNode;
}

export const Label: React.FC<LabelProps> = ({ className = '', htmlFor, children }) => (
  <label
    className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}
    htmlFor={htmlFor}
  >
    {children}
  </label>
);