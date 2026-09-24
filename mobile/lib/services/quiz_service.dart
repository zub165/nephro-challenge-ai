import '../models/category.dart';
import '../models/chapter.dart';
import '../models/question.dart';
import '../models/quiz_attempt.dart';
import '../utils/json_helpers.dart';
import 'api_service.dart';

class QuizService {
  static QuizService? _instance;
  final ApiService _api = ApiService.instance;

  QuizService._();

  static QuizService get instance {
    _instance ??= QuizService._();
    return _instance!;
  }

  Future<List<Question>> fetchQuizQuestions({
    String? categoryId,
    String? chapterId,
    bool daily = false,
    int limit = 10,
  }) async {
    try {
      final response = await _api.get('/questions/quiz/', queryParameters: {
        if (categoryId != null) 'categoryId': categoryId,
        if (chapterId != null) 'chapterId': chapterId,
        if (daily) 'daily': 'true',
        'limit': limit,
      });
      final data = response.data as Map<String, dynamic>;
      return JsonHelpers.listOfMaps(data['questions'])
          .map(Question.fromJson)
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<List<Question>> fetchChapterQuestions(String chapterId,
      {int limit = 10}) async {
    try {
      final response =
          await _api.get('/quiz/chapter/$chapterId/', queryParameters: {
        'limit': limit,
      });
      final data = response.data as Map<String, dynamic>;
      return JsonHelpers.listOfMaps(data['questions'])
          .map(Question.fromJson)
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<List<Category>> fetchCategories() async {
    try {
      final response = await _api.get('/categories/');
      final list = response.data is List
          ? response.data as List
          : (response.data as Map)['results'] as List? ?? [];
      return list
          .map((c) => Category.fromJson(c as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<List<Chapter>> fetchChapters() async {
    try {
      final response = await _api.get('/chapters/');
      final list = response.data is List
          ? response.data as List
          : (response.data as Map)['results'] as List? ?? [];
      return list
          .map((c) => Chapter.fromJson(c as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<Chapter?> fetchChapterDetail(String slug) async {
    try {
      final response = await _api.get('/chapters/$slug/');
      return Chapter.fromJson(response.data as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<Lesson?> fetchLesson(String lessonId) async {
    try {
      final response = await _api.get('/lessons/$lessonId/');
      return Lesson.fromJson(response.data as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<QuizAttempt?> submitQuiz({
    required List<Map<String, dynamic>> answersData,
    String mode = 'practice',
    String? categoryId,
    String? chapterId,
    int timeTaken = 0,
  }) async {
    try {
      final response = await _api.post('/attempts/', data: {
        'mode': mode,
        if (categoryId != null) 'category': categoryId,
        if (chapterId != null) 'chapter': chapterId,
        'total_questions': answersData.length,
        'time_taken': timeTaken,
        'answers_data': answersData,
      });
      return QuizAttempt.fromJson(response.data as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<List<QuizAttempt>> fetchAttempts() async {
    try {
      final response = await _api.get('/attempts/');
      final list = response.data is List
          ? response.data as List
          : (response.data as Map)['results'] as List? ?? [];
      return list
          .map((a) => QuizAttempt.fromJson(a as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<Map<String, dynamic>> fetchDashboard() async {
    try {
      final response = await _api.get('/stats/');
      return response.data as Map<String, dynamic>;
    } catch (_) {
      return {};
    }
  }

  Future<List<Map<String, dynamic>>> fetchWeakTopics() async {
    try {
      final response = await _api.get('/weaknesses/');
      final list = response.data as List<dynamic>;
      return list.map((t) => Map<String, dynamic>.from(t as Map)).toList();
    } catch (_) {
      return [];
    }
  }
}
