import '../utils/json_helpers.dart';
import 'api_service.dart';

class AdminService {
  static AdminService? _instance;
  final ApiService _api = ApiService.instance;

  AdminService._();

  static AdminService get instance {
    _instance ??= AdminService._();
    return _instance!;
  }

  Future<Map<String, dynamic>> fetchStats() async {
    final response = await _api.get('/admin/stats/');
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<Map<String, dynamic>> fetchQuestions({
    int page = 1,
    String search = '',
  }) async {
    final response = await _api.get('/admin/questions/', queryParameters: {
      'page': page,
      'limit': 20,
      if (search.trim().isNotEmpty) 'search': search.trim(),
    });
    return Map<String, dynamic>.from(response.data as Map);
  }

  Future<void> saveQuestion(Map<String, dynamic> payload, {String? id}) async {
    if (id == null || id.isEmpty) {
      await _api.post('/admin/questions/', data: payload);
    } else {
      await _api.put('/admin/questions/$id/', data: payload);
    }
  }

  Future<void> deleteQuestion(String id) async {
    await _api.delete('/admin/questions/$id/');
  }

  Future<List<Map<String, dynamic>>> fetchAi({String status = 'pending'}) async {
    final response = await _api.get(
      '/admin/questions/ai-generated/',
      queryParameters: {'status': status},
    );
    return JsonHelpers.listOfMaps(response.data);
  }

  Future<void> reviewAi(String id, String status) async {
    await _api.put(
      '/admin/questions/$id/review/',
      data: {'aiReviewStatus': status},
    );
  }
}
