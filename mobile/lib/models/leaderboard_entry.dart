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
    String? displayName,
    String? photoUrl,
    this.points = 0,
    this.streakDays = 0,
    this.accuracy = 0.0,
    this.period = 'all_time',
  })  : displayName = JsonHelpers.firstNonBlankString([displayName]),
        photoUrl = JsonHelpers.firstNonBlankString([photoUrl]);

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json, {int rank = 0}) {
    return LeaderboardEntry(
      rank: rank > 0 ? rank : JsonHelpers.integer(json['rank']),
      userId: JsonHelpers.str(json['user_id'] ?? json['user']),
      displayName: JsonHelpers.firstNonBlankString([
        json['display_name'],
        json['name'],
        json['username'],
      ]),
      photoUrl: JsonHelpers.firstNonBlankString([
        json['photo_url'],
        json['avatar'],
      ]),
      points: JsonHelpers.integer(json['points'] ?? json['score']),
      streakDays: JsonHelpers.integer(
          json['streak'] ?? json['streak_days'] ?? json['streak_count']),
      accuracy: JsonHelpers.decimal(json['accuracy']),
      period: JsonHelpers.str(json['period'], 'all_time'),
    );
  }
}
