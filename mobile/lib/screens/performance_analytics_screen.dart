import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../providers/dashboard_provider.dart';

class PerformanceAnalyticsScreen extends StatefulWidget {
  const PerformanceAnalyticsScreen({super.key});

  @override
  State<PerformanceAnalyticsScreen> createState() =>
      _PerformanceAnalyticsScreenState();
}

class _PerformanceAnalyticsScreenState
    extends State<PerformanceAnalyticsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DashboardProvider>().loadDashboard();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Performance Analytics')),
      body: Consumer<DashboardProvider>(
        builder: (context, dash, _) {
          if (dash.isLoading && dash.totalQuestions == 0) {
            return const Center(child: CircularProgressIndicator());
          }
          if (dash.error != null && dash.totalQuestions == 0) {
            return _ErrorState(
              message: dash.error!,
              onRetry: () => dash.loadDashboard(),
            );
          }

          return RefreshIndicator(
            onRefresh: () => dash.loadDashboard(),
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _SummaryGrid(dash: dash),
                const SizedBox(height: 20),
                Text(
                  'Category Breakdown',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
                if (dash.categoryBreakdown.isEmpty)
                  const _EmptyCard(
                    message: 'Complete quizzes to see category analytics.',
                  )
                else
                  ...dash.categoryBreakdown.map(
                    (c) => _CategoryRow(
                      name: c.categoryName,
                      accuracy: c.accuracy,
                      correct: c.correctAnswers,
                      total: c.totalQuestions,
                    ),
                  ),
                const SizedBox(height: 20),
                Text(
                  'Weak Topics',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
                if (dash.weakTopics.isEmpty)
                  const _EmptyCard(
                    message: 'No weak topics yet — keep studying!',
                  )
                else
                  ...dash.weakTopics.map(
                    (w) => _WeakTopicRow(
                      name: (w['name'] as String? ?? w['category'] as String? ?? w['chapter'] as String? ?? w['subcategory'] as String? ?? 'Unknown').toString(),
                      accuracy: (w['accuracy'] as num?)?.toDouble() ?? 0,
                    ),
                  ),
                const SizedBox(height: 20),
                Text(
                  'Recent Activity',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 12),
                if (dash.recentActivity.isEmpty)
                  const _EmptyCard(message: 'No recent quiz activity.')
                else
                  ...dash.recentActivity.map(
                    (a) => _ActivityRow(
                      date: a['date']?.toString() ?? '',
                      quizzes: a['quizzesCompleted'] as int? ?? 0,
                      questions: a['questionsAnswered'] as int? ?? 0,
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _SummaryGrid extends StatelessWidget {
  const _SummaryGrid({required this.dash});

  final DashboardProvider dash;

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.4,
      children: [
        _StatTile(label: 'Accuracy', value: '${dash.accuracy.toStringAsFixed(1)}%'),
        _StatTile(label: 'Quizzes', value: '${dash.totalQuizzes}'),
        _StatTile(label: 'Questions', value: '${dash.totalQuestions}'),
        _StatTile(label: 'Streak', value: '${dash.streakDays} days'),
        _StatTile(label: 'Rank', value: dash.userRank > 0 ? '#${dash.userRank}' : '—'),
        _StatTile(label: 'Points', value: '${dash.points}'),
      ],
    );
  }
}

class _StatTile extends StatelessWidget {
  const _StatTile({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              value,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.teal,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey[600],
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CategoryRow extends StatelessWidget {
  const _CategoryRow({
    required this.name,
    required this.accuracy,
    required this.correct,
    required this.total,
  });

  final String name;
  final double accuracy;
  final int correct;
  final int total;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(name),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 6),
          child: LinearProgressIndicator(
            value: total > 0 ? correct / total : 0,
            backgroundColor: Colors.grey[200],
            color: AppColors.teal,
          ),
        ),
        trailing: Text(
          '${accuracy.toStringAsFixed(0)}%',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}

class _WeakTopicRow extends StatelessWidget {
  const _WeakTopicRow({required this.name, required this.accuracy});

  final String name;
  final double accuracy;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(Icons.warning_amber_rounded, color: Colors.orange[700]),
        title: Text(name),
        trailing: Text(
          '${accuracy.toStringAsFixed(0)}%',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.orange[800],
          ),
        ),
      ),
    );
  }
}

class _ActivityRow extends StatelessWidget {
  const _ActivityRow({
    required this.date,
    required this.quizzes,
    required this.questions,
  });

  final String date;
  final int quizzes;
  final int questions;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: const Icon(Icons.calendar_today_outlined),
        title: Text(date),
        subtitle: Text('$quizzes quiz${quizzes == 1 ? '' : 'zes'} · $questions questions'),
      ),
    );
  }
}

class _EmptyCard extends StatelessWidget {
  const _EmptyCard({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Text(
          message,
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.grey[600]),
        ),
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton(onPressed: onRetry, child: const Text('Retry')),
          ],
        ),
      ),
    );
  }
}
