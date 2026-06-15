import '../models/question.dart';
import '../models/quiz_attempt.dart';
import 'api_service.dart';

class QuizService {
  static QuizService? _instance;
  final ApiService _api = ApiService.instance;

  QuizService._();

  static QuizService get instance {
    _instance ??= QuizService._();
    return _instance!;
  }

  Future<List<Question>> fetchQuestions({
    String? categoryId,
    int limit = 10,
    String? difficulty,
  }) async {
    try {
      final response = await _api.get('/questions', queryParameters: {
        if (categoryId != null) 'category_id': categoryId,
        'limit': limit,
        if (difficulty != null) 'difficulty': difficulty,
      });
      final data = response.data as Map<String, dynamic>;
      final questions = (data['questions'] as List<dynamic>)
          .map((q) => Question.fromJson(q as Map<String, dynamic>))
          .toList();
      return questions;
    } catch (_) {
      return [];
    }
  }

  Future<List<Question>> fetchDailyChallengeQuestions() async {
    try {
      final response = await _api.get('/questions/daily-challenge');
      final data = response.data as Map<String, dynamic>;
      final questions = (data['questions'] as List<dynamic>)
          .map((q) => Question.fromJson(q as Map<String, dynamic>))
          .toList();
      return questions;
    } catch (_) {
      return [];
    }
  }

  Future<QuizAttempt?> submitQuiz({
    required List<Map<String, dynamic>> answers,
    String? categoryId,
    bool isDailyChallenge = false,
  }) async {
    try {
      final response = await _api.post('/quizzes/submit', data: {
        'answers': answers,
        if (categoryId != null) 'category_id': categoryId,
        'is_daily_challenge': isDailyChallenge,
      });
      return QuizAttempt.fromJson(
          response.data['attempt'] as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<List<QuizAttempt>> fetchAttempts({int limit = 20}) async {
    try {
      final response =
          await _api.get('/quizzes/attempts', queryParameters: {'limit': limit});
      final data = response.data as Map<String, dynamic>;
      final attempts = (data['attempts'] as List<dynamic>)
          .map((a) => QuizAttempt.fromJson(a as Map<String, dynamic>))
          .toList();
      return attempts;
    } catch (_) {
      return [];
    }
  }

  Future<Map<String, dynamic>> fetchDashboard() async {
    try {
      final response = await _api.get('/quizzes/dashboard');
      return response.data as Map<String, dynamic>;
    } catch (_) {
      return {};
    }
  }

  Future<List<Map<String, dynamic>>> fetchWeakTopics() async {
    try {
      final response = await _api.get('/quizzes/weak-topics');
      final data = response.data as Map<String, dynamic>;
      return (data['topics'] as List<dynamic>)
          .map((t) => t as Map<String, dynamic>)
          .toList();
    } catch (_) {
      return [];
    }
  }
}
