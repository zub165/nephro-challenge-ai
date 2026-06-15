import '../models/leaderboard_entry.dart';
import 'api_service.dart';

class LeaderboardService {
  static LeaderboardService? _instance;
  final ApiService _api = ApiService.instance;

  LeaderboardService._();

  static LeaderboardService get instance {
    _instance ??= LeaderboardService._();
    return _instance!;
  }

  Future<List<LeaderboardEntry>> fetchLeaderboard({
    String period = 'all_time',
    int limit = 50,
  }) async {
    try {
      final response = await _api.get('/leaderboard', queryParameters: {
        'period': period,
        'limit': limit,
      });
      final data = response.data as Map<String, dynamic>;
      final entries = (data['entries'] as List<dynamic>)
          .map((e) => LeaderboardEntry.fromJson(e as Map<String, dynamic>))
          .toList();
      return entries;
    } catch (_) {
      return [];
    }
  }

  Future<LeaderboardEntry?> fetchCurrentUserRank({String period = 'all_time'}) async {
    try {
      final response =
          await _api.get('/leaderboard/me', queryParameters: {'period': period});
      return LeaderboardEntry.fromJson(
          response.data['entry'] as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }
}
