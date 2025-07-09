import React from 'react';

interface TextareaProps {
  className?: string;
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  disabled?: boolean;
  required?: boolean;
  id?: string;
  name?: string;
  rows?: number;
}

export const Textarea: React.FC<TextareaProps> = ({
  className = '',
  placeholder,
  value,
  onChange,
  disabled = false,
  required = false,
  id,
  name,
  rows = 4
}) => (
  <textarea
    className={`flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    placeholder={placeholder}
    value={value}
    onChange={onChange}
    disabled={disabled}
    required={required}
    id={id}
    name={name}
    rows={rows}
  />
);