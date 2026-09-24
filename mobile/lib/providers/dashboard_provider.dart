import 'package:flutter/foundation.dart';
import '../models/category.dart' as app_models;
import '../models/quiz_attempt.dart';
import '../services/leaderboard_service.dart';
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
  bool _dailyChallengeCompleted = false;
  List<app_models.Category> _categories = [];
  List<Map<String, dynamic>> _weakTopics = [];

  List<CategoryPerformance> _categoryBreakdown = [];
  List<Map<String, dynamic>> _recentActivity = [];
  int _userRank = 0;

  bool get isLoading => _isLoading;
  String? get error => _error;
  int get streakDays => _streakDays;
  int get totalQuizzes => _totalQuizzes;
  int get totalQuestions => _totalQuestions;
  int get correctAnswers => _correctAnswers;
  double get accuracy => _accuracy;
  bool get dailyChallengeCompleted => _dailyChallengeCompleted;
  List<app_models.Category> get categories => _categories;
  List<Map<String, dynamic>> get weakTopics => _weakTopics;
  List<CategoryPerformance> get categoryBreakdown => _categoryBreakdown;
  List<Map<String, dynamic>> get recentActivity => _recentActivity;
  int get userRank => _userRank;
  int get points => _correctAnswers * 10;

  Future<void> loadDashboard() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await _quizService.fetchDashboard();
      _streakDays = (data['currentStreak'] as num?)?.toInt() ?? 0;
      _totalQuizzes = (data['totalQuizzes'] as num?)?.toInt() ?? 0;
      _totalQuestions = (data['totalQuestions'] as num?)?.toInt() ?? 0;
      _correctAnswers = (data['correctAnswers'] as num?)?.toInt() ?? 0;
      _accuracy = (data['accuracy'] as num?)?.toDouble() ?? 0.0;
      _dailyChallengeCompleted = data['dailyQuizCompleted'] as bool? ?? false;
      _categoryBreakdown = (data['categoryBreakdown'] as List<dynamic>? ?? [])
          .map((c) => CategoryPerformance.fromJson(c as Map<String, dynamic>))
          .toList();
      _recentActivity = (data['recentActivity'] as List<dynamic>? ?? [])
          .map((a) => Map<String, dynamic>.from(a as Map))
          .toList();
      _categories = await _quizService.fetchCategories();
      _weakTopics = await _quizService.fetchWeakTopics();
      final rankEntry =
          await LeaderboardService.instance.fetchCurrentUserRank();
      _userRank = rankEntry?.rank ?? 0;
    } catch (e) {
      _error = 'Failed to load dashboard. Check your connection.';
    }

    _isLoading = false;
    notifyListeners();
  }

  void markDailyChallengeCompleted() {
    _dailyChallengeCompleted = true;
    notifyListeners();
  }
}
