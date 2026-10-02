import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:percent_indicator/circular_percent_indicator.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/routes.dart';
import '../models/quiz_attempt.dart';
import '../providers/navigation_provider.dart';
import '../providers/quiz_provider.dart';
import '../widgets/app_nav_drawer.dart';
import '../widgets/question_card.dart';
import '../widgets/choice_button.dart';

class QuizScreen extends StatefulWidget {
  const QuizScreen({super.key});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final quiz = context.read<QuizProvider>();
      if (quiz.status == QuizStatus.idle) {
        final args = ModalRoute.of(context)?.settings.arguments;
        if (args is Map<String, dynamic>) {
          quiz.loadQuestions(
            categoryId: args['category_id'] as String? ?? args['categoryId'] as String?,
            chapterId: args['chapterId'] as String?,
            isDailyChallenge: args['is_daily_challenge'] as bool? ?? args['daily'] as bool? ?? false,
            boardDay: args['boardDay'] as int?,
            limit: args['limit'] as int?,
          );
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<QuizProvider>(
      builder: (context, quiz, _) {
        return Scaffold(
          appBar: quiz.status == QuizStatus.playing
              ? _buildQuizAppBar(context, quiz)
              : quiz.status == QuizStatus.completed
                  ? AppBar(
                      leading: const AppMenuButton(),
                      title: const Text('Quiz Complete'),
                    )
                  : AppBar(
                      leading: const AppMenuButton(),
                      title: const Text('Quiz'),
                    ),
          body: _buildBody(context, quiz),
        );
      },
    );
  }

  PreferredSizeWidget _buildQuizAppBar(BuildContext context, QuizProvider quiz) {
    return AppBar(
      leading: const AppMenuButton(),
      title: Column(
        children: [
          Text(
            'Question ${quiz.currentIndex + 1} of ${quiz.totalQuestions}',
            style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w500),
          ),
          const SizedBox(height: 4),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: quiz.progress,
              backgroundColor: Colors.white24,
              valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
              minHeight: 4,
            ),
          ),
        ],
      ),
      actions: [
        if (quiz.status == QuizStatus.playing)
          IconButton(
            icon: const Icon(Icons.pause_circle_outline),
            onPressed: quiz.pauseQuiz,
          ),
      ],
    );
  }

  Widget _buildBody(BuildContext context, QuizProvider quiz) {
    final needsReset = quiz.questions.isEmpty &&
        quiz.status != QuizStatus.idle &&
        quiz.status != QuizStatus.loading;
    if (needsReset ||
        (quiz.status == QuizStatus.playing && quiz.currentQuestion == null)) {
      WidgetsBinding.instance.addPostFrameCallback((_) => quiz.restart());
      return const Center(child: CircularProgressIndicator());
    }

    switch (quiz.status) {
      case QuizStatus.loading:
        return const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Loading questions...'),
            ],
          ),
        );
      case QuizStatus.idle:
        return _buildIdleScreen(context, quiz);
      case QuizStatus.playing:
        return _buildQuizInterface(context, quiz);
      case QuizStatus.paused:
        return _buildPausedScreen(context, quiz);
      case QuizStatus.completed:
        return _buildResultsScreen(context, quiz);
      case QuizStatus.reviewing:
        return _buildReviewScreen(context, quiz);
    }
  }

  Widget _buildQuizInterface(BuildContext context, QuizProvider quiz) {
    final question = quiz.currentQuestion;
    if (question == null) {
      return const Center(child: Text('No question'));
    }

    return SafeArea(
      child: Column(
        children: [
          _buildTimer(context, quiz),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  QuestionCard(question: question),
                  const SizedBox(height: 20),
                  ...question.choices.map((choice) {
                    final isSelected = quiz.selectedChoiceId == choice.id;
                    final isAnswered = quiz.answers.containsKey(quiz.currentIndex);
                    final feedback = quiz.feedbackFor(question.id);
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: ChoiceButton(
                        choice: choice,
                        isSelected: isSelected,
                        isAnswered: isAnswered && feedback != null,
                        correctAnswerId: feedback?.correctChoiceId,
                        onTap: () => quiz.selectAnswer(choice.id),
                      ),
                    );
                  }),
                  if (quiz.isRevealingAnswer) ...[
                    const SizedBox(height: 12),
                    const CircularProgressIndicator(),
                  ],
                  if (quiz.feedbackFor(question.id) != null) ...[
                    const SizedBox(height: 12),
                    _buildFeedbackCard(context, quiz.feedbackFor(question.id)!),
                  ],
                  const SizedBox(height: 24),
                  if (quiz.selectedChoiceId != null ||
                      quiz.answers.containsKey(quiz.currentIndex)) ...[
                    if (quiz.feedbackFor(question.id) == null &&
                        !quiz.isRevealingAnswer)
                      Text(
                        'Waiting for the explanation…',
                        style: GoogleFonts.inter(fontSize: 13),
                      )
                    else if (quiz.confidenceForCurrent() == null) ...[
                      Text(
                        'Classify before continuing',
                        style: GoogleFonts.inter(fontSize: 13),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton(
                              onPressed: () {
                                quiz.tagConfidence('know');
                                quiz.nextQuestion();
                              },
                              child: const Text('Know'),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () {
                                quiz.tagConfidence('guessed');
                                quiz.nextQuestion();
                              },
                              child: const Text('Guessed'),
                            ),
                          ),
                        ],
                      ),
                    ] else
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: quiz.nextQuestion,
                          style: ElevatedButton.styleFrom(
                            backgroundColor:
                                Theme.of(context).colorScheme.secondary,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child: Text(
                            quiz.currentIndex < quiz.totalQuestions - 1
                                ? 'Next Question'
                                : 'See Results',
                          ),
                        ),
                      ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimer(BuildContext context, QuizProvider quiz) {
    final timeLeft = quiz.timeLeft;
    final totalTime = quiz.currentQuestion?.timeLimitSeconds ?? 30;
    final percent = timeLeft / totalTime;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          CircularPercentIndicator(
            radius: 16,
            lineWidth: 3,
            percent: percent.clamp(0.0, 1.0),
            center: Text(
              '$timeLeft',
              style: GoogleFonts.inter(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: timeLeft <= 5
                    ? const Color(0xFFEF4444)
                    : Theme.of(context).colorScheme.primary,
              ),
            ),
            progressColor: timeLeft <= 5
                ? const Color(0xFFEF4444)
                : Theme.of(context).colorScheme.secondary,
            backgroundColor: Theme.of(context).dividerTheme.color!,
          ),
          const Spacer(),
          Text(
            'Score: ${quiz.score}',
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIdleScreen(BuildContext context, QuizProvider quiz) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.quiz_outlined,
                size: 72, color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 20),
            Text(
              'Practice Quiz',
              style: GoogleFonts.inter(
                fontSize: 24,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Start a random set of board-style MCQs, or open a chapter for topic-focused review.',
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(fontSize: 14, color: Colors.grey[600]),
            ),
            if (quiz.error != null) ...[
              const SizedBox(height: 16),
              Text(
                quiz.error!,
                textAlign: TextAlign.center,
                style: GoogleFonts.inter(color: Colors.red[700], fontSize: 14),
              ),
            ],
            const SizedBox(height: 28),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => quiz.loadQuestions(),
                icon: const Icon(Icons.play_arrow),
                label: const Text('Start Practice Quiz'),
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () =>
                    context.read<NavigationProvider>().goToShellTab(1),
                icon: const Icon(Icons.menu_book_outlined),
                label: const Text('Browse Chapters'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPausedScreen(BuildContext context, QuizProvider quiz) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.pause_circle, size: 80, color: Color(0xFF1E3A5F)),
          const SizedBox(height: 24),
          Text(
            'Quiz Paused',
            style: GoogleFonts.inter(fontSize: 24, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
            '${quiz.answeredCount} of ${quiz.totalQuestions} questions answered',
            style: GoogleFonts.inter(
              fontSize: 14,
              color: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.color
                  ?.withValues(alpha: 0.7),
            ),
          ),
          const SizedBox(height: 32),
          ElevatedButton.icon(
            onPressed: quiz.resumeQuiz,
            icon: const Icon(Icons.play_arrow),
            label: const Text('Resume'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResultsScreen(BuildContext context, QuizProvider quiz) {
    final accuracy = quiz.totalQuestions > 0
        ? (quiz.correctCount / quiz.totalQuestions) * 100
        : 0.0;
    final isPassed = accuracy >= 60;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 20),
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isPassed
                  ? const Color(0xFF22C55E).withValues(alpha: 0.1)
                  : const Color(0xFFEF4444).withValues(alpha: 0.1),
            ),
            child: CircularPercentIndicator(
              radius: 60,
              lineWidth: 10,
              percent: accuracy / 100,
              center: Icon(
                isPassed ? Icons.check_circle : Icons.cancel,
                size: 48,
                color: isPassed
                    ? const Color(0xFF22C55E)
                    : const Color(0xFFEF4444),
              ),
              progressColor: isPassed
                  ? const Color(0xFF22C55E)
                  : const Color(0xFFEF4444),
              backgroundColor: Theme.of(context).dividerTheme.color!,
            ),
          ).animate().scale(
                begin: const Offset(0, 0),
                end: const Offset(1, 1),
                duration: 600.ms,
                curve: Curves.easeOutBack,
              ),
          const SizedBox(height: 24),
          Text(
            isPassed ? 'Great Job!' : 'Keep Practicing!',
            style: GoogleFonts.inter(
              fontSize: 28,
              fontWeight: FontWeight.w700,
              color: isPassed
                  ? const Color(0xFF22C55E)
                  : const Color(0xFFEF4444),
            ),
          ).animate().fadeIn(duration: 400.ms, delay: 300.ms),
          const SizedBox(height: 8),
          Text(
            '${accuracy.toStringAsFixed(0)}% Accuracy',
            style: GoogleFonts.inter(
              fontSize: 16,
              color: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.color
                  ?.withValues(alpha: 0.7),
            ),
          ).animate().fadeIn(duration: 400.ms, delay: 400.ms),
          const SizedBox(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildResultStat(
                'Correct',
                '${quiz.correctCount}',
                const Color(0xFF22C55E),
              ),
              _buildResultStat(
                'Incorrect',
                '${quiz.incorrectCount}',
                const Color(0xFFEF4444),
              ),
              _buildResultStat(
                'Score',
                '${quiz.score}',
                const Color(0xFFF59E0B),
              ),
            ],
          ).animate().fadeIn(duration: 400.ms, delay: 500.ms),
          const SizedBox(height: 32),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => quiz.loadExplanation(),
              icon: const Icon(Icons.auto_awesome),
              label: const Text('AI Explanation'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0D9488),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ).animate().fadeIn(duration: 400.ms, delay: 600.ms),
          if (quiz.currentExplanation != null) ...[
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () {
                  Navigator.of(context).pushNamed(
                    AppRoutes.explanation,
                    arguments: quiz.currentExplanation,
                  );
                },
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('View Explanation'),
              ),
            ),
          ],
          if (quiz.isLoadingExplanation)
            const Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(),
            ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: quiz.goToReview,
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: const Text('Review Answers'),
            ),
          ).animate().fadeIn(duration: 400.ms, delay: 700.ms),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: TextButton(
              onPressed: () {
                quiz.restart();
                Navigator.of(context).pop();
              },
              child: const Text('Back to Dashboard'),
            ),
          ).animate().fadeIn(duration: 400.ms, delay: 800.ms),
        ],
      ),
    );
  }

  Widget _buildFeedbackCard(BuildContext context, QuizAnswerFeedback feedback) {
    final theme = Theme.of(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0D9488).withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF0D9488).withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            feedback.isCorrect ? 'Correct' : 'Incorrect',
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: feedback.isCorrect
                  ? const Color(0xFF22C55E)
                  : const Color(0xFFEF4444),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            feedback.explanation,
            style: GoogleFonts.inter(fontSize: 14, height: 1.45),
          ),
          if (feedback.whyWrong.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              'Why it\'s wrong: ${feedback.whyWrong}',
              style: GoogleFonts.inter(
                fontSize: 13,
                height: 1.4,
                color: theme.textTheme.bodyMedium?.color?.withValues(alpha: 0.85),
              ),
            ),
          ],
          if (feedback.clinicalPearl.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              'Pearl: ${feedback.clinicalPearl}',
              style: GoogleFonts.inter(
                fontSize: 13,
                height: 1.4,
                fontWeight: FontWeight.w600,
                color: const Color(0xFFD97706),
              ),
            ),
          ],
          if (feedback.reference.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              'Reference: ${feedback.reference}',
              style: GoogleFonts.inter(
                fontSize: 12,
                height: 1.4,
                color: theme.textTheme.bodyMedium?.color?.withValues(alpha: 0.7),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildResultStat(String label, String value, Color color) {
    return Column(
      children: [
        Container(
          width: 72,
          height: 72,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withValues(alpha: 0.1),
          ),
          child: Center(
            child: Text(
              value,
              style: GoogleFonts.inter(
                fontSize: 24,
                fontWeight: FontWeight.w700,
                color: color,
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 13,
            color: Theme.of(context)
                .textTheme
                .bodyMedium
                ?.color
                ?.withValues(alpha: 0.7),
          ),
        ),
      ],
    );
  }

  Widget _buildReviewScreen(BuildContext context, QuizProvider quiz) {
    final question = quiz.currentQuestion;
    if (question == null) {
      return const Center(child: Text('No question'));
    }
    final feedback = quiz.feedbackFor(question.id);

    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Text(
                'Review Mode',
                style: GoogleFonts.inter(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              Text(
                '${quiz.currentIndex + 1}/${quiz.totalQuestions}',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: Theme.of(context)
                      .textTheme
                      .bodyMedium
                      ?.color
                      ?.withValues(alpha: 0.7),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                QuestionCard(question: question),
                const SizedBox(height: 20),
                ...question.choices.map((choice) {
                  final isSelected = quiz.selectedChoiceId == choice.id;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: ChoiceButton(
                      choice: choice,
                      isSelected: isSelected,
                      isAnswered: true,
                      correctAnswerId: feedback?.correctChoiceId,
                      onTap: () {},
                      readOnly: true,
                    ),
                  );
                }),
                if (feedback != null) ...[
                  const SizedBox(height: 8),
                  _buildFeedbackCard(context, feedback),
                ],
              ],
            ),
          ),
        ),
        Container(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              if (quiz.currentIndex > 0)
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => quiz.reviewQuestion(quiz.currentIndex - 1),
                    child: const Text('Previous'),
                  ),
                ),
              if (quiz.currentIndex > 0) const SizedBox(width: 12),
              if (quiz.currentIndex < quiz.totalQuestions - 1)
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => quiz.reviewQuestion(quiz.currentIndex + 1),
                    child: const Text('Next'),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}
