import { useState, useMemo } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/axios';
import { unwrapList } from '@/lib/apiMappers';
import { dedupeStudyNotes } from '@/lib/noteFormatUtils';
import { useNotesStore } from '@/store/notesStore';
import type { Chapter, NotesReview, OrganizeNotesResponse, StudyNote } from '@/types';
import PearlCard from '@/components/PearlCard';
import StudyNoteCard from '@/components/StudyNoteCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import toast from 'react-hot-toast';
import {
  BookOpenIcon,
  ClipboardDocumentIcon,
  BookmarkIcon,
  TrashIcon,
  ArrowRightIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ListBulletIcon,
  DocumentTextIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';

type Tab = 'paste' | 'book';

const PEARL_MAX = 220;

interface BookChapter {
  key: string;
  label: string;
  title: string;
  order: number;
  notes: StudyNote[];
  pearls: StudyNote[];
  clinicalNotes: StudyNote[];
  chapter?: Chapter;
}

function splitNotes(notes: StudyNote[]) {
  const unique = dedupeStudyNotes(notes);
  const pearls = unique.filter((n) => n.content.length <= PEARL_MAX);
  const clinicalNotes = unique.filter((n) => n.content.length > PEARL_MAX);
  return { pearls, clinicalNotes };
}

export default function Notes() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<Tab>('paste');
  const [activeSection, setActiveSection] = useState<string>('toc');
  const { draftPaste, setDraftPaste, setCachedReview, clearDraft, cachedReview } = useNotesStore();

  const { data: review, isLoading, error, refetch } = useQuery<NotesReview>({
    queryKey: ['notes-review'],
    queryFn: () =>
      api.get('/notes/review/').then((r) => {
        setCachedReview(r.data);
        return r.data as NotesReview;
      }),
    placeholderData: cachedReview ?? undefined,
  });

  const { data: chapters } = useQuery<Chapter[]>({
    queryKey: ['chapters'],
    queryFn: () => api.get('/chapters/').then((r) => unwrapList<Chapter>(r.data)),
  });

  const saveMutation = useMutation({
    mutationFn: (text: string) =>
      api.post<OrganizeNotesResponse>('/notes/organize/', { text }).then((r) => r.data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['notes-review'] });
      clearDraft();
      setTab('book');
      if (data.notes[0]?.chapter_slug) {
        setActiveSection(data.notes[0].chapter_slug!);
      }
      const skipped = data.skipped_duplicates ?? 0;
      if (data.total === 0 && skipped > 0) {
        toast('All notes were already in your book — no duplicates added', { icon: 'ℹ️' });
      } else if (skipped > 0) {
        toast.success(`Saved ${data.total} note${data.total === 1 ? '' : 's'} (${skipped} duplicate${skipped === 1 ? '' : 's'} skipped)`);
      } else {
        toast.success(`Saved ${data.total} note${data.total === 1 ? '' : 's'} to your book`);
      }
    },
    onError: (err: { response?: { data?: { message?: string; detail?: string } } }) => {
      toast.error(err.response?.data?.message || err.response?.data?.detail || 'Could not save to book');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/notes/${id}/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes-review'] });
      toast.success('Removed from book');
    },
    onError: () => toast.error('Failed to delete'),
  });

  const moveMutation = useMutation({
    mutationFn: ({ id, chapterId }: { id: string; chapterId: string | null }) =>
      api.patch(`/notes/${id}/`, { chapter: chapterId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes-review'] });
      toast.success('Moved to chapter');
    },
    onError: () => toast.error('Failed to move note'),
  });

  const dedupeMutation = useMutation({
    mutationFn: () => api.post<{ removed: number }>('/notes/dedupe/').then((r) => r.data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['notes-review'] });
      if (data.removed > 0) {
        toast.success(`Removed ${data.removed} duplicate${data.removed === 1 ? '' : 's'}`);
      } else {
        toast('No duplicates found', { icon: 'ℹ️' });
      }
    },
    onError: () => toast.error('Could not remove duplicates'),
  });

  const displayReview = review ?? cachedReview;

  const bookChapters = useMemo((): BookChapter[] => {
    const bySlug = new Map<string, StudyNote[]>();
    for (const group of displayReview?.chapters ?? []) {
      bySlug.set(group.chapter.slug, group.notes);
    }
    const list: BookChapter[] = (chapters ?? []).map((ch) => {
      const notes = dedupeStudyNotes(bySlug.get(ch.slug) ?? []);
      const { pearls, clinicalNotes } = splitNotes(notes);
      return {
        key: ch.slug,
        label: `Ch. ${ch.order_index}`,
        title: ch.title,
        order: ch.order_index,
        notes,
        pearls,
        clinicalNotes,
        chapter: ch,
      };
    });
    if (displayReview?.uncategorized?.length) {
      const uncategorized = dedupeStudyNotes(displayReview.uncategorized);
      const { pearls, clinicalNotes } = splitNotes(uncategorized);
      list.push({
        key: 'other',
        label: 'Other',
        title: 'Uncategorized Notes',
        order: 99,
        notes: uncategorized,
        pearls,
        clinicalNotes,
      });
    }
    return list;
  }, [displayReview, chapters]);

  const chaptersWithContent = bookChapters.filter((c) => c.notes.length > 0);
  const activeChapter = bookChapters.find((c) => c.key === activeSection);
  const activeIndex = chaptersWithContent.findIndex((c) => c.key === activeSection);

  const goPrev = () => {
    if (activeIndex > 0) setActiveSection(chaptersWithContent[activeIndex - 1].key);
  };
  const goNext = () => {
    if (activeIndex >= 0 && activeIndex < chaptersWithContent.length - 1) {
      setActiveSection(chaptersWithContent[activeIndex + 1].key);
    }
  };

  const totalPearls = bookChapters.reduce((n, c) => n + c.pearls.length, 0);
  const totalClinical = bookChapters.reduce((n, c) => n + c.clinicalNotes.length, 0);
  const duplicateCount = useMemo(() => {
    if (!displayReview) return 0;
    const all = [
      ...displayReview.chapters.flatMap((g) => g.notes),
      ...displayReview.uncategorized,
    ];
    return all.length - dedupeStudyNotes(all).length;
  }, [displayReview]);

  return (
    <div className="space-y-6">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-900 via-primary-800 to-teal-900 p-8 text-white shadow-lg">
        <div className="relative">
          <p className="text-xs font-semibold uppercase tracking-widest text-teal-300">Personal Board Notebook</p>
          <h1 className="mt-2 text-3xl font-bold">My Nephrology Book</h1>
          <p className="mt-2 max-w-2xl text-sm text-teal-100/90">
            Organized by chapter — <strong>Pearls</strong> first, then <strong>Clinical Notes</strong>. Use the table of contents to flip between chapters like a board review book.
          </p>
          <div className="mt-4 flex flex-wrap gap-3 text-sm">
            <span className="rounded-full bg-white/10 px-3 py-1">{displayReview?.total ?? 0} entries</span>
            <span className="rounded-full bg-amber-500/25 px-3 py-1">{totalPearls} pearls</span>
            <span className="rounded-full bg-white/10 px-3 py-1">{totalClinical} clinical notes</span>
            {duplicateCount > 0 && tab === 'book' && (
              <button
                type="button"
                onClick={() => dedupeMutation.mutate()}
                disabled={dedupeMutation.isPending}
                className="rounded-full bg-red-500/30 px-3 py-1 font-medium hover:bg-red-500/40"
              >
                {dedupeMutation.isPending ? 'Cleaning...' : `Remove ${duplicateCount} duplicate${duplicateCount === 1 ? '' : 's'}`}
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="flex gap-2">
        {([
          { key: 'paste' as const, label: 'Paste Notes', icon: ClipboardDocumentIcon },
          { key: 'book' as const, label: 'Read My Book', icon: BookOpenIcon },
        ]).map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              tab === t.key
                ? 'bg-primary-900 text-white dark:bg-teal-800'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400'
            }`}
          >
            <t.icon className="h-4 w-4" />
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'paste' ? (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="card space-y-4">
          <h2 className="text-lg font-semibold">Paste your notes</h2>
          <p className="text-sm text-gray-500">
            Paste MCQ explanations as-is — the app splits by <strong>Question #</strong>, <strong>Correct Answer</strong>, and <strong>Board Pearl</strong> sections automatically.
          </p>
          <div className="rounded-lg border border-teal-200 bg-teal-50/50 p-3 text-xs text-teal-900 dark:border-teal-800 dark:bg-teal-950/30 dark:text-teal-100">
            <p className="font-semibold">Best format for learning:</p>
            <pre className="mt-1 whitespace-pre-wrap font-mono text-[11px] leading-relaxed opacity-90">{`Question 210 — Obstructive uropathy
Correct Answer: A. Obstructive uropathy
Key clues
Rising Cr + bland UA + hydronephrosis
Prior Hodgkin lymphoma
Board Pearl
Retroperitoneal fibrosis → bilateral ureteral obstruction`}</pre>
          </div>
          <textarea
            value={draftPaste}
            onChange={(e) => setDraftPaste(e.target.value)}
            placeholder={`Paste MCQ explanations here — no need to reformat.\n\nQuestion 211 — Lithium overdose\nCorrect Answer: D. Polyethylene glycol (PEG)\nBoard Pearl: SR lithium → whole-bowel irrigation with PEG; charcoal does NOT work`}
            className="input-field min-h-[280px] resize-y font-mono text-sm"
          />
          <button
            onClick={() => draftPaste.trim() && saveMutation.mutate(draftPaste.trim())}
            disabled={saveMutation.isPending || !draftPaste.trim()}
            className="btn-teal gap-2"
          >
            <BookmarkIcon className="h-4 w-4" />
            {saveMutation.isPending ? 'Saving...' : 'Save to My Book'}
          </button>
        </motion.div>
      ) : isLoading && !displayReview ? (
        <LoadingSpinner text="Opening your book..." />
      ) : error ? (
        <div className="py-16 text-center">
          <button onClick={() => refetch()} className="btn-primary text-sm">Retry</button>
        </div>
      ) : !displayReview?.total ? (
        <div className="py-16 text-center">
          <BookOpenIcon className="mx-auto h-12 w-12 text-gray-300" />
          <p className="mt-4 font-medium">Your book is empty</p>
          <button onClick={() => setTab('paste')} className="btn-primary mt-4 text-sm">Paste Notes</button>
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
          {/* Table of Contents */}
          <aside className="card sticky top-20 h-fit max-h-[calc(100vh-8rem)] overflow-y-auto p-0">
            <div className="border-b border-gray-100 bg-primary-900 px-4 py-3 dark:border-gray-700">
              <div className="flex items-center gap-2 text-white">
                <ListBulletIcon className="h-5 w-5" />
                <h2 className="text-sm font-bold uppercase tracking-wide">Contents</h2>
              </div>
            </div>
            <nav className="p-2">
              <button
                type="button"
                onClick={() => setActiveSection('toc')}
                className={`mb-1 flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition-colors ${
                  activeSection === 'toc'
                    ? 'bg-teal-100 font-semibold text-teal-900 dark:bg-teal-900/40 dark:text-teal-100'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
              >
                <span>Table of Contents</span>
              </button>
              {bookChapters.map((ch) => {
                if (ch.notes.length === 0) return null;
                return (
                  <button
                    key={ch.key}
                    type="button"
                    onClick={() => setActiveSection(ch.key)}
                    className={`mb-0.5 flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left text-sm transition-colors ${
                      activeSection === ch.key
                        ? 'bg-teal-100 font-semibold text-teal-900 dark:bg-teal-900/40 dark:text-teal-100'
                        : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                  >
                    <span className="min-w-0 truncate">
                      <span className="text-xs text-gray-400">{ch.label}</span>{' '}
                      {ch.title}
                    </span>
                    <span className="ml-2 flex-shrink-0 text-xs text-gray-400">
                      {ch.pearls.length > 0 && (
                        <span className="text-amber-600">{ch.pearls.length}★</span>
                      )}
                      {ch.clinicalNotes.length > 0 && (
                        <span className="ml-1">{ch.clinicalNotes.length}¶</span>
                      )}
                    </span>
                  </button>
                );
              })}
            </nav>
            <div className="border-t border-gray-100 px-4 py-3 text-xs text-gray-400 dark:border-gray-700">
              ★ pearls · ¶ clinical notes
            </div>
          </aside>

          {/* Book page */}
          <div className="min-w-0">
            <AnimatePresence mode="wait">
              {activeSection === 'toc' ? (
                <motion.div
                  key="toc"
                  initial={{ opacity: 0, x: 12 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  className="rounded-2xl border border-stone-200 bg-gradient-to-br from-stone-50 to-amber-50/30 p-8 shadow-inner dark:border-stone-700 dark:from-stone-900 dark:to-amber-950/20"
                >
                  <h2 className="text-2xl font-bold text-primary-900 dark:text-stone-100">
                    Nephrology Board Review Book
                  </h2>
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    {displayReview?.total} entries across {chaptersWithContent.length} chapters
                  </p>
                  <ol className="mt-8 space-y-3">
                    {chaptersWithContent.map((ch, i) => (
                      <li key={ch.key}>
                        <button
                          type="button"
                          onClick={() => setActiveSection(ch.key)}
                          className="group flex w-full items-center gap-4 rounded-xl border border-stone-200/80 bg-white/80 px-4 py-3 text-left transition-all hover:border-teal-300 hover:shadow-md dark:border-stone-700 dark:bg-stone-800/50"
                        >
                          <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-primary-900 text-sm font-bold text-white">
                            {i + 1}
                          </span>
                          <div className="min-w-0 flex-1">
                            <p className="font-semibold text-gray-900 dark:text-stone-100">{ch.title}</p>
                            <p className="text-xs text-gray-500">
                              {ch.pearls.length} pearl{ch.pearls.length !== 1 ? 's' : ''} ·{' '}
                              {ch.clinicalNotes.length} clinical note{ch.clinicalNotes.length !== 1 ? 's' : ''}
                            </p>
                          </div>
                          <ArrowRightIcon className="h-4 w-4 text-gray-400 group-hover:text-teal-600" />
                        </button>
                      </li>
                    ))}
                  </ol>
                </motion.div>
              ) : activeChapter ? (
                <BookPage
                  key={activeChapter.key}
                  chapter={activeChapter}
                  chapters={chapters || []}
                  onDelete={(id) => deleteMutation.mutate(id)}
                  onMove={(id, chapterId) => moveMutation.mutate({ id, chapterId })}
                  onPrev={activeIndex > 0 ? goPrev : undefined}
                  onNext={activeIndex < chaptersWithContent.length - 1 ? goNext : undefined}
                  pageNum={activeIndex + 1}
                  totalPages={chaptersWithContent.length}
                />
              ) : null}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
}

function BookPage({
  chapter,
  chapters,
  onDelete,
  onMove,
  onPrev,
  onNext,
  pageNum,
  totalPages,
}: {
  chapter: BookChapter;
  chapters: Chapter[];
  onDelete: (id: string) => void;
  onMove: (id: string, chapterId: string | null) => void;
  onPrev?: () => void;
  onNext?: () => void;
  pageNum: number;
  totalPages: number;
}) {
  return (
    <motion.article
      initial={{ opacity: 0, x: 12 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0 }}
      className="overflow-hidden rounded-2xl border border-stone-200 bg-gradient-to-br from-stone-50 via-white to-amber-50/20 shadow-lg dark:border-stone-700 dark:from-stone-900 dark:via-stone-900 dark:to-amber-950/10"
    >
      {/* Chapter header */}
      <header className="border-b border-stone-200 bg-primary-900 px-6 py-5 text-white dark:border-stone-700">
        <p className="text-xs font-semibold uppercase tracking-widest text-teal-300">
          Chapter {chapter.order < 99 ? chapter.order : '—'} · Page {pageNum} of {totalPages}
        </p>
        <h2 className="mt-1 text-2xl font-bold">{chapter.title}</h2>
        {chapter.chapter?.description && (
          <p className="mt-2 text-sm text-teal-100/80">{chapter.chapter.description}</p>
        )}
      </header>

      <div className="space-y-8 p-6 sm:p-8">
        {/* Pearls section */}
        <section>
          <div className="mb-4 flex items-center gap-2 border-b border-amber-200 pb-2 dark:border-amber-800">
            <LightBulbIcon className="h-5 w-5 text-amber-600" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-amber-800 dark:text-amber-300">
              Board Pearls
            </h3>
            <span className="ml-auto text-xs text-gray-400">{chapter.pearls.length}</span>
          </div>
          {chapter.pearls.length === 0 ? (
            <p className="text-sm italic text-gray-400">No pearls in this chapter yet. Add short one-liners when you paste notes.</p>
          ) : (
            <ol className="space-y-3">
              {chapter.pearls.map((note, i) => (
                <li key={note.id} className="flex gap-3">
                  <span className="mt-1 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-amber-500/20 text-xs font-bold text-amber-800 dark:text-amber-300">
                    {i + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <PearlCard
                      item={{
                        topic: note.topic_title || 'Pearl',
                        pearl: note.content,
                        source: 'my_book',
                      }}
                      compact
                    />
                    <NoteActions note={note} chapters={chapters} onDelete={onDelete} onMove={onMove} />
                  </div>
                </li>
              ))}
            </ol>
          )}
        </section>

        {/* Clinical notes section */}
        <section>
          <div className="mb-4 flex items-center gap-2 border-b border-gray-200 pb-2 dark:border-gray-700">
            <DocumentTextIcon className="h-5 w-5 text-gray-500" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-gray-700 dark:text-gray-300">
              Case Reviews & MCQs
            </h3>
            <span className="ml-auto text-xs text-gray-400">{chapter.clinicalNotes.length}</span>
          </div>
          {chapter.clinicalNotes.length === 0 ? (
            <p className="text-sm italic text-gray-400">No case reviews in this chapter yet.</p>
          ) : (
            <ol className="space-y-4">
              {chapter.clinicalNotes.map((note, i) => (
                <li key={note.id} className="flex gap-3">
                  <span className="mt-2 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-gray-200 text-xs font-bold text-gray-600 dark:bg-gray-700 dark:text-gray-300">
                    {i + 1}
                  </span>
                  <div className="min-w-0 flex-1 rounded-xl border border-stone-200 bg-white/90 p-4 dark:border-stone-700 dark:bg-stone-800/50">
                    {note.topic_title && (
                      <p className="mb-3 text-sm font-bold text-primary-900 dark:text-stone-100">
                        {note.topic_title}
                      </p>
                    )}
                    <StudyNoteCard
                      content={note.content}
                      topicTitle={note.topic_title}
                      knownPearls={chapter.pearls.map((p) => p.content)}
                    />
                    <NoteActions note={note} chapters={chapters} onDelete={onDelete} onMove={onMove} />
                  </div>
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>

      {/* Chapter footer */}
      <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-stone-200 bg-stone-100/80 px-6 py-4 dark:border-stone-700 dark:bg-stone-800/50">
        <div className="flex gap-2">
          {onPrev && (
            <button type="button" onClick={onPrev} className="btn-outline gap-1 text-xs">
              <ChevronLeftIcon className="h-4 w-4" /> Prev
            </button>
          )}
          {onNext && (
            <button type="button" onClick={onNext} className="btn-outline gap-1 text-xs">
              Next <ChevronRightIcon className="h-4 w-4" />
            </button>
          )}
        </div>
        {chapter.chapter && (
          <div className="flex flex-wrap gap-3">
            <Link to={`/pearls?chapter=${chapter.key}`} className="text-xs font-medium text-amber-700 dark:text-amber-400">
              Curated pearls
            </Link>
            <Link to={`/chapters/${chapter.key}`} className="text-xs font-medium text-teal-700 dark:text-teal-400">
              Chapter content
            </Link>
            <Link to={`/quiz/chapter/${chapter.chapter.id}`} className="text-xs font-medium text-teal-700 dark:text-teal-400">
              Practice MCQs →
            </Link>
          </div>
        )}
      </footer>
    </motion.article>
  );
}

function NoteActions({
  note,
  chapters,
  onDelete,
  onMove,
}: {
  note: StudyNote;
  chapters: Chapter[];
  onDelete: (id: string) => void;
  onMove: (id: string, chapterId: string | null) => void;
}) {
  return (
    <div className="mt-3 flex flex-wrap items-center gap-2">
      <select
        value={note.chapter ?? ''}
        onChange={(e) => onMove(note.id, e.target.value || null)}
        className="select-field max-w-[200px] text-xs"
        aria-label="Move to chapter"
      >
        <option value="">Other</option>
        {chapters.map((c) => (
          <option key={c.id} value={c.id}>{c.title}</option>
        ))}
      </select>
      <button
        type="button"
        onClick={() => onDelete(note.id)}
        className="rounded-lg p-1.5 text-gray-400 hover:text-red-600"
        title="Delete"
      >
        <TrashIcon className="h-4 w-4" />
      </button>
    </div>
  );
}
