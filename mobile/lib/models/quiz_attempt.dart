import '../utils/json_helpers.dart';

class QuizAttempt {
  final String id;
  final String mode;
  final String? categoryName;
  final int score;
  final int totalQuestions;
  final double percentage;
  final int timeTaken;
  final DateTime? completedAt;

  QuizAttempt({
    required this.id,
    this.mode = 'practice',
    this.categoryName,
    this.score = 0,
    this.totalQuestions = 0,
    this.percentage = 0.0,
    this.timeTaken = 0,
    this.completedAt,
  });

  factory QuizAttempt.fromJson(Map<String, dynamic> json) {
    return QuizAttempt(
      id: JsonHelpers.str(json['id']),
      mode: JsonHelpers.str(json['mode'], 'practice'),
      categoryName: json['category_name'] as String?,
      score: JsonHelpers.integer(json['score']),
      totalQuestions: JsonHelpers.integer(json['total_questions']),
      percentage: JsonHelpers.decimal(json['percentage']),
      timeTaken: JsonHelpers.integer(json['time_taken']),
      completedAt: json['completed_at'] != null
          ? DateTime.tryParse(json['completed_at'].toString())
          : null,
    );
  }

  String get modeLabel {
    switch (mode) {
      case 'daily':
        return 'Daily Challenge';
      case 'chapter':
        return 'Chapter Quiz';
      case 'category':
        return 'Category Quiz';
      default:
        return 'Practice';
    }
  }
}

class CategoryPerformance {
  final String categoryId;
  final String categoryName;
  final int totalQuestions;
  final int correctAnswers;
  final double accuracy;

  const CategoryPerformance({
    required this.categoryId,
    required this.categoryName,
    required this.totalQuestions,
    required this.correctAnswers,
    required this.accuracy,
  });

  factory CategoryPerformance.fromJson(Map<String, dynamic> json) {
    return CategoryPerformance(
      categoryId: JsonHelpers.str(json['categoryId']),
      categoryName: JsonHelpers.str(json['categoryName']),
      totalQuestions: JsonHelpers.integer(json['totalQuestions']),
      correctAnswers: JsonHelpers.integer(json['correctAnswers']),
      accuracy: JsonHelpers.decimal(json['accuracy']),
    );
  }
}
