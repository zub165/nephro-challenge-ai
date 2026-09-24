import '../models/leaderboard_entry.dart';
import '../utils/json_helpers.dart';
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
  }) async {
    try {
      final response = await _api.get('/leaderboard/', queryParameters: {
        'period': period,
      });
      final list = response.data is List
          ? response.data as List
          : (response.data as Map)['results'] as List? ?? [];
      var rank = 1;
      return list.map((e) {
        final entry = LeaderboardEntry.fromJson(
            e as Map<String, dynamic>, rank: rank);
        rank++;
        return entry;
      }).toList();
    } catch (_) {
      return [];
    }
  }

  Future<LeaderboardEntry?> fetchCurrentUserRank(
      {String period = 'all_time'}) async {
    try {
      final response = await _api.get('/leaderboard/user_rank/',
          queryParameters: {'period': period});
      final data = response.data as Map<String, dynamic>;
      if (data['rank'] == null) return null;
      return LeaderboardEntry(
        rank: JsonHelpers.integer(data['rank']),
        userId: JsonHelpers.str(data['user_id']),
        displayName: 'You',
        points: JsonHelpers.integer(data['score']),
        streakDays: JsonHelpers.integer(data['streak']),
        period: period,
      );
    } catch (_) {
      return null;
    }
  }
}
