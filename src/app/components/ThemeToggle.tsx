/**
 * Theme Toggle Component
 * Allows users to switch between light and dark themes
 */

import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useAppStore();

  return (
    <button
      onClick={toggleTheme}
      className="fixed top-6 right-6 z-50 w-12 h-12 rounded-full bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center hover:bg-white/20 transition-all duration-300 shadow-lg group"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? (
        <Sun 
          size={20} 
          className="text-yellow-300 group-hover:rotate-90 transition-transform duration-300" 
        />
      ) : (
        <Moon 
          size={20} 
          className="text-indigo-600 group-hover:-rotate-12 transition-transform duration-300" 
        />
      )}
    </button>
  );
};
