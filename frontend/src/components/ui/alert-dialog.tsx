import React, { useState, createContext, useContext } from 'react';

interface AlertDialogContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

const AlertDialogContext = createContext<AlertDialogContextType | undefined>(undefined);

interface AlertDialogProps {
  children: React.ReactNode;
}

export const AlertDialog: React.FC<AlertDialogProps> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <AlertDialogContext.Provider value={{ isOpen, setIsOpen }}>
      {children}
    </AlertDialogContext.Provider>
  );
};

export const AlertDialogTrigger: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const context = useContext(AlertDialogContext);
  if (!context) throw new Error('AlertDialogTrigger must be used within AlertDialog');
  
  return (
    <div onClick={() => context.setIsOpen(true)}>
      {children}
    </div>
  );
};

export const AlertDialogContent: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const context = useContext(AlertDialogContext);
  if (!context) throw new Error('AlertDialogContent must be used within AlertDialog');
  
  if (!context.isOpen) return null;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        {children}
      </div>
    </div>
  );
};

export const AlertDialogHeader: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="mb-4">
    {children}
  </div>
);

export const AlertDialogTitle: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <h3 className="text-lg font-semibold mb-2">
    {children}
  </h3>
);

export const AlertDialogDescription: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <p className="text-sm text-gray-600">
    {children}
  </p>
);

export const AlertDialogFooter: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="flex justify-end space-x-2 mt-4">
    {children}
  </div>
);

export const AlertDialogAction: React.FC<{ children: React.ReactNode; onClick?: () => void }> = ({ 
  children, 
  onClick 
}) => {
  const context = useContext(AlertDialogContext);
  if (!context) throw new Error('AlertDialogAction must be used within AlertDialog');
  
  return (
    <button
      className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      onClick={() => {
        onClick?.();
        context.setIsOpen(false);
      }}
    >
      {children}
    </button>
  );
};

export const AlertDialogCancel: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const context = useContext(AlertDialogContext);
  if (!context) throw new Error('AlertDialogCancel must be used within AlertDialog');
  
  return (
    <button
      className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300"
      onClick={() => context.setIsOpen(false)}
    >
      {children}
    </button>
  );
};