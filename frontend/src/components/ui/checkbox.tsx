import React from 'react';
import { Check } from 'lucide-react';

interface CheckboxProps {
  id?: string;
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  className?: string;
  disabled?: boolean;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  id,
  checked = false,
  onCheckedChange,
  className = '',
  disabled = false
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onCheckedChange) {
      onCheckedChange(e.target.checked);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <input
        id={id}
        type="checkbox"
        checked={checked}
        onChange={handleChange}
        disabled={disabled}
        className="sr-only"
      />
      <div
        className={`
          w-4 h-4 rounded-sm border-2 border-gray-300 bg-white
          flex items-center justify-center cursor-pointer
          ${checked ? 'bg-blue-600 border-blue-600' : ''}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-500'}
          transition-colors duration-200
        `}
        onClick={() => !disabled && onCheckedChange?.(!checked)}
      >
        {checked && <Check className="w-3 h-3 text-white" />}
      </div>
    </div>
  );
};