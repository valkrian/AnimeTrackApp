/**
 * Error Toast Notification Component
 * Displays backend error messages with dismissible notifications
 * Integrates with TanStack Query error handling
 * Requirements: 6.3
 */

'use client';

import { useEffect, useState } from 'react';
import { ErrorToastProps } from '../types/anime';

export default function ErrorToast({ error, onDismiss }: ErrorToastProps) {
  const [isVisible, setIsVisible] = useState(true);
  const [isExiting, setIsExiting] = useState(false);

  const handleDismiss = () => {
    setIsExiting(true);
    setTimeout(() => {
      setIsVisible(false);
      onDismiss();
    }, 300); // Match animation duration
  };

  // Auto-dismiss after 5 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      handleDismiss();
    }, 5000);

    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!isVisible) {
    return null;
  }

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-md transition-all duration-300 ${
        isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0'
      }`}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="backdrop-blur-md bg-red-500/20 border border-red-500/30 rounded-xl p-4 shadow-2xl">
        <div className="flex items-start gap-3">
          {/* Error Icon */}
          <div className="flex-shrink-0">
            <svg
              className="w-6 h-6 text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          {/* Error Content */}
          <div className="flex-1 min-w-0">
            <h3 className="text-white font-semibold text-sm mb-1">Error</h3>
            <p className="text-white/90 text-sm break-words">{error.message}</p>
            {error.status > 0 && (
              <p className="text-white/60 text-xs mt-1">Status Code: {error.status}</p>
            )}
          </div>

          {/* Dismiss Button */}
          <button
            onClick={handleDismiss}
            className="flex-shrink-0 text-white/60 hover:text-white transition-colors"
            aria-label="Dismiss notification"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Progress Bar */}
        <div className="mt-3 h-1 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-red-400 rounded-full animate-progress"
            style={{ animation: 'progress 5s linear forwards' }}
          />
        </div>
      </div>
    </div>
  );
}

/**
 * Error Toast Container Component
 * Manages multiple error toasts
 */
interface ErrorToastContainerProps {
  errors: Array<{ id: string; error: ErrorToastProps['error'] }>;
  onDismiss: (id: string) => void;
}

export function ErrorToastContainer({ errors, onDismiss }: ErrorToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {errors.map(({ id, error }) => (
        <ErrorToast key={id} error={error} onDismiss={() => onDismiss(id)} />
      ))}
    </div>
  );
}
