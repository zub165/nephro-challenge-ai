import { LightBulbIcon, SparklesIcon } from '@heroicons/react/24/outline';

export interface PearlItem {
  topic: string;
  pearl: string;
  mnemonic?: string | null;
  source?: 'curated' | 'mcq' | 'my_book';
  note_id?: string;
  reference?: string;
  verified?: boolean;
}

interface PearlCardProps {
  item: PearlItem;
  compact?: boolean;
}

const SOURCE_LABEL: Record<string, string> = {
  curated: 'Board Pearl',
  mcq: 'From MCQ',
  my_book: 'Your Pearl',
};

export default function PearlCard({ item, compact }: PearlCardProps) {
  return (
    <div
      className={`relative overflow-hidden rounded-xl border border-amber-200/80 bg-gradient-to-br from-amber-50 via-yellow-50/80 to-orange-50/50 dark:border-amber-800/50 dark:from-amber-950/40 dark:via-amber-900/20 dark:to-orange-950/20 ${
        compact ? 'p-3' : 'p-4'
      }`}
    >
      <div className="absolute right-3 top-3 opacity-20">
        <LightBulbIcon className="h-8 w-8 text-amber-600" />
      </div>
      <div className="relative">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2 py-0.5 text-xs font-bold uppercase tracking-wide text-amber-800 dark:text-amber-300">
            <SparklesIcon className="h-3 w-3" />
            {item.source ? SOURCE_LABEL[item.source] ?? 'Pearl' : 'Pearl'}
          </span>
          {item.mnemonic && (
            <span className="rounded-full bg-primary-900/10 px-2 py-0.5 text-xs font-semibold text-primary-900 dark:bg-white/10 dark:text-amber-100">
              {item.mnemonic}
            </span>
          )}
        </div>
        <p className="text-xs font-semibold uppercase tracking-wide text-amber-900/70 dark:text-amber-400/90">
          {item.topic}
        </p>
        <p className={`mt-1.5 font-medium leading-relaxed text-gray-900 dark:text-amber-50 ${compact ? 'text-sm' : 'text-base'}`}>
          {item.pearl}
        </p>
        {item.reference && (
          <p className="mt-2 border-t border-amber-200/60 pt-2 text-xs leading-snug text-amber-900/60 dark:border-amber-800/40 dark:text-amber-400/70">
            <span className="font-semibold">Ref: </span>
            {item.reference}
          </p>
        )}
        {item.verified && item.source === 'curated' && (
          <span className="mt-1 inline-block text-[10px] font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
            Literature verified
          </span>
        )}
      </div>
    </div>
  );
}
