import 'dart:async';
import 'package:flutter/foundation.dart';
import '../config/constants.dart';
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
  final Map<int, String?> _answers = {};
  final Map<int, int> _answerTimes = {};
  int _correctCount = 0;
  int _incorrectCount = 0;
  int _timeLeft = 30;
  Timer? _timer;
  QuizAttempt? _lastAttempt;
  final Map<String, QuizAnswerFeedback> _feedback = {};
  AIExplanation? _currentExplanation;
  bool _isLoadingExplanation = false;
  String? _error;
  String? _categoryId;
  String? _chapterId;
  bool _isDailyChallenge = false;
  bool _revealing = false;
  bool get isRevealingAnswer => _revealing;
  int? _boardDay;
  final Map<int, String> _confidence = {};

  QuizStatus get status => _status;
  List<Question> get questions => _questions;
  int get currentIndex => _currentIndex;
  String? get selectedChoiceId => _selectedChoiceId;
  Map<int, String?> get answers => Map.unmodifiable(_answers);
  int get correctCount => _correctCount;
  int get score => _correctCount * 10;
  int get incorrectCount => _incorrectCount;
  int get timeLeft => _timeLeft;
  QuizAttempt? get lastAttempt => _lastAttempt;
  AIExplanation? get currentExplanation => _currentExplanation;
  bool get isLoadingExplanation => _isLoadingExplanation;
  String? get error => _error;
  bool get isDailyChallenge => _isDailyChallenge;
  int get answeredCount => _answers.length;

  /// Server-marked feedback for a question, or null if not yet known.
  QuizAnswerFeedback? feedbackFor(String questionId) => _feedback[questionId];

  double get progress => _questions.isEmpty
      ? 0.0
      : (_currentIndex + 1) / _questions.length;

  Question? get currentQuestion =>
      _currentIndex < _questions.length ? _questions[_currentIndex] : null;

  int get totalQuestions => _questions.length;

  Future<void> loadQuestions({
    String? categoryId,
    String? chapterId,
    bool isDailyChallenge = false,
    int? boardDay,
    int? limit,
  }) async {
    _status = QuizStatus.loading;
    _error = null;
    _categoryId = categoryId;
    _chapterId = chapterId;
    _isDailyChallenge = isDailyChallenge;
    _boardDay = boardDay;
    notifyListeners();

    List<Question> questions;
    if (chapterId != null) {
      questions = await _quizService.fetchChapterQuestions(chapterId);
    } else {
      questions = await _quizService.fetchQuizQuestions(
        categoryId: categoryId,
        daily: isDailyChallenge,
        boardDay: boardDay,
        limit: limit ??
            (isDailyChallenge
                ? AppConstants.dailyChallengeQuestions
                : boardDay != null
                    ? 18
                    : 10),
      );
    }

    if (questions.isEmpty) {
      _error = 'No questions available. Please try again later.';
      _status = QuizStatus.idle;
      notifyListeners();
      return;
    }

    _questions = questions;
    _currentIndex = 0;
    _answers.clear();
    _answerTimes.clear();
    _confidence.clear();
    _correctCount = 0;
    _incorrectCount = 0;
    _selectedChoiceId = null;
    _feedback.clear();
    _currentExplanation = null;
    _error = null;
    _status = QuizStatus.playing;
    _startTimer();
    notifyListeners();
  }

  void _startTimer() {
    _timer?.cancel();
    _timeLeft = currentQuestion?.timeLimitSeconds ?? 30;
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (_answers.containsKey(_currentIndex)) {
        _timer?.cancel();
        return;
      }
      _timeLeft--;
      if (_timeLeft <= 0) {
        _timer?.cancel();
        _timeLeft = 0;
        selectAnswer(null);
      }
      notifyListeners();
    });
  }

  void selectAnswer(String? choiceId) {
    if (_status != QuizStatus.playing) return;
    if (_answers.containsKey(_currentIndex)) return;

    _selectedChoiceId = choiceId;
    _timer?.cancel();
    final question = currentQuestion;
    if (question != null) {
      _answers[_currentIndex] = choiceId;
      _answerTimes[_currentIndex] =
          (question.timeLimitSeconds - _timeLeft).clamp(0, question.timeLimitSeconds);
    }
    notifyListeners();
    if (choiceId != null) {
      _revealAnswer(choiceId);
    }
  }

  Future<void> _revealAnswer(String choiceId) async {
    final question = currentQuestion;
    if (question == null) return;
    _revealing = true;
    notifyListeners();
    final feedback = await _quizService.checkAnswer(
      questionId: question.id,
      choiceId: choiceId,
    );
    if (feedback != null) {
      _feedback[question.id] = feedback;
      if (feedback.isCorrect) {
        _correctCount++;
      } else {
        _incorrectCount++;
      }
    } else {
      _error = 'Could not load the correct answer. Check your connection.';
    }
    _revealing = false;
    notifyListeners();
  }

  void tagConfidence(String tag) {
    if (tag != 'know' && tag != 'guessed') return;
    _confidence[_currentIndex] = tag;
    notifyListeners();
  }

  String? confidenceForCurrent() => _confidence[_currentIndex];

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
    if (_answers.containsKey(_currentIndex)) {
      _selectedChoiceId = _answers[_currentIndex];
    } else {
      _startTimer();
    }
    notifyListeners();
  }

  Future<void> _finishQuiz() async {
    _timer?.cancel();
    _status = QuizStatus.loading;
    notifyListeners();

    final answersData = _answers.entries
        .where((e) => e.value != null)
        .map((e) {
      final question = _questions[e.key];
      return {
        'question_id': question.id,
        'chosen_choice_id': e.value,
        'time_taken': _answerTimes[e.key] ?? 30,
        'confidence': _confidence[e.key] ?? 'know',
      };
    }).toList();

    try {
      if (answersData.isNotEmpty) {
        final totalTimeTaken = _answerTimes.values.fold<int>(0, (a, b) => a + b);
        _lastAttempt = await _quizService.submitQuiz(
          answersData: answersData,
          mode: _isDailyChallenge
              ? 'daily'
              : _boardDay != null
                  ? 'board_prep'
                  : _chapterId != null
                      ? 'chapter'
                      : _categoryId != null
                          ? 'category'
                          : 'practice',
          categoryId: _categoryId,
          chapterId: _chapterId,
          timeTaken: totalTimeTaken,
        );
        if (_lastAttempt == null) {
          _error =
              'Your quiz could not be saved to the server. Check your connection and try again.';
        } else {
          // The server is the only place answers live. Its marked attempt is
          // the source of truth for the summary and the per-question review.
          _feedback.clear();
          for (final answer in _lastAttempt!.answers) {
            _feedback[answer.questionId] = answer;
          }
          _correctCount = _lastAttempt!.score;
          _incorrectCount =
              (_lastAttempt!.totalQuestions - _lastAttempt!.score).clamp(0, _lastAttempt!.totalQuestions);
        }
      }
    } catch (e) {
      _error = 'Could not save your quiz to the server.';
    }

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
    _answers.clear();
    _answerTimes.clear();
    _confidence.clear();
    _correctCount = 0;
    _incorrectCount = 0;
    _timeLeft = 30;
    _lastAttempt = null;
    _feedback.clear();
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
