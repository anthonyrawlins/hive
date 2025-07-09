import { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Bars3Icon, 
  XMarkIcon,
  FolderIcon,
  Cog6ToothIcon,
  PlayIcon,
  ChartBarIcon,
  HomeIcon,
  UserGroupIcon,
  ComputerDesktopIcon,
  UserCircleIcon,
  ChevronDownIcon,
  AdjustmentsHorizontalIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import UserProfile from './auth/UserProfile';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  current?: boolean;
}

const navigation: NavigationItem[] = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Projects', href: '/projects', icon: FolderIcon },
  { name: 'Workflows', href: '/workflows', icon: Cog6ToothIcon },
  { name: 'Cluster', href: '/cluster', icon: ComputerDesktopIcon },
  { name: 'Executions', href: '/executions', icon: PlayIcon },
  { name: 'Agents', href: '/agents', icon: UserGroupIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: AdjustmentsHorizontalIcon },
];

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const { user } = useAuth();
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Close user menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    }

    if (userMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [userMenuOpen]);

  const navigationWithCurrent = navigation.map(item => ({
    ...item,
    current: location.pathname === item.href || 
             (item.href !== '/' && location.pathname.startsWith(item.href))
  }));

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div 
            className="fixed inset-0 bg-gray-600 bg-opacity-75" 
            onClick={() => setSidebarOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 flex flex-col w-64 bg-white shadow-xl">
            <div className="flex items-center justify-between p-4 border-b">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🐝</span>
                <span className="text-lg font-semibold text-gray-900">Hive</span>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            <nav className="flex-1 px-4 py-4 space-y-1">
              {navigationWithCurrent.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors
                    ${item.current
                      ? 'bg-blue-100 text-blue-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className={`mr-3 h-5 w-5 ${item.current ? 'text-blue-500' : 'text-gray-400'}`} />
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-64 bg-white border-r border-gray-200">
          <div className="flex items-center px-6 py-4 border-b">
            <span className="text-2xl mr-2">🐝</span>
            <span className="text-xl font-semibold text-gray-900">Hive</span>
          </div>
          <nav className="flex-1 px-4 py-4 space-y-1">
            {navigationWithCurrent.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors
                  ${item.current
                    ? 'bg-blue-100 text-blue-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }
                `}
              >
                <item.icon className={`mr-3 h-5 w-5 ${item.current ? 'text-blue-500' : 'text-gray-400'}`} />
                {item.name}
              </Link>
            ))}
          </nav>
          
          {/* Status indicator */}
          <div className="border-t p-4">
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span>All systems operational</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-gray-400 hover:text-gray-600"
              >
                <Bars3Icon className="h-6 w-6" />
              </button>
              <div className="lg:hidden flex items-center space-x-2">
                <span className="text-2xl">🐝</span>
                <span className="text-lg font-semibold text-gray-900">Hive</span>
              </div>
            </div>
            
            {/* User menu */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2 text-sm text-gray-700 hover:text-gray-900 focus:outline-none"
              >
                <UserCircleIcon className="h-8 w-8 text-gray-400" />
                <span className="hidden sm:block">{user?.name}</span>
                <ChevronDownIcon className="h-4 w-4" />
              </button>
              
              {/* User dropdown */}
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 z-50">
                  <UserProfile 
                    isDropdown={true} 
                    onClose={() => setUserMenuOpen(false)} 
                  />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}