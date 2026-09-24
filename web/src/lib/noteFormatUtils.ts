/** Parse pasted board-review notes into scannable study sections. */

export type SectionType =
  | 'answer'
  | 'pearl'
  | 'clues'
  | 'workup'
  | 'mechanism'
  | 'distractors'
  | 'case'
  | 'table'
  | 'mnemonic'
  | 'text';

export interface ParsedSection {
  type: SectionType;
  label: string;
  content: string;
  bullets: string[];
}

export function normalizeNoteText(text: string): string {
  return text.trim().toLowerCase().replace(/\s+/g, ' ');
}

export function dedupeStudyNotes<T extends { content: string }>(notes: T[]): T[] {
  const seen = new Set<string>();
  return notes.filter((note) => {
    const key = normalizeNoteText(note.content);
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export interface ParsedStudyNote {
  title: string;
  answer?: string;
  pearls: string[];
  sections: ParsedSection[];
  isStructured: boolean;
}

const SECTION_PATTERNS: { type: SectionType; pattern: RegExp }[] = [
  { type: 'clues', pattern: /^key clues?\b/i },
  { type: 'workup', pattern: /^workup\b/i },
  { type: 'mechanism', pattern: /^mechanism\b/i },
  { type: 'distractors', pattern: /^why not (the )?others?\??/i },
  { type: 'pearl', pattern: /^board pearls?\b/i },
  { type: 'mnemonic', pattern: /^mnemonic\b/i },
  { type: 'table', pattern: /^(?:drug|finding)\b.*\b(?:target|diagnosis)\b/i },
];

const ANSWER_RE =
  /(?:@ |✅ )?(?:correct answer|answer)\s*:\s*([A-F])[.\s)]*\s*([^\n]+)/i;

function splitBullets(text: string): string[] {
  return text
    .split(/\n/)
    .map((line) => line.replace(/^[\s•\-*]+/, '').replace(/^[A-F][.)]\s*/, '').trim())
    .filter(Boolean);
}

function detectSectionHeader(line: string): { type: SectionType; label: string } | null {
  const trimmed = line.trim().replace(/:$/, '');
  for (const { type, pattern } of SECTION_PATTERNS) {
    if (pattern.test(trimmed)) {
      return { type, label: trimmed };
    }
  }
  if (/^pearl\s*:/i.test(trimmed)) {
    return { type: 'pearl', label: 'Pearl' };
  }
  return null;
}

export function parseStudyNote(content: string, topicTitle = ''): ParsedStudyNote {
  const lines = content.replace(/\r\n/g, '\n').split('\n');
  const answerMatch = content.match(ANSWER_RE);
  const answer = answerMatch
    ? `${answerMatch[1]}. ${answerMatch[2].trim()}`
    : undefined;

  const pearls: string[] = [];
  const sections: ParsedSection[] = [];
  let current: ParsedSection | null = null;
  let caseLines: string[] = [];

  const flushCase = () => {
    const text = caseLines.join('\n').trim();
    if (text.length > 40) {
      sections.unshift({ type: 'case', label: 'Clinical vignette', content: text, bullets: [] });
    }
    caseLines = [];
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) continue;

    if (ANSWER_RE.test(line)) continue;

    const header = detectSectionHeader(line);
    if (header) {
      flushCase();
      if (current) sections.push(current);
      current = { type: header.type, label: header.label, content: '', bullets: [] };
      const inline = line.replace(/^[^:]+:\s*/i, '').trim();
      if (inline && inline !== header.label) {
        if (header.type === 'pearl' || header.type === 'mnemonic') {
          pearls.push(inline);
        } else {
          current.bullets.push(inline);
        }
      }
      continue;
    }

    const pearlInline = line.match(/^pearl\s*:\s*(.+)/i);
    if (pearlInline) {
      pearls.push(pearlInline[1].trim());
      continue;
    }

    if (line.match(/^think\s*:/i)) {
      pearls.push(line.replace(/^think\s*:\s*/i, '').trim());
      continue;
    }

    const isBullet =
      /^[•\-*]\s/.test(rawLine) ||
      /^[A-F][.)]\s/.test(line) ||
      (current && current.bullets.length > 0 && line.length < 200);

    if (current) {
      if (isBullet || current.type === 'distractors' || current.type === 'workup') {
        current.bullets.push(line.replace(/^[•\-*]\s*/, ''));
      } else {
        current.content += (current.content ? '\n' : '') + line;
      }
      continue;
    }

    if (line.match(/^a \d{1,3}-year-old/i) || caseLines.length > 0) {
      caseLines.push(line);
    } else if (line.length <= 220 && !line.includes('?')) {
      pearls.push(line);
    } else {
      sections.push({ type: 'text', label: '', content: line, bullets: [] });
    }
  }

  flushCase();
  if (current) sections.push(current);

  for (const sec of sections) {
    if (sec.type === 'pearl') {
      for (const b of sec.bullets) pearls.push(b);
      if (sec.content) pearls.push(sec.content);
    }
  }

  const title =
    topicTitle ||
    (answer ? answer.slice(0, 80) : '') ||
    pearls[0]?.slice(0, 80) ||
    sections.find((s) => s.type === 'case')?.content.slice(0, 80) ||
    'Study note';

  const isStructured = Boolean(
    answer || pearls.length > 0 || sections.some((s) => s.type !== 'text')
  );

  return {
    title,
    answer,
    pearls: [...new Set(pearls.filter(Boolean))],
    sections: sections.filter((s) => s.type !== 'pearl' || s.bullets.length || s.content),
    isStructured,
  };
}

export function isPearlContent(content: string): boolean {
  return content.length <= 220 && !content.includes('\n\n');
}
