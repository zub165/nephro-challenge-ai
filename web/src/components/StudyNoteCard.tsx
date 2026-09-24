import { useState } from 'react';
import {
  CheckCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  LightBulbIcon,
  ClipboardDocumentListIcon,
  BeakerIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { parseStudyNote, normalizeNoteText } from '@/lib/noteFormatUtils';
import type { ParsedSection } from '@/lib/noteFormatUtils';

const SECTION_STYLES: Record<string, { icon: typeof LightBulbIcon; className: string }> = {
  clues: {
    icon: ClipboardDocumentListIcon,
    className: 'border-blue-200 bg-blue-50/80 dark:border-blue-800 dark:bg-blue-950/30',
  },
  workup: {
    icon: BeakerIcon,
    className: 'border-indigo-200 bg-indigo-50/80 dark:border-indigo-800 dark:bg-indigo-950/30',
  },
  mechanism: {
    icon: BeakerIcon,
    className: 'border-purple-200 bg-purple-50/80 dark:border-purple-800 dark:bg-purple-950/30',
  },
  distractors: {
    icon: XCircleIcon,
    className: 'border-rose-200 bg-rose-50/60 dark:border-rose-800 dark:bg-rose-950/20',
  },
  case: {
    icon: ClipboardDocumentListIcon,
    className: 'border-stone-200 bg-stone-50/90 dark:border-stone-700 dark:bg-stone-800/40',
  },
  mnemonic: {
    icon: LightBulbIcon,
    className: 'border-amber-200 bg-amber-50/80 dark:border-amber-800 dark:bg-amber-950/30',
  },
  text: {
    icon: ClipboardDocumentListIcon,
    className: 'border-stone-200 bg-white/90 dark:border-stone-700 dark:bg-stone-800/50',
  },
};

function SectionBlock({ section, defaultOpen }: { section: ParsedSection; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen ?? section.type !== 'distractors');
  const style = SECTION_STYLES[section.type] ?? SECTION_STYLES.text;
  const Icon = style.icon;
  const label =
    section.label ||
    (section.type === 'distractors' ? 'Why not the others?' : section.type);

  return (
    <div className={`overflow-hidden rounded-xl border ${style.className}`}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-xs font-bold uppercase tracking-wide text-gray-700 dark:text-gray-300"
      >
        <Icon className="h-4 w-4 flex-shrink-0 opacity-70" />
        <span className="flex-1">{label}</span>
        {open ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
      </button>
      {open && (
        <div className="border-t border-inherit px-4 pb-3 pt-1">
          {section.content && (
            <p className="mb-2 text-sm leading-relaxed text-gray-800 dark:text-stone-200 whitespace-pre-wrap">
              {section.content}
            </p>
          )}
          {section.bullets.length > 0 && (
            <ul className="space-y-1.5">
              {section.bullets.map((b, i) => (
                <li key={i} className="flex gap-2 text-sm leading-relaxed text-gray-700 dark:text-stone-300">
                  <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-teal-500" />
                  <span>{b}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

interface StudyNoteCardProps {
  content: string;
  topicTitle?: string;
  knownPearls?: string[];
}

export default function StudyNoteCard({ content, topicTitle, knownPearls = [] }: StudyNoteCardProps) {
  const parsed = parseStudyNote(content, topicTitle);
  const known = new Set(knownPearls.map(normalizeNoteText));
  const pearls = parsed.pearls.filter((p) => !known.has(normalizeNoteText(p)));

  if (!parsed.isStructured) {
    return (
      <p className="text-sm leading-relaxed text-gray-800 dark:text-stone-200 whitespace-pre-wrap">
        {content}
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {parsed.title && topicTitle !== parsed.title && (
        <h4 className="text-sm font-semibold text-primary-900 dark:text-stone-100">{parsed.title}</h4>
      )}

      {parsed.answer && (
        <div className="flex items-start gap-2 rounded-xl border border-emerald-300 bg-emerald-50 px-4 py-3 dark:border-emerald-800 dark:bg-emerald-950/40">
          <CheckCircleIcon className="mt-0.5 h-5 w-5 flex-shrink-0 text-emerald-600" />
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-emerald-800 dark:text-emerald-300">
              Correct Answer
            </p>
            <p className="mt-0.5 text-sm font-semibold text-emerald-900 dark:text-emerald-100">
              {parsed.answer}
            </p>
          </div>
        </div>
      )}

      {pearls.length > 0 && (
        <div className="space-y-2">
          {pearls.map((pearl, i) => (
            <div
              key={i}
              className="flex gap-2 rounded-xl border border-amber-200 bg-gradient-to-r from-amber-50 to-yellow-50/50 px-3 py-2.5 dark:border-amber-800 dark:from-amber-950/40 dark:to-yellow-950/20"
            >
              <LightBulbIcon className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-600" />
              <p className="text-sm font-medium leading-relaxed text-amber-950 dark:text-amber-100">
                {pearl}
              </p>
            </div>
          ))}
        </div>
      )}

      {parsed.sections.map((section, i) => (
        <SectionBlock
          key={`${section.type}-${i}`}
          section={section}
          defaultOpen={section.type === 'case' || section.type === 'clues'}
        />
      ))}
    </div>
  );
}
