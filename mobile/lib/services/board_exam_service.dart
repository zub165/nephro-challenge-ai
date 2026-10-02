import 'dart:convert';

import '../utils/json_helpers.dart';
import 'api_service.dart';
import 'storage_service.dart';

class BoardExamService {
  static BoardExamService? _instance;
  final ApiService _api = ApiService.instance;
  final StorageService _storage = StorageService.instance;
  static const _cacheKey = 'board_exams_list_cache';

  BoardExamService._();

  static BoardExamService get instance {
    _instance ??= BoardExamService._();
    return _instance!;
  }

  Future<List<Map<String, dynamic>>> fetchExams() async {
    try {
      final response = await _api.get('/board-exams/');
      final list = response.data is List
          ? response.data as List
          : (response.data as Map)['results'] as List? ?? [];
      final exams = list
          .whereType<Map>()
          .map((e) => Map<String, dynamic>.from(e))
          .toList();
      await _storage.setString(_cacheKey, jsonEncode(exams));
      return exams;
    } catch (_) {
      final cached = _storage.getString(_cacheKey);
      if (cached != null && cached.isNotEmpty) {
        final decoded = jsonDecode(cached);
        if (decoded is List) {
          return decoded
              .whereType<Map>()
              .map((e) => Map<String, dynamic>.from(e))
              .toList();
        }
      }
      return [];
    }
  }

  Future<Map<String, dynamic>> startOrResume(String slug) async {
    final response = await _api.post('/board-exams/$slug/start/');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> fetchAttempt(String attemptId) async {
    final response = await _api.get('/board-exams/attempts/$attemptId/');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<void> saveAnswer({
    required String attemptId,
    required int position,
    required String choiceKey,
  }) async {
    await _api.put(
      '/board-exams/attempts/$attemptId/items/$position/',
      data: {'selected_choice_key': choiceKey},
    );
  }

  Future<Map<String, dynamic>> submit(String attemptId) async {
    final response = await _api.post('/board-exams/attempts/$attemptId/submit/');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> fetchResults(String attemptId) async {
    final response = await _api.get('/board-exams/attempts/$attemptId/results/');
    return Map<String, dynamic>.from(response.data as Map);
  }

  int asInt(dynamic value) => JsonHelpers.integer(value);

  String attemptIdOf(Map<String, dynamic> payload) {
    return JsonHelpers.str(payload['attempt_id'] ?? payload['id']);
  }
}
