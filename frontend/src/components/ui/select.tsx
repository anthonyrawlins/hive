import React, { useState } from 'react';

interface SelectProps {
  children: React.ReactNode;
  onValueChange?: (value: string) => void;
  value?: string;
}

interface SelectTriggerProps {
  className?: string;
  children: React.ReactNode;
}

interface SelectContentProps {
  children: React.ReactNode;
}

interface SelectItemProps {
  value: string;
  children: React.ReactNode;
}

interface SelectValueProps {
  placeholder?: string;
}

export const Select: React.FC<SelectProps> = ({ children, onValueChange, value }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div className="relative">
      {React.Children.map(children, child => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { 
            isOpen, 
            setIsOpen, 
            onValueChange, 
            value 
          } as any);
        }
        return child;
      })}
    </div>
  );
};

export const SelectTrigger: React.FC<SelectTriggerProps & any> = ({ 
  className = '', 
  children, 
  isOpen, 
  setIsOpen 
}) => (
  <button
    type="button"
    className={`flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    onClick={() => setIsOpen(!isOpen)}
  >
    {children}
  </button>
);

export const SelectContent: React.FC<SelectContentProps & any> = ({ 
  children, 
  isOpen, 
  setIsOpen, 
  onValueChange 
}) => {
  if (!isOpen) return null;
  
  return (
    <div className="absolute top-full z-50 w-full rounded-md border border-gray-300 bg-white shadow-lg">
      {React.Children.map(children, child => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { 
            setIsOpen, 
            onValueChange 
          } as any);
        }
        return child;
      })}
    </div>
  );
};

export const SelectItem: React.FC<SelectItemProps & any> = ({ 
  value, 
  children, 
  setIsOpen, 
  onValueChange 
}) => (
  <div
    className="cursor-pointer px-3 py-2 text-sm hover:bg-gray-100"
    onClick={() => {
      onValueChange?.(value);
      setIsOpen(false);
    }}
  >
    {children}
  </div>
);

export const SelectValue: React.FC<SelectValueProps & any> = ({ 
  placeholder, 
  value 
}) => (
  <span className="block truncate">
    {value || placeholder}
  </span>
);