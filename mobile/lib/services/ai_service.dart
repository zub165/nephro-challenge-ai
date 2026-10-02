import 'package:dio/dio.dart';

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

  String _tutorFailureMessage(Object error) {
    if (error is DioException) {
      final code = error.response?.statusCode;
      if (code == 403) {
        return 'AI Tutor requires a premium or admin account. '
            'Your current plan can still use quizzes, chapters, Board Plan, and pearls.';
      }
      if (code == 401) {
        return 'Your session expired. Please sign out and sign in again, then retry AI Tutor.';
      }
      if (error.type == DioExceptionType.connectionTimeout ||
          error.type == DioExceptionType.receiveTimeout ||
          error.type == DioExceptionType.sendTimeout) {
        return 'The AI tutor timed out. Please try again in a moment.';
      }
      if (error.type == DioExceptionType.connectionError) {
        return 'No network connection. Check internet and try again.';
      }
    }
    return 'I\'m sorry, I couldn\'t process that request.';
  }

  Future<AIExplanation?> getExplanation(String questionId) async {
    try {
      final response = await _api.post('/ai/explain/', data: {
        'question_id': questionId,
      }, timeout: const Duration(seconds: 60));
      final text = response.data['explanation'] as String? ?? '';
      return AIExplanation(
        id: questionId,
        questionId: questionId,
        explanation: text,
        references: const [],
      );
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
      }, timeout: const Duration(seconds: 60));
      return AIExplanation.fromJson(
          response.data['explanation'] as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<String> chatWithTutor(String message) async {
    try {
      final response = await _api.post('/ai/tutor/chat', data: {
        'message': message,
      }, timeout: const Duration(seconds: 60));
      final text = response.data['response'] as String?;
      if (text != null && text.trim().isNotEmpty) return text;
      return 'The AI tutor is currently unavailable. Please try again shortly.';
    } catch (error) {
      return _tutorFailureMessage(error);
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
      }, timeout: const Duration(seconds: 90));
      final data = response.data as Map<String, dynamic>;
      return (data['questions'] as List<dynamic>)
          .map((q) => q as Map<String, dynamic>)
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<Map<String, dynamic>> generateBoardPrep({
    required String topic,
    int count = 3,
    String difficulty = 'medium',
  }) async {
    try {
      final response = await _api.post('/ai/board-prep', data: {
        'topic': topic,
        'count': count,
        'difficulty': difficulty,
      }, timeout: const Duration(minutes: 5));
      return response.data as Map<String, dynamic>;
    } catch (_) {
      return {'questions': [], 'generated': false};
    }
  }
}
