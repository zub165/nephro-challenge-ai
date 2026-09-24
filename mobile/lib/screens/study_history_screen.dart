import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../config/theme.dart';
import '../models/quiz_attempt.dart';
import '../services/quiz_service.dart';

class StudyHistoryScreen extends StatefulWidget {
  const StudyHistoryScreen({super.key});

  @override
  State<StudyHistoryScreen> createState() => _StudyHistoryScreenState();
}

class _StudyHistoryScreenState extends State<StudyHistoryScreen> {
  final QuizService _quizService = QuizService.instance;
  List<QuizAttempt> _attempts = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final attempts = await _quizService.fetchAttempts();
      if (!mounted) return;
      setState(() {
        _attempts = attempts;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Could not load study history. Pull to retry.';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Study History')),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_error!),
            const SizedBox(height: 16),
            FilledButton(onPressed: _load, child: const Text('Retry')),
          ],
        ),
      );
    }
    if (_attempts.isEmpty) {
      return RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          children: const [
            SizedBox(height: 120),
            Center(
              child: Text(
                'No quiz attempts yet.\nComplete a quiz to see your history.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey),
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _attempts.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, index) {
          final attempt = _attempts[index];
          return _AttemptCard(attempt: attempt);
        },
      ),
    );
  }
}

class _AttemptCard extends StatelessWidget {
  const _AttemptCard({required this.attempt});

  final QuizAttempt attempt;

  @override
  Widget build(BuildContext context) {
    final dateStr = attempt.completedAt != null
        ? DateFormat.yMMMd().add_jm().format(attempt.completedAt!.toLocal())
        : 'In progress';

    final passed = attempt.percentage >= 70;

    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: CircleAvatar(
          backgroundColor: passed
              ? AppColors.teal.withValues(alpha: 0.15)
              : Colors.orange.withValues(alpha: 0.15),
          child: Icon(
            passed ? Icons.check : Icons.trending_down,
            color: passed ? AppColors.teal : Colors.orange[800],
          ),
        ),
        title: Text(
          attempt.categoryName ?? attempt.modeLabel,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text('$dateStr · ${attempt.modeLabel}'),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              '${attempt.score}/${attempt.totalQuestions}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              '${attempt.percentage.toStringAsFixed(0)}%',
              style: TextStyle(
                fontSize: 12,
                color: passed ? AppColors.teal : Colors.orange[800],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
