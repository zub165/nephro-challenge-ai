import '../utils/json_helpers.dart';

class User {
  final String id;
  final String email;
  final String? displayName;
  final String? photoUrl;
  final String role;
  final int streakDays;
  final int xpPoints;
  final DateTime createdAt;

  User({
    required this.id,
    required this.email,
    this.displayName,
    this.photoUrl,
    this.role = 'free',
    this.streakDays = 0,
    this.xpPoints = 0,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  int get rank => 0;

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: JsonHelpers.str(json['id']),
      email: JsonHelpers.str(json['email']),
      displayName: json['display_name'] as String? ??
          json['username'] as String? ??
          json['name'] as String?,
      photoUrl: json['photo_url'] as String? ?? json['avatar'] as String?,
      role: JsonHelpers.str(json['role'], 'free'),
      streakDays: JsonHelpers.integer(json['streak_days'] ?? json['streak_count']),
      xpPoints: JsonHelpers.integer(json['xp_points'] ?? json['points']),
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'].toString()) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'display_name': displayName,
      'photo_url': photoUrl,
      'role': role,
      'streak_days': streakDays,
      'xp_points': xpPoints,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
