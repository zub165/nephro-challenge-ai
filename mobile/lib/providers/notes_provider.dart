import 'package:flutter/foundation.dart';

import '../models/study_note.dart';
import '../services/notes_service.dart';

class NotesProvider extends ChangeNotifier {
  final NotesService _service = NotesService.instance;

  NotesReview? _review;
  List<PearlChapterGroup> _pearls = [];
  bool _loadingReview = false;
  bool _loadingPearls = false;
  bool _saving = false;
  String? _error;
  String _draftPaste = '';

  NotesReview? get review => _review;
  List<PearlChapterGroup> get pearls => _pearls;
  bool get isLoadingReview => _loadingReview;
  bool get isLoadingPearls => _loadingPearls;
  bool get isSaving => _saving;
  String? get error => _error;
  String get draftPaste => _draftPaste;

  int get totalNotes => _review?.total ?? 0;

  Future<void> loadDraft() async {
    _draftPaste = _service.getDraftPaste() ?? '';
    notifyListeners();
  }

  void setDraftPaste(String value) {
    _draftPaste = value;
    _service.saveDraftPaste(value);
    notifyListeners();
  }

  Future<void> loadReview({bool forceRefresh = false}) async {
    _loadingReview = true;
    _error = null;
    notifyListeners();
    try {
      _review = await _service.fetchReview(forceRefresh: forceRefresh);
    } catch (e) {
      _error = 'Could not load your book';
    } finally {
      _loadingReview = false;
      notifyListeners();
    }
  }

  Future<void> loadPearls() async {
    _loadingPearls = true;
    notifyListeners();
    try {
      _pearls = await _service.fetchPearls();
    } catch (_) {
      _pearls = [];
    } finally {
      _loadingPearls = false;
      notifyListeners();
    }
  }

  Future<OrganizeResult?> savePastedNotes() async {
    final text = _draftPaste.trim();
    if (text.isEmpty) return null;
    _saving = true;
    _error = null;
    notifyListeners();
    try {
      final result = await _service.organizeNotes(text);
      _draftPaste = '';
      await loadReview(forceRefresh: true);
      return result;
    } catch (e) {
      _error = 'Could not save notes. Check login and connection.';
      return null;
    } finally {
      _saving = false;
      notifyListeners();
    }
  }

  Future<bool> deleteNote(String id) async {
    try {
      await _service.deleteNote(id);
      await loadReview(forceRefresh: true);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<int> dedupeNotes() async {
    try {
      final removed = await _service.dedupeNotes();
      await loadReview(forceRefresh: true);
      return removed;
    } catch (_) {
      return 0;
    }
  }
}
