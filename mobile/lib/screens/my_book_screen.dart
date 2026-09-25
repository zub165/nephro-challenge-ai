import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../models/study_note.dart';
import '../providers/notes_provider.dart';
import '../widgets/loading_shimmer.dart';

class MyBookScreen extends StatefulWidget {
  const MyBookScreen({super.key});

  @override
  State<MyBookScreen> createState() => _MyBookScreenState();
}

class _MyBookScreenState extends State<MyBookScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _pasteController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final notes = context.read<NotesProvider>();
      notes.loadDraft();
      notes.loadReview();
      _pasteController.text = notes.draftPaste;
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _pasteController.dispose();
    super.dispose();
  }

  Future<void> _savePaste() async {
    final notes = context.read<NotesProvider>();
    notes.setDraftPaste(_pasteController.text);
    final result = await notes.savePastedNotes();
    if (!mounted) return;
    if (result == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(notes.error ?? 'Could not save notes'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }
    if (result.total == 0 && result.skippedDuplicates > 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Notes already in your book')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Saved ${result.total} note${result.total == 1 ? '' : 's'} to your book',
          ),
        ),
      );
      _tabController.animateTo(1);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.content_paste), text: 'Paste'),
            Tab(icon: Icon(Icons.auto_stories), text: 'My Book'),
          ],
        ),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildPasteTab(),
              _buildBookTab(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPasteTab() {
    return Consumer<NotesProvider>(
      builder: (context, notes, _) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Paste MCQ explanations',
                style: GoogleFonts.inter(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Paste as-is — the app splits Question #, Correct Answer, Board Pearl, and case reviews into chapters automatically.',
                style: GoogleFonts.inter(
                  fontSize: 13,
                  color: Colors.grey[600],
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _pasteController,
                onChanged: notes.setDraftPaste,
                maxLines: 14,
                decoration: InputDecoration(
                  hintText:
                      'Question 211 — Lithium overdose\nCorrect Answer: D. PEG\nBoard Pearl: SR lithium → whole-bowel irrigation',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  alignLabelWithHint: true,
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: notes.isSaving ? null : _savePaste,
                  icon: notes.isSaving
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.bookmark_add),
                  label: Text(notes.isSaving ? 'Organizing…' : 'Save to My Book'),
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'Short lines become ★ pearls. Longer text becomes clinical case notes.',
                style: GoogleFonts.inter(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildBookTab() {
    return Consumer<NotesProvider>(
      builder: (context, notes, _) {
        if (notes.isLoadingReview) {
          return const LoadingShimmer();
        }
        final review = notes.review;
        if (review == null || review.total == 0) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.auto_stories_outlined,
                      size: 64, color: Colors.grey[400]),
                  const SizedBox(height: 16),
                  Text(
                    'Your book is empty',
                    style: GoogleFonts.inter(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Paste MCQ explanations on the Paste tab to build chapter-wise notes, pearls, and case reviews.',
                    textAlign: TextAlign.center,
                    style: GoogleFonts.inter(color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 20),
                  OutlinedButton.icon(
                    onPressed: () => _tabController.animateTo(0),
                    icon: const Icon(Icons.content_paste),
                    label: const Text('Paste Notes'),
                  ),
                ],
              ),
            ),
          );
        }

        final groups = [...review.chapters];
        if (review.uncategorized.isNotEmpty) {
          groups.add(NotesChapterGroup(
            key: 'other',
            title: 'Other',
            notes: review.uncategorized,
          ));
        }

        return RefreshIndicator(
          onRefresh: () => notes.loadReview(forceRefresh: true),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Row(
                children: [
                  Text(
                    '${review.total} notes',
                    style: GoogleFonts.inter(fontWeight: FontWeight.w600),
                  ),
                  const Spacer(),
                  TextButton.icon(
                    onPressed: () async {
                      final removed = await notes.dedupeNotes();
                      if (!context.mounted) return;
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(removed > 0
                              ? 'Removed $removed duplicate(s)'
                              : 'No duplicates found'),
                        ),
                      );
                    },
                    icon: const Icon(Icons.filter_none, size: 18),
                    label: const Text('Dedupe'),
                  ),
                ],
              ),
              ...groups.map((g) => _BookChapterSection(
                    group: g,
                    onDelete: (id) => notes.deleteNote(id),
                  )),
            ],
          ),
        );
      },
    );
  }
}

class _BookChapterSection extends StatelessWidget {
  final NotesChapterGroup group;
  final Future<bool> Function(String id) onDelete;

  const _BookChapterSection({
    required this.group,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final pearls = group.pearls;
    final cases = group.clinicalNotes;
    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              group.title,
              style: GoogleFonts.inter(
                fontSize: 17,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              '${pearls.length} pearl${pearls.length == 1 ? '' : 's'} · ${cases.length} case note${cases.length == 1 ? '' : 's'}',
              style: GoogleFonts.inter(fontSize: 12, color: Colors.grey[600]),
            ),
            if (pearls.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text('★ Pearls',
                  style: GoogleFonts.inter(
                      fontWeight: FontWeight.w600, color: Colors.amber[800])),
              ...pearls.map((n) => _NoteTile(note: n, isPearl: true, onDelete: onDelete)),
            ],
            if (cases.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text('¶ Case Reviews',
                  style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
              ...cases.map((n) => _NoteTile(note: n, isPearl: false, onDelete: onDelete)),
            ],
          ],
        ),
      ),
    );
  }
}

class _NoteTile extends StatelessWidget {
  final StudyNote note;
  final bool isPearl;
  final Future<bool> Function(String id) onDelete;

  const _NoteTile({
    required this.note,
    required this.isPearl,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isPearl
            ? Colors.amber.withValues(alpha: 0.08)
            : Theme.of(context).cardTheme.color,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: isPearl
              ? Colors.amber.withValues(alpha: 0.3)
              : Theme.of(context).dividerColor,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (note.topicTitle.isNotEmpty)
                  Text(
                    note.topicTitle,
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey[600],
                    ),
                  ),
                Text(
                  note.content,
                  style: GoogleFonts.inter(fontSize: 13, height: 1.35),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline, size: 20),
            onPressed: () async {
              final ok = await onDelete(note.id);
              if (context.mounted && !ok) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Could not delete note')),
                );
              }
            },
          ),
        ],
      ),
    );
  }
}
