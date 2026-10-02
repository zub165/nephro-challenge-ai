import '../utils/json_helpers.dart';

/// Per-question result returned by the server after a quiz is marked. This is
/// the single source of truth; the quiz payload never contains the answer.
class QuizAnswerFeedback {
  final String questionId;
  final String? chosenChoiceId;
  final String? correctChoiceId;
  final bool isCorrect;
  final String whyWrong;
  final String explanation;
  final String clinicalPearl;
  final String reference;

  QuizAnswerFeedback({
    required this.questionId,
    this.chosenChoiceId,
    this.correctChoiceId,
    this.isCorrect = false,
    this.whyWrong = '',
    this.explanation = '',
    this.clinicalPearl = '',
    this.reference = '',
  });

  factory QuizAnswerFeedback.fromJson(Map<String, dynamic> json) {
    final refs = json['references'] as List<dynamic>? ?? const [];
    final reference = refs
        .whereType<Map>()
        .map((r) => JsonHelpers.str(r['citation'] ?? r['title']))
        .where((s) => s.isNotEmpty)
        .join(' | ');
    return QuizAnswerFeedback(
      questionId: JsonHelpers.str(json['question_id'] ?? json['question']),
      chosenChoiceId: json['chosen_choice_id']?.toString(),
      correctChoiceId: json['correct_choice_id']?.toString(),
      isCorrect: json['is_correct'] as bool? ?? false,
      whyWrong: JsonHelpers.str(json['why_wrong']),
      explanation: JsonHelpers.str(json['explanation']),
      clinicalPearl: JsonHelpers.str(json['clinical_pearl']),
      reference: reference,
    );
  }
}

class QuizAttempt {
  final String id;
  final String mode;
  final String? categoryName;
  final int score;
  final int totalQuestions;
  final double percentage;
  final int timeTaken;
  final DateTime? completedAt;
  final List<QuizAnswerFeedback> answers;

  QuizAttempt({
    required this.id,
    this.mode = 'practice',
    this.categoryName,
    this.score = 0,
    this.totalQuestions = 0,
    this.percentage = 0.0,
    this.timeTaken = 0,
    this.completedAt,
    this.answers = const [],
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
      answers: JsonHelpers.listOfMaps(json['answers'])
          .map(QuizAnswerFeedback.fromJson)
          .toList(),
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
