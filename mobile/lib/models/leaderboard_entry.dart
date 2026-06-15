class LeaderboardEntry {
  final int rank;
  final String userId;
  final String? displayName;
  final String? photoUrl;
  final int points;
  final int streakDays;
  final double accuracy;
  final int quizzesCompleted;
  final String period;

  LeaderboardEntry({
    required this.rank,
    required this.userId,
    this.displayName,
    this.photoUrl,
    this.points = 0,
    this.streakDays = 0,
    this.accuracy = 0.0,
    this.quizzesCompleted = 0,
    this.period = 'all_time',
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) {
    return LeaderboardEntry(
      rank: json['rank'] as int,
      userId: json['user_id'] as String,
      displayName: json['display_name'] as String?,
      photoUrl: json['photo_url'] as String?,
      points: json['points'] as int? ?? 0,
      streakDays: json['streak_days'] as int? ?? 0,
      accuracy: (json['accuracy'] as num?)?.toDouble() ?? 0.0,
      quizzesCompleted: json['quizzes_completed'] as int? ?? 0,
      period: json['period'] as String? ?? 'all_time',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'rank': rank,
      'user_id': userId,
      'display_name': displayName,
      'photo_url': photoUrl,
      'points': points,
      'streak_days': streakDays,
      'accuracy': accuracy,
      'quizzes_completed': quizzesCompleted,
      'period': period,
    };
  }
}
