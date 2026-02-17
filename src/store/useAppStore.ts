/**
 * VidyaSetu AI - Zustand Store
 * Global state management for the application
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Subject = 'Math' | 'Science' | 'English' | 'Hindi' | 'GK';

export interface StudentProfile {
  student_id: string;
  name: string;
  grade: number;
  subject: Subject;
  iq_scores: Record<string, number>;
  eq_scores: Record<string, number>;
  learning_style: string;
  xp: number;
  textbook_id?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  timestamp: string;
  thoughtExpanded?: boolean;
  agentSteps?: Array<{
    agent: string;
    action: string;
  }>;
  safety_verified?: boolean;
}

export interface AppState {
  // Student state
  student: StudentProfile | null;
  setStudent: (student: StudentProfile) => void;

  // Chat state
  messages: ChatMessage[];
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  toggleThought: (messageId: string) => void;

  // UI state
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  currentScreen: 'welcome' | 'game' | 'upload' | 'chat';
  setCurrentScreen: (screen: 'welcome' | 'game' | 'upload' | 'chat') => void;

  // Upload state
  isUploading: boolean;
  uploadProgress: number;
  setIsUploading: (uploading: boolean) => void;
  setUploadProgress: (progress: number | ((prev: number) => number)) => void;

  // XP and game state
  addXp: (amount: number) => void;

  // Theme
  theme: 'dark' | 'light';
  toggleTheme: () => void;

  // Reset
  reset: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial state
      student: null,
      messages: [],
      isLoading: false,
      currentScreen: 'welcome',
      isUploading: false,
      uploadProgress: 0,
      theme: 'dark',

      // Student actions
      setStudent: (student) => set({ student }),

      // Chat actions
      addMessage: (message) => set((state) => ({
        messages: [...state.messages, message]
      })),

      clearMessages: () => set({ messages: [] }),

      toggleThought: (messageId) => set((state) => ({
        messages: state.messages.map(msg =>
          msg.id === messageId
            ? { ...msg, thoughtExpanded: !msg.thoughtExpanded }
            : msg
        )
      })),

      // UI actions
      setIsLoading: (loading) => set({ isLoading: loading }),
      setCurrentScreen: (screen) => set({ currentScreen: screen }),

      // Upload actions
      setIsUploading: (uploading) => set({ isUploading: uploading }),
      setUploadProgress: (progress) => set((state) => ({
        uploadProgress: typeof progress === 'function' ? progress(state.uploadProgress) : progress
      })),

      // XP action
      addXp: (amount) => set((state) => ({
        student: state.student
          ? { ...state.student, xp: state.student.xp + amount }
          : null
      })),

      // Theme action
      toggleTheme: () => set((state) => {
        const newTheme = state.theme === 'dark' ? 'light' : 'dark';
        // Update document class for CSS
        document.documentElement.classList.toggle('dark', newTheme === 'dark');
        document.documentElement.classList.toggle('light', newTheme === 'light');
        return { theme: newTheme };
      }),

      // Reset
      reset: () => set({
        student: null,
        messages: [],
        isLoading: false,
        currentScreen: 'welcome',
        isUploading: false,
        uploadProgress: 0,
      })
    }),
    {
      name: 'vidyasetu-storage',
      partialize: (state) => ({
        student: state.student,
        theme: state.theme,
        currentScreen: state.currentScreen
      })
    }
  )
);
