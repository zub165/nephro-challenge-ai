import { ShieldExclamationIcon } from '@heroicons/react/24/outline';

export default function Disclaimer() {
  return (
    <div className="border-t border-gray-200 bg-amber-50 px-4 py-3 dark:border-gray-700 dark:bg-amber-900/20">
      <div className="mx-auto flex max-w-7xl items-center justify-center gap-2 text-xs text-amber-800 dark:text-amber-300">
        <ShieldExclamationIcon className="h-4 w-4 flex-shrink-0" />
        <span>
          For medical education only. Not medical advice. Always consult a qualified
          healthcare professional for clinical decisions.
        </span>
      </div>
    </div>
  );
}
