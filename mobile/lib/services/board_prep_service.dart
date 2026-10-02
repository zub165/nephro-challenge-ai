import 'dart:convert';
import '../utils/json_helpers.dart';
import 'api_service.dart';
import 'storage_service.dart';

class BoardPrepService {
  static BoardPrepService? _instance;
  final ApiService _api = ApiService.instance;
  final StorageService _storage = StorageService.instance;
  static const _cacheKey = 'board_prep_plan_cache';

  BoardPrepService._();

  static BoardPrepService get instance {
    _instance ??= BoardPrepService._();
    return _instance!;
  }

  Future<Map<String, dynamic>> fetchPlan() async {
    try {
      final response = await _api.get('/board-prep/plan/');
      final data = Map<String, dynamic>.from(response.data as Map);
      await _storage.setString(_cacheKey, jsonEncode(data));
      return data;
    } catch (_) {
      final cached = _storage.getString(_cacheKey);
      if (cached != null && cached.isNotEmpty) {
        return jsonDecode(cached) as Map<String, dynamic>;
      }
      return {};
    }
  }

  Future<Map<String, dynamic>> savePlan({
    String? examDate,
    List<int>? workWeekdays,
  }) async {
    final response = await _api.post('/board-prep/plan/', data: {
      if (examDate != null) 'exam_date': examDate,
      if (workWeekdays != null) 'work_weekdays': workWeekdays,
    });
    final data = Map<String, dynamic>.from(response.data as Map);
    await _storage.setString(_cacheKey, jsonEncode(data));
    return data;
  }

  Future<Map<String, dynamic>> fetchReview({String tag = 'review'}) async {
    try {
      final response = await _api.get(
        '/board-prep/review-queue/',
        queryParameters: {'tag': tag},
      );
      return Map<String, dynamic>.from(response.data as Map);
    } catch (_) {
      return {'items': [], 'count': 0, 'tag': tag};
    }
  }

  Future<Map<String, dynamic>> fetchLast48() async {
    try {
      final response = await _api.get('/board-prep/last-48h/');
      return Map<String, dynamic>.from(response.data as Map);
    } catch (_) {
      return {'items': []};
    }
  }

  Future<void> addFact({required String kind, required String text}) async {
    await _api.post('/board-prep/last-48h/', data: {'kind': kind, 'text': text});
  }

  Future<void> deleteFact(String id) async {
    await _api.delete('/board-prep/last-48h/$id/');
  }

  int asInt(dynamic value) => JsonHelpers.integer(value);
}
