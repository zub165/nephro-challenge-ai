import '../models/ai_explanation.dart';
import 'api_service.dart';

class AIService {
  static AIService? _instance;
  final ApiService _api = ApiService.instance;

  AIService._();

  static AIService get instance {
    _instance ??= AIService._();
    return _instance!;
  }

  Future<AIExplanation?> getExplanation(String questionId) async {
    try {
      final response = await _api.get('/ai/explanation/$questionId');
      return AIExplanation.fromJson(
          response.data['explanation'] as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<AIExplanation?> getDetailedExplanation({
    required String questionId,
    required String questionText,
    required String selectedAnswer,
    required String correctAnswer,
  }) async {
    try {
      final response = await _api.post('/ai/explanation/detailed', data: {
        'question_id': questionId,
        'question_text': questionText,
        'selected_answer': selectedAnswer,
        'correct_answer': correctAnswer,
      });
      return AIExplanation.fromJson(
          response.data['explanation'] as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<String?> chatWithTutor(String message) async {
    try {
      final response = await _api.post('/ai/tutor/chat', data: {
        'message': message,
      });
      return response.data['response'] as String?;
    } catch (_) {
      return null;
    }
  }

  Future<List<Map<String, dynamic>>> generateQuestions({
    required String topic,
    int count = 5,
    String difficulty = 'medium',
  }) async {
    try {
      final response = await _api.post('/ai/questions/generate', data: {
        'topic': topic,
        'count': count,
        'difficulty': difficulty,
      });
      final data = response.data as Map<String, dynamic>;
      return (data['questions'] as List<dynamic>)
          .map((q) => q as Map<String, dynamic>)
          .toList();
    } catch (_) {
      return [];
    }
  }
}
