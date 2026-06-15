import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/question.dart';
import '../models/quiz_attempt.dart';
import '../models/ai_explanation.dart';
import '../services/quiz_service.dart';
import '../services/ai_service.dart';

enum QuizStatus { idle, loading, playing, paused, completed, reviewing }

class QuizProvider extends ChangeNotifier {
  final QuizService _quizService = QuizService.instance;
  final AIService _aiService = AIService.instance;

  QuizStatus _status = QuizStatus.idle;
  List<Question> _questions = [];
  int _currentIndex = 0;
  String? _selectedChoiceId;
  Map<int, String?> _answers = {};
  int _score = 0;
  int _correctCount = 0;
  int _incorrectCount = 0;
  int _timeLeft = 30;
  Timer? _timer;
  QuizAttempt? _lastAttempt;
  AIExplanation? _currentExplanation;
  bool _isLoadingExplanation = false;
  String? _error;
  String? _categoryId;
  bool _isDailyChallenge = false;

  QuizStatus get status => _status;
  List<Question> get questions => _questions;
  int get currentIndex => _currentIndex;
  String? get selectedChoiceId => _selectedChoiceId;
  int get score => _score;
  int get correctCount => _correctCount;
  int get incorrectCount => _incorrectCount;
  int get timeLeft => _timeLeft;
  QuizAttempt? get lastAttempt => _lastAttempt;
  AIExplanation? get currentExplanation => _currentExplanation;
  bool get isLoadingExplanation => _isLoadingExplanation;
  String? get error => _error;
  bool get isDailyChallenge => _isDailyChallenge;
  double get progress => _questions.isEmpty
      ? 0.0
      : (_currentIndex + 1) / _questions.length;

  Question? get currentQuestion =>
      _currentIndex < _questions.length ? _questions[_currentIndex] : null;

  int get totalQuestions => _questions.length;
  int get answeredCount => _answers.length;
  bool get allAnswered => _answers.length == _questions.length;

  Future<void> loadQuestions({
    String? categoryId,
    bool isDailyChallenge = false,
  }) async {
    _status = QuizStatus.loading;
    _error = null;
    _categoryId = categoryId;
    _isDailyChallenge = isDailyChallenge;
    notifyListeners();

    List<Question> questions;
    if (isDailyChallenge) {
      questions = await _quizService.fetchDailyChallengeQuestions();
    } else {
      questions = await _quizService.fetchQuestions(categoryId: categoryId);
    }

    if (questions.isEmpty) {
      _error = 'No questions available. Please try again later.';
      _status = QuizStatus.idle;
      notifyListeners();
      return;
    }

    _questions = questions;
    _currentIndex = 0;
    _answers = {};
    _score = 0;
    _correctCount = 0;
    _incorrectCount = 0;
    _selectedChoiceId = null;
    _currentExplanation = null;
    _status = QuizStatus.playing;
    _startTimer();
    notifyListeners();
  }

  void _startTimer() {
    _timer?.cancel();
    _timeLeft = currentQuestion?.timeLimitSeconds ?? 30;
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      _timeLeft--;
      if (_timeLeft <= 0) {
        _timeOut();
      }
      notifyListeners();
    });
  }

  void _timeOut() {
    if (_selectedChoiceId == null) {
      selectAnswer(null);
    }
  }

  void selectAnswer(String? choiceId) {
    if (_status != QuizStatus.playing) return;
    if (_answers.containsKey(_currentIndex)) return;

    _selectedChoiceId = choiceId;
    final question = currentQuestion;
    if (question != null) {
      final isCorrect = choiceId != null &&
          question.choices.any((c) => c.id == choiceId && c.isCorrect);
      if (isCorrect) {
        _correctCount++;
        _score += question.points;
      } else {
        _incorrectCount++;
      }
      _answers[_currentIndex] = choiceId;
    }
    notifyListeners();
  }

  void nextQuestion() {
    if (_currentIndex < _questions.length - 1) {
      _currentIndex++;
      _selectedChoiceId = null;
      _startTimer();
      notifyListeners();
    } else {
      _finishQuiz();
    }
  }

  void pauseQuiz() {
    _timer?.cancel();
    _status = QuizStatus.paused;
    notifyListeners();
  }

  void resumeQuiz() {
    _status = QuizStatus.playing;
    _startTimer();
    notifyListeners();
  }

  Future<void> _finishQuiz() async {
    _timer?.cancel();
    _status = QuizStatus.loading;
    notifyListeners();

    final answers = _answers.entries.map((e) {
      final question = _questions[e.key];
      final correctChoice = question.choices.firstWhere(
        (c) => c.isCorrect,
        orElse: () => question.choices.first,
      );
      return {
        'question_id': question.id,
        'selected_choice_id': e.value,
        'correct_choice_id': correctChoice.id,
        'is_correct': e.value != null &&
            question.choices
                .any((c) => c.id == e.value && c.isCorrect),
      };
    }).toList();

    _lastAttempt = await _quizService.submitQuiz(
      answers: answers,
      categoryId: _categoryId,
      isDailyChallenge: _isDailyChallenge,
    );

    _status = QuizStatus.completed;
    notifyListeners();
  }

  Future<void> loadExplanation() async {
    if (currentQuestion == null) return;
    _isLoadingExplanation = true;
    notifyListeners();

    _currentExplanation =
        await _aiService.getExplanation(currentQuestion!.id);

    _isLoadingExplanation = false;
    notifyListeners();
  }

  void restart() {
    _timer?.cancel();
    _status = QuizStatus.idle;
    _questions = [];
    _currentIndex = 0;
    _selectedChoiceId = null;
    _answers = {};
    _score = 0;
    _correctCount = 0;
    _incorrectCount = 0;
    _timeLeft = 30;
    _lastAttempt = null;
    _currentExplanation = null;
    _error = null;
    notifyListeners();
  }

  void goToReview() {
    _status = QuizStatus.reviewing;
    _currentIndex = 0;
    _selectedChoiceId = _answers[0];
    notifyListeners();
  }

  void reviewQuestion(int index) {
    _currentIndex = index;
    _selectedChoiceId = _answers[index];
    notifyListeners();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }
}
