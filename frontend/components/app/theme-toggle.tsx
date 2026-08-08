'use client';

import { useTheme } from 'next-themes';
import { MonitorIcon, MoonIcon, SunIcon } from '@phosphor-icons/react';
import { cn } from '@/lib/shadcn/utils';

interface ThemeToggleProps {
  className?: string;
}

export function ThemeToggle({ className }: ThemeToggleProps) {
  const { theme, setTheme } = useTheme();

  return (
    <div
      className={cn(
        "flex overflow-hidden rounded-full border border-green-300 bg-white/80 shadow backdrop-blur-md",
        className
      )}
    >
      <span className="sr-only">Theme Toggle</span>

      <button
        type="button"
        onClick={() => setTheme("light")}
        className="px-3 py-2 transition hover:bg-green-100"
      >
        <span className="sr-only">Light Theme</span>

        <SunIcon
          suppressHydrationWarning
          size={18}
          weight="fill"
          className={cn(
            theme === "light"
              ? "text-yellow-500"
              : "text-gray-400"
          )}
        />
      </button>

      <button
        type="button"
        onClick={() => setTheme("dark")}
        className="border-l border-green-200 px-3 py-2 transition hover:bg-green-100"
      >
        <span className="sr-only">Dark Theme</span>

        <MoonIcon
          suppressHydrationWarning
          size={18}
          weight="fill"
          className={cn(
            theme === "dark"
              ? "text-green-700"
              : "text-gray-400"
          )}
        />
      </button>

      <button
        type="button"
        onClick={() => setTheme("system")}
        className="border-l border-green-200 px-3 py-2 transition hover:bg-green-100"
      >
        <span className="sr-only">System Theme</span>

        <MonitorIcon
          suppressHydrationWarning
          size={18}
          weight="fill"
          className={cn(
            theme === "system"
              ? "text-green-700"
              : "text-gray-400"
          )}
        />
      </button>
    </div>
  );
}
