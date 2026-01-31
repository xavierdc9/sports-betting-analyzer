"use client";

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div className="bg-red-900/30 border border-red-700/50 rounded p-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <svg
          className="w-5 h-5 text-red-400 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-sm text-red-300">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-sm text-red-400 hover:text-red-300 border border-red-700/50 rounded px-3 py-1 transition-colors flex-shrink-0 ml-4"
        >
          Retry
        </button>
      )}
    </div>
  );
}
