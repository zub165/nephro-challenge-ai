import '../utils/json_helpers.dart';

class AnimationStep {
  final String title;
  final String body;
  final String tip;
  final String visual;
  final Map<String, String> metrics;

  AnimationStep({
    this.title = '',
    this.body = '',
    this.tip = '',
    this.visual = '',
    Map<String, String>? metrics,
  }) : metrics = metrics ?? const {};

  factory AnimationStep.fromJson(Map<String, dynamic> json) {
    final rawMetrics = json['metrics'];
    final metrics = <String, String>{};
    if (rawMetrics is Map) {
      rawMetrics.forEach((key, value) {
        if (key is String && value != null) {
          metrics[key] = value.toString();
        }
      });
    }
    return AnimationStep(
      title: JsonHelpers.str(json['title']),
      body: JsonHelpers.str(json['body']),
      tip: JsonHelpers.str(json['tip']),
      visual: JsonHelpers.str(json['visual']),
      metrics: metrics,
    );
  }

  bool get hasMetrics => metrics.isNotEmpty;
}

class LessonAnimation {
  final String title;
  final String subtitle;
  final String theme;
  final List<AnimationStep> steps;

  LessonAnimation({
    this.title = '',
    this.subtitle = '',
    this.theme = 'default',
    List<AnimationStep>? steps,
  }) : steps = steps ?? const [];

  bool get isCrrt => theme == 'crrt';

  factory LessonAnimation.fromJson(Map<String, dynamic> json) {
    return LessonAnimation(
      title: JsonHelpers.str(json['title']),
      subtitle: JsonHelpers.str(json['subtitle']),
      theme: JsonHelpers.str(json['theme'], 'default'),
      steps: JsonHelpers.listOfMaps(json['steps'])
          .map(AnimationStep.fromJson)
          .toList(),
    );
  }
}
