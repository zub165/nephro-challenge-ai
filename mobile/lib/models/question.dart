import '../utils/json_helpers.dart';

class Choice {
  final String id;
  final String text;
  final String? key;
  final bool isCorrect;

  Choice({
    required this.id,
    required this.text,
    this.key,
    this.isCorrect = false,
  });

  factory Choice.fromJson(Map<String, dynamic> json) {
    return Choice(
      id: JsonHelpers.str(json['id']),
      text: JsonHelpers.str(json['text'] ?? json['choice_text']),
      key: json['key'] as String? ?? json['choice_key'] as String?,
      isCorrect: json['is_correct'] as bool? ?? false,
    );
  }
}

class Question {
  final String id;
  final String text;
  final String? caseText;
  final Map<String, dynamic> labs;
  final List<Choice> choices;
  final String? correctChoiceId;
  final String? categoryId;
  final String? chapterId;
  final String? categoryName;
  final String difficulty;
  final String? explanation;
  final String? clinicalPearl;
  final String? imageUrl;
  final List<String> tags;
  final int points;
  final int timeLimitSeconds;

  Question({
    required this.id,
    required this.text,
    this.caseText,
    this.labs = const {},
    required this.choices,
    this.correctChoiceId,
    this.categoryId,
    this.chapterId,
    this.categoryName,
    this.difficulty = 'medium',
    this.explanation,
    this.clinicalPearl,
    this.imageUrl,
    this.tags = const [],
    this.points = 10,
    this.timeLimitSeconds = 30,
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    final choicesRaw = json['choices'] as List<dynamic>? ?? [];
    final choices = choicesRaw
        .map((c) => Choice.fromJson(c as Map<String, dynamic>))
        .toList();

    String? correctId = json['correctAnswer'] as String? ??
        json['correct_choice_id'] as String? ??
        json['correctChoiceId'] as String?;
    if ((correctId == null || correctId.isEmpty) &&
        (json['correctChoiceKey'] != null || json['correct_choice_key'] != null)) {
      final key = (json['correctChoiceKey'] ?? json['correct_choice_key']) as String;
      for (final c in choices) {
        if (c.key == key) {
          correctId = c.id;
          break;
        }
      }
    }
    if (correctId == null) {
      for (final c in choices) {
        if (c.isCorrect) {
          correctId = c.id;
          break;
        }
      }
    }

    return Question(
      id: JsonHelpers.str(json['id']),
      text: JsonHelpers.str(json['text'] ?? json['question_text']),
      caseText: json['caseText'] as String? ?? json['case_text'] as String?,
      labs: Map<String, dynamic>.from(json['labs'] as Map? ?? {}),
      choices: choices,
      correctChoiceId: correctId,
      categoryId: JsonHelpers.str(json['categoryId'] ?? json['category']),
      chapterId: json['chapterId']?.toString() ?? json['chapter']?.toString(),
      categoryName: json['category_name'] as String? ?? json['categoryName'] as String?,
      difficulty: JsonHelpers.str(json['difficulty'], 'medium'),
      explanation: json['explanation'] as String?,
      clinicalPearl: json['clinicalPearl'] as String? ?? json['clinical_pearl'] as String?,
      imageUrl: json['image_url'] as String? ?? json['imageUrl'] as String?,
      tags: (json['tags'] as List<dynamic>?)?.map((t) => t.toString()).toList() ?? const [],
      points: JsonHelpers.integer(json['points'], 10),
      timeLimitSeconds: JsonHelpers.integer(json['time_limit_seconds'] ?? json['timeLimitSeconds'], 30),
    );
  }

  /// Correct choice id from API field or choice flags (quiz list hides is_correct).
  String? get resolvedCorrectChoiceId {
    if (correctChoiceId != null && correctChoiceId!.isNotEmpty) {
      return correctChoiceId;
    }
    for (final c in choices) {
      if (c.isCorrect) return c.id;
    }
    return null;
  }
}
