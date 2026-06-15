import 'package:flutter/foundation.dart';
import '../models/category.dart';
import '../services/quiz_service.dart';

class DashboardProvider extends ChangeNotifier {
  final QuizService _quizService = QuizService.instance;

  bool _isLoading = false;
  String? _error;
  int _streakDays = 0;
  int _totalQuizzes = 0;
  int _totalQuestions = 0;
  int _correctAnswers = 0;
  double _accuracy = 0.0;
  int _points = 0;
  int _rank = 0;
  bool _dailyChallengeCompleted = false;
  String _dailyChallengeStatus = 'pending';
  List<Category> _categories = [];
  List<Map<String, dynamic>> _weakTopics = [];
  List<Map<String, dynamic>> _recentPerformance = [];

  bool get isLoading => _isLoading;
  String? get error => _error;
  int get streakDays => _streakDays;
  int get totalQuizzes => _totalQuizzes;
  int get totalQuestions => _totalQuestions;
  int get correctAnswers => _correctAnswers;
  double get accuracy => _accuracy;
  int get points => _points;
  int get rank => _rank;
  bool get dailyChallengeCompleted => _dailyChallengeCompleted;
  String get dailyChallengeStatus => _dailyChallengeStatus;
  List<Category> get categories => _categories;
  List<Map<String, dynamic>> get weakTopics => _weakTopics;
  List<Map<String, dynamic>> get recentPerformance => _recentPerformance;

  Future<void> loadDashboard() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await _quizService.fetchDashboard();

      _streakDays = data['streak_days'] as int? ?? 0;
      _totalQuizzes = data['total_quizzes'] as int? ?? 0;
      _totalQuestions = data['total_questions'] as int? ?? 0;
      _correctAnswers = data['correct_answers'] as int? ?? 0;
      _accuracy = (data['accuracy'] as num?)?.toDouble() ?? 0.0;
      _points = data['points'] as int? ?? 0;
      _rank = data['rank'] as int? ?? 0;
      _dailyChallengeCompleted = data['daily_challenge_completed'] as bool? ?? false;
      _dailyChallengeStatus = data['daily_challenge_status'] as String? ?? 'pending';

      if (data['categories'] != null) {
        _categories = (data['categories'] as List<dynamic>)
            .map((c) => Category.fromJson(c as Map<String, dynamic>))
            .toList();
      }

      if (data['recent_performance'] != null) {
        _recentPerformance = (data['recent_performance'] as List<dynamic>)
            .map((p) => p as Map<String, dynamic>)
            .toList();
      }

      _weakTopics = await _quizService.fetchWeakTopics();
    } catch (e) {
      _error = 'Failed to load dashboard data.';
    }

    _isLoading = false;
    notifyListeners();
  }

  void markDailyChallengeCompleted() {
    _dailyChallengeCompleted = true;
    _dailyChallengeStatus = 'completed';
    notifyListeners();
  }
}
