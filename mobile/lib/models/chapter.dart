import '../utils/json_helpers.dart';

class Chapter {
  final String id;
  final String title;
  final String slug;
  final String description;
  final int orderIndex;
  final int topicCount;
  final int questionCount;
  final int lessonCount;
  final List<Topic>? topics;

  Chapter({
    required this.id,
    required this.title,
    required this.slug,
    required this.description,
    this.orderIndex = 0,
    this.topicCount = 0,
    this.questionCount = 0,
    this.lessonCount = 0,
    this.topics,
  });

  factory Chapter.fromJson(Map<String, dynamic> json) {
    return Chapter(
      id: JsonHelpers.str(json['id']),
      title: JsonHelpers.str(json['title']),
      slug: JsonHelpers.str(json['slug']),
      description: JsonHelpers.str(json['description']),
      orderIndex: JsonHelpers.integer(json['order_index']),
      topicCount: JsonHelpers.integer(json['topic_count']),
      questionCount: JsonHelpers.integer(json['question_count']),
      lessonCount: JsonHelpers.integer(json['lesson_count']),
      topics: json['topics'] != null
          ? (json['topics'] as List)
              .map((t) => Topic.fromJson(t as Map<String, dynamic>))
              .toList()
          : null,
    );
  }
}

class Topic {
  final String id;
  final String title;
  final String slug;
  final String description;
  final List<Lesson>? lessons;

  Topic({
    required this.id,
    required this.title,
    required this.slug,
    this.description = '',
    this.lessons,
  });

  factory Topic.fromJson(Map<String, dynamic> json) {
    return Topic(
      id: JsonHelpers.str(json['id']),
      title: JsonHelpers.str(json['title']),
      slug: JsonHelpers.str(json['slug']),
      description: JsonHelpers.str(json['description']),
      lessons: json['lessons'] != null
          ? (json['lessons'] as List)
              .map((l) => Lesson.fromJson(l as Map<String, dynamic>))
              .toList()
          : null,
    );
  }
}

class Lesson {
  final String id;
  final String title;
  final String lessonType;
  final String summary;
  final String animationUrl;
  final String thumbnailUrl;
  final int durationSeconds;

  Lesson({
    required this.id,
    required this.title,
    this.lessonType = 'animation',
    this.summary = '',
    this.animationUrl = '',
    this.thumbnailUrl = '',
    this.durationSeconds = 0,
  });

  factory Lesson.fromJson(Map<String, dynamic> json) {
    return Lesson(
      id: JsonHelpers.str(json['id']),
      title: JsonHelpers.str(json['title']),
      lessonType: JsonHelpers.str(json['lesson_type'], 'animation'),
      summary: JsonHelpers.str(json['summary']),
      animationUrl: JsonHelpers.str(json['animation_url']),
      thumbnailUrl: JsonHelpers.str(json['thumbnail_url']),
      durationSeconds: JsonHelpers.integer(json['duration_seconds']),
    );
  }
}
