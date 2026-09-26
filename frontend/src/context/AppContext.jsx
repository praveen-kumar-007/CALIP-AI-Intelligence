import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [toasts, setToasts] = useState([]);

  // Toast notification dispatcher
  const showToast = (message, type = 'info', duration = 4000) => {
    const id = Date.now() + Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  };

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const refreshPlatformData = async () => {
    try {
      setLoadingStats(true);
      const [healthData, statsData] = await Promise.allSettled([
        api.getHealth(),
        api.getPlatformStats(),
      ]);

      if (healthData.status === 'fulfilled') {
        setHealth(healthData.value);
      }
      if (statsData.status === 'fulfilled') {
        setStats(statsData.value);
      }
    } catch (err) {
      console.error('Error refreshing platform stats:', err);
    } finally {
      setLoadingStats(false);
    }
  };

  useEffect(() => {
    refreshPlatformData();
  }, []);

  return (
    <AppContext.Provider
      value={{
        stats,
        health,
        loadingStats,
        refreshPlatformData,
        showToast,
        toasts,
        removeToast,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
