import '../utils/json_helpers.dart';

class Category {
  final String id;
  final String name;
  final String? description;
  final String? icon;
  final int questionCount;
  final int completedCount;
  final double accuracy;
  final bool isLocked;

  Category({
    required this.id,
    required this.name,
    this.description,
    this.icon,
    this.questionCount = 0,
    this.completedCount = 0,
    this.accuracy = 0.0,
    this.isLocked = false,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: JsonHelpers.str(json['id']),
      name: JsonHelpers.str(json['name']),
      description: json['description'] as String?,
      icon: json['icon'] as String? ?? json['icon_url'] as String?,
      questionCount: JsonHelpers.integer(json['question_count'] ?? json['questionCount']),
      completedCount: JsonHelpers.integer(json['completed_count']),
      accuracy: JsonHelpers.decimal(json['accuracy']),
      isLocked: json['is_locked'] as bool? ?? false,
    );
  }

  double get completionPercentage =>
      questionCount > 0 ? completedCount / questionCount : 0.0;
}
