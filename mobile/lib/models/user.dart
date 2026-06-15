class User {
  final String id;
  final String email;
  final String? displayName;
  final String? photoUrl;
  final String role;
  final int streakDays;
  final int totalQuizzes;
  final int totalQuestions;
  final int correctAnswers;
  final double accuracy;
  final int points;
  final int rank;
  final DateTime createdAt;
  final DateTime? lastActiveAt;

  User({
    required this.id,
    required this.email,
    this.displayName,
    this.photoUrl,
    this.role = 'student',
    this.streakDays = 0,
    this.totalQuizzes = 0,
    this.totalQuestions = 0,
    this.correctAnswers = 0,
    this.accuracy = 0.0,
    this.points = 0,
    this.rank = 0,
    DateTime? createdAt,
    this.lastActiveAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      email: json['email'] as String,
      displayName: json['display_name'] as String?,
      photoUrl: json['photo_url'] as String?,
      role: json['role'] as String? ?? 'student',
      streakDays: json['streak_days'] as int? ?? 0,
      totalQuizzes: json['total_quizzes'] as int? ?? 0,
      totalQuestions: json['total_questions'] as int? ?? 0,
      correctAnswers: json['correct_answers'] as int? ?? 0,
      accuracy: (json['accuracy'] as num?)?.toDouble() ?? 0.0,
      points: json['points'] as int? ?? 0,
      rank: json['rank'] as int? ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      lastActiveAt: json['last_active_at'] != null
          ? DateTime.parse(json['last_active_at'] as String)
          : null,
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
      'total_quizzes': totalQuizzes,
      'total_questions': totalQuestions,
      'correct_answers': correctAnswers,
      'accuracy': accuracy,
      'points': points,
      'rank': rank,
      'created_at': createdAt.toIso8601String(),
      'last_active_at': lastActiveAt?.toIso8601String(),
    };
  }

  User copyWith({
    String? id,
    String? email,
    String? displayName,
    String? photoUrl,
    String? role,
    int? streakDays,
    int? totalQuizzes,
    int? totalQuestions,
    int? correctAnswers,
    double? accuracy,
    int? points,
    int? rank,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      displayName: displayName ?? this.displayName,
      photoUrl: photoUrl ?? this.photoUrl,
      role: role ?? this.role,
      streakDays: streakDays ?? this.streakDays,
      totalQuizzes: totalQuizzes ?? this.totalQuizzes,
      totalQuestions: totalQuestions ?? this.totalQuestions,
      correctAnswers: correctAnswers ?? this.correctAnswers,
      accuracy: accuracy ?? this.accuracy,
      points: points ?? this.points,
      rank: rank ?? this.rank,
      createdAt: createdAt,
      lastActiveAt: lastActiveAt,
    );
  }
}
