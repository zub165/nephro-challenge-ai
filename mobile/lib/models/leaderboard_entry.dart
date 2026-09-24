import '../utils/json_helpers.dart';

class LeaderboardEntry {
  final int rank;
  final String userId;
  final String? displayName;
  final String? photoUrl;
  final int points;
  final int streakDays;
  final double accuracy;
  final String period;

  int get quizzesCompleted => 0;

  LeaderboardEntry({
    required this.rank,
    required this.userId,
    this.displayName,
    this.photoUrl,
    this.points = 0,
    this.streakDays = 0,
    this.accuracy = 0.0,
    this.period = 'all_time',
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json, {int rank = 0}) {
    return LeaderboardEntry(
      rank: rank > 0 ? rank : JsonHelpers.integer(json['rank']),
      userId: JsonHelpers.str(json['user_id'] ?? json['user']),
      displayName: json['display_name'] as String? ??
          json['username'] as String? ??
          json['name'] as String?,
      photoUrl: json['photo_url'] as String? ?? json['avatar'] as String?,
      points: JsonHelpers.integer(json['points'] ?? json['score']),
      streakDays: JsonHelpers.integer(
          json['streak'] ?? json['streak_days'] ?? json['streak_count']),
      accuracy: JsonHelpers.decimal(json['accuracy']),
      period: JsonHelpers.str(json['period'], 'all_time'),
    );
  }
}
