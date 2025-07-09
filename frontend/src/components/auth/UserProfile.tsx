import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

interface UserProfileProps {
  isDropdown?: boolean;
  onClose?: () => void;
}

export default function UserProfile({ isDropdown = false, onClose }: UserProfileProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(user?.name || '');

  const handleSave = () => {
    // In a real app, this would make an API call to update user profile
    console.log('Saving user profile:', { name: editedName });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedName(user?.name || '');
    setIsEditing(false);
  };

  const handleLogout = () => {
    logout();
    onClose?.();
  };

  if (!user) return null;

  if (isDropdown) {
    return (
      <div className="w-64 bg-white rounded-lg shadow-lg border p-4">
        {/* User Info */}
        <div className="flex items-center space-x-3 pb-4 border-b">
          <UserCircleIcon className="h-12 w-12 text-gray-400" />
          <div>
            <p className="font-medium text-gray-900">{user.name}</p>
            <p className="text-sm text-gray-500">@{user.username}</p>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
              {user.role}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="pt-4 space-y-2">
          <button
            onClick={() => {
              navigate('/profile');
              onClose?.();
            }}
            className="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
          >
            <Cog6ToothIcon className="h-4 w-4 mr-3" />
            View Profile
          </button>
          <button
            onClick={handleLogout}
            className="w-full flex items-center px-3 py-2 text-sm text-red-700 hover:bg-red-50 rounded-md"
          >
            <ArrowRightOnRectangleIcon className="h-4 w-4 mr-3" />
            Sign out
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white shadow rounded-lg">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">User Profile</h2>
          <p className="text-sm text-gray-500">Manage your account settings and preferences</p>
        </div>

        {/* Profile Content */}
        <div className="px-6 py-4">
          {/* Avatar and Basic Info */}
          <div className="flex items-center space-x-6 mb-6">
            <div className="relative">
              <UserCircleIcon className="h-24 w-24 text-gray-400" />
              <button className="absolute bottom-0 right-0 bg-blue-600 text-white rounded-full p-2 hover:bg-blue-700">
                <PencilIcon className="h-4 w-4" />
              </button>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-900">{user.name}</h3>
              <p className="text-gray-600">@{user.username}</p>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 mt-2">
                {user.role}
              </span>
            </div>
          </div>

          {/* Profile Fields */}
          <div className="space-y-6">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              {isEditing ? (
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={editedName}
                    onChange={(e) => setEditedName(e.target.value)}
                    className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <button
                    onClick={handleSave}
                    className="p-2 text-green-600 hover:text-green-800"
                  >
                    <CheckIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={handleCancel}
                    className="p-2 text-red-600 hover:text-red-800"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <span className="text-gray-900">{user.name}</span>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>

            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <span className="text-gray-900">{user.username}</span>
              <p className="text-xs text-gray-500 mt-1">Username cannot be changed</p>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <span className="text-gray-900">{user.email || 'Not set'}</span>
            </div>

            {/* Role */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role
              </label>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                {user.role}
              </span>
              <p className="text-xs text-gray-500 mt-1">Role is managed by system administrators</p>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex space-x-4">
              <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm font-medium">
                Change Password
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 text-sm font-medium"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}