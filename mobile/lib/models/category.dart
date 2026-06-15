class Category {
  final String id;
  final String name;
  final String? description;
  final String? iconUrl;
  final int questionCount;
  final int completedCount;
  final double accuracy;
  final bool isLocked;

  Category({
    required this.id,
    required this.name,
    this.description,
    this.iconUrl,
    this.questionCount = 0,
    this.completedCount = 0,
    this.accuracy = 0.0,
    this.isLocked = false,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      iconUrl: json['icon_url'] as String?,
      questionCount: json['question_count'] as int? ?? 0,
      completedCount: json['completed_count'] as int? ?? 0,
      accuracy: (json['accuracy'] as num?)?.toDouble() ?? 0.0,
      isLocked: json['is_locked'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'icon_url': iconUrl,
      'question_count': questionCount,
      'completed_count': completedCount,
      'accuracy': accuracy,
      'is_locked': isLocked,
    };
  }

  double get completionPercentage =>
      questionCount > 0 ? (completedCount / questionCount) : 0.0;
}
