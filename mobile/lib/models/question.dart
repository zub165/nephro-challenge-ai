class Choice {
  final String id;
  final String text;
  final bool isCorrect;

  Choice({
    required this.id,
    required this.text,
    required this.isCorrect,
  });

  factory Choice.fromJson(Map<String, dynamic> json) {
    return Choice(
      id: json['id'] as String,
      text: json['text'] as String,
      isCorrect: json['is_correct'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'is_correct': isCorrect,
    };
  }
}

class Question {
  final String id;
  final String text;
  final List<Choice> choices;
  final String? categoryId;
  final String? categoryName;
  final String difficulty;
  final String? explanation;
  final String? imageUrl;
  final List<String>? tags;
  final int timeLimitSeconds;
  final int points;

  Question({
    required this.id,
    required this.text,
    required this.choices,
    this.categoryId,
    this.categoryName,
    this.difficulty = 'medium',
    this.explanation,
    this.imageUrl,
    this.tags,
    this.timeLimitSeconds = 30,
    this.points = 10,
  });

  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      id: json['id'] as String,
      text: json['text'] as String,
      choices: (json['choices'] as List<dynamic>)
          .map((c) => Choice.fromJson(c as Map<String, dynamic>))
          .toList(),
      categoryId: json['category_id'] as String?,
      categoryName: json['category_name'] as String?,
      difficulty: json['difficulty'] as String? ?? 'medium',
      explanation: json['explanation'] as String?,
      imageUrl: json['image_url'] as String?,
      tags: (json['tags'] as List<dynamic>?)
          ?.map((t) => t as String)
          .toList(),
      timeLimitSeconds: json['time_limit_seconds'] as int? ?? 30,
      points: json['points'] as int? ?? 10,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'text': text,
      'choices': choices.map((c) => c.toJson()).toList(),
      'category_id': categoryId,
      'category_name': categoryName,
      'difficulty': difficulty,
      'explanation': explanation,
      'image_url': imageUrl,
      'tags': tags,
      'time_limit_seconds': timeLimitSeconds,
      'points': points,
    };
  }
}
