class QuestionResult {
  final String questionId;
  final String? selectedChoiceId;
  final String? correctChoiceId;
  final bool isCorrect;
  final int timeTakenSeconds;
  final int pointsEarned;

  QuestionResult({
    required this.questionId,
    this.selectedChoiceId,
    this.correctChoiceId,
    required this.isCorrect,
    this.timeTakenSeconds = 0,
    this.pointsEarned = 0,
  });

  factory QuestionResult.fromJson(Map<String, dynamic> json) {
    return QuestionResult(
      questionId: json['question_id'] as String,
      selectedChoiceId: json['selected_choice_id'] as String?,
      correctChoiceId: json['correct_choice_id'] as String?,
      isCorrect: json['is_correct'] as bool,
      timeTakenSeconds: json['time_taken_seconds'] as int? ?? 0,
      pointsEarned: json['points_earned'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'question_id': questionId,
      'selected_choice_id': selectedChoiceId,
      'correct_choice_id': correctChoiceId,
      'is_correct': isCorrect,
      'time_taken_seconds': timeTakenSeconds,
      'points_earned': pointsEarned,
    };
  }
}

class QuizAttempt {
  final String id;
  final String userId;
  final String? categoryId;
  final List<QuestionResult> results;
  final int totalQuestions;
  final int correctCount;
  final int incorrectCount;
  final int totalPoints;
  final double accuracy;
  final int durationSeconds;
  final bool isDailyChallenge;
  final DateTime startedAt;
  final DateTime? completedAt;

  QuizAttempt({
    required this.id,
    required this.userId,
    this.categoryId,
    required this.results,
    this.totalQuestions = 0,
    this.correctCount = 0,
    this.incorrectCount = 0,
    this.totalPoints = 0,
    this.accuracy = 0.0,
    this.durationSeconds = 0,
    this.isDailyChallenge = false,
    DateTime? startedAt,
    this.completedAt,
  }) : startedAt = startedAt ?? DateTime.now();

  factory QuizAttempt.fromJson(Map<String, dynamic> json) {
    return QuizAttempt(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      categoryId: json['category_id'] as String?,
      results: (json['results'] as List<dynamic>)
          .map((r) => QuestionResult.fromJson(r as Map<String, dynamic>))
          .toList(),
      totalQuestions: json['total_questions'] as int? ?? 0,
      correctCount: json['correct_count'] as int? ?? 0,
      incorrectCount: json['incorrect_count'] as int? ?? 0,
      totalPoints: json['total_points'] as int? ?? 0,
      accuracy: (json['accuracy'] as num?)?.toDouble() ?? 0.0,
      durationSeconds: json['duration_seconds'] as int? ?? 0,
      isDailyChallenge: json['is_daily_challenge'] as bool? ?? false,
      startedAt: json['started_at'] != null
          ? DateTime.parse(json['started_at'] as String)
          : DateTime.now(),
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'category_id': categoryId,
      'results': results.map((r) => r.toJson()).toList(),
      'total_questions': totalQuestions,
      'correct_count': correctCount,
      'incorrect_count': incorrectCount,
      'total_points': totalPoints,
      'accuracy': accuracy,
      'duration_seconds': durationSeconds,
      'is_daily_challenge': isDailyChallenge,
      'started_at': startedAt.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
    };
  }
}
