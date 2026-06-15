class AIExplanation {
  final String id;
  final String questionId;
  final String explanation;
  final List<String> keyPoints;
  final List<String> references;
  final String? relatedTopic;
  final String difficulty;
  final DateTime createdAt;

  AIExplanation({
    required this.id,
    required this.questionId,
    required this.explanation,
    this.keyPoints = const [],
    this.references = const [],
    this.relatedTopic,
    this.difficulty = 'intermediate',
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory AIExplanation.fromJson(Map<String, dynamic> json) {
    return AIExplanation(
      id: json['id'] as String,
      questionId: json['question_id'] as String,
      explanation: json['explanation'] as String,
      keyPoints: (json['key_points'] as List<dynamic>?)
              ?.map((k) => k as String)
              .toList() ??
          [],
      references: (json['references'] as List<dynamic>?)
              ?.map((r) => r as String)
              .toList() ??
          [],
      relatedTopic: json['related_topic'] as String?,
      difficulty: json['difficulty'] as String? ?? 'intermediate',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'question_id': questionId,
      'explanation': explanation,
      'key_points': keyPoints,
      'references': references,
      'related_topic': relatedTopic,
      'difficulty': difficulty,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
