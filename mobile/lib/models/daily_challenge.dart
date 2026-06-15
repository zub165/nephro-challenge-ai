class DailyChallenge {
  final String id;
  final DateTime date;
  final List<String> questionIds;
  final String status;
  final int? score;
  final int? timeTakenSeconds;
  final bool completed;

  DailyChallenge({
    required this.id,
    DateTime? date,
    required this.questionIds,
    this.status = 'pending',
    this.score,
    this.timeTakenSeconds,
    this.completed = false,
  }) : date = date ?? DateTime.now();

  factory DailyChallenge.fromJson(Map<String, dynamic> json) {
    return DailyChallenge(
      id: json['id'] as String,
      date: DateTime.parse(json['date'] as String),
      questionIds:
          (json['question_ids'] as List<dynamic>).map((q) => q as String).toList(),
      status: json['status'] as String? ?? 'pending',
      score: json['score'] as int?,
      timeTakenSeconds: json['time_taken_seconds'] as int?,
      completed: json['completed'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': date.toIso8601String(),
      'question_ids': questionIds,
      'status': status,
      'score': score,
      'time_taken_seconds': timeTakenSeconds,
      'completed': completed,
    };
  }

  bool get isToday {
    final now = DateTime.now();
    return date.year == now.year &&
        date.month == now.month &&
        date.day == now.day;
  }
}
