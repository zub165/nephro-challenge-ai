import 'dart:convert';

import '../models/study_note.dart';
import 'api_service.dart';
import 'storage_service.dart';

class NotesService {
  static NotesService? _instance;
  final ApiService _api = ApiService.instance;
  final StorageService _storage = StorageService.instance;

  static const _reviewCacheKey = 'notes_review_cache';
  static const _draftKey = 'notes_draft_paste';

  NotesService._();

  static NotesService get instance {
    _instance ??= NotesService._();
    return _instance!;
  }

  String? getDraftPaste() => _storage.getString(_draftKey);

  Future<void> saveDraftPaste(String text) async {
    await _storage.setString(_draftKey, text);
  }

  Future<void> clearDraftPaste() async {
    await _storage.setString(_draftKey, '');
  }

  NotesReview? _cachedReview() {
    final raw = _storage.getString(_reviewCacheKey);
    if (raw == null || raw.isEmpty) return null;
    try {
      return NotesReview.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<void> _cacheReview(NotesReview review) async {
    await _storage.setString(_reviewCacheKey, jsonEncode({
      'chapters': review.chapters
          .map((c) => {
                'chapter': {
                  'slug': c.key,
                  'title': c.title,
                  'order_index': c.order,
                },
                'notes': c.notes.map((n) => n.toJson()).toList(),
              })
          .toList(),
      'uncategorized':
          review.uncategorized.map((n) => n.toJson()).toList(),
      'total': review.total,
    }));
  }

  Future<NotesReview> fetchReview({bool forceRefresh = false}) async {
    if (!forceRefresh) {
      final cached = _cachedReview();
      if (cached != null && cached.total > 0) return cached;
    }
    try {
      final response = await _api.get('/notes/review/');
      final review =
          NotesReview.fromJson(response.data as Map<String, dynamic>);
      await _cacheReview(review);
      return review;
    } catch (_) {
      return _cachedReview() ?? const NotesReview();
    }
  }

  Future<OrganizeResult> organizeNotes(String text) async {
    final response = await _api.post('/notes/organize/', data: {'text': text});
    final data = response.data as Map<String, dynamic>;
    final notes = (data['notes'] as List<dynamic>? ?? [])
        .map((n) => StudyNote.fromJson(n as Map<String, dynamic>))
        .toList();
    await clearDraftPaste();
    await fetchReview(forceRefresh: true);
    return OrganizeResult(
      notes: notes,
      total: data['total'] as int? ?? notes.length,
      skippedDuplicates: data['skipped_duplicates'] as int? ?? 0,
      method: data['method'] as String? ?? 'keywords',
    );
  }

  Future<void> deleteNote(String id) async {
    await _api.delete('/notes/$id/');
    await fetchReview(forceRefresh: true);
  }

  Future<int> dedupeNotes() async {
    final response = await _api.post('/notes/dedupe/');
    final removed = (response.data as Map<String, dynamic>)['removed'] as int? ?? 0;
    await fetchReview(forceRefresh: true);
    return removed;
  }

  Future<List<PearlChapterGroup>> fetchPearls({String? chapterSlug}) async {
    try {
      final response = await _api.get('/pearls/', queryParameters: {
        if (chapterSlug != null) 'chapter': chapterSlug,
      });
      final data = response.data as Map<String, dynamic>;
      final chapters = data['chapters'] as List<dynamic>? ?? [];
      return chapters.map((c) {
        final m = c as Map<String, dynamic>;
        final ch = m['chapter'] as Map<String, dynamic>? ?? {};
        final pearls = (m['pearls'] as List<dynamic>? ?? [])
            .map((p) => PearlItem.fromJson(p as Map<String, dynamic>))
            .toList();
        return PearlChapterGroup(
          title: ch['title'] as String? ?? 'General',
          slug: ch['slug'] as String? ?? '',
          pearls: pearls,
        );
      }).toList();
    } catch (_) {
      return [];
    }
  }
}

class OrganizeResult {
  final List<StudyNote> notes;
  final int total;
  final int skippedDuplicates;
  final String method;

  const OrganizeResult({
    required this.notes,
    required this.total,
    this.skippedDuplicates = 0,
    this.method = 'keywords',
  });
}
