import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:percent_indicator/percent_indicator.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/constants.dart';
import '../config/routes.dart';
import '../providers/auth_provider.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/disclaimer_banner.dart';
import '../widgets/stats_card.dart';
import '../widgets/streak_indicator.dart';
import '../widgets/loading_shimmer.dart';
import '../widgets/category_card.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
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
      body: Consumer2<DashboardProvider, AuthProvider>(
        builder: (context, dashboard, auth, _) {
          return RefreshIndicator(
            onRefresh: dashboard.loadDashboard,
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 8),
                  _buildHeader(context, auth),
                  const SizedBox(height: 20),
                  const DisclaimerBanner(),
                  const SizedBox(height: 20),
                  if (dashboard.isLoading) ...[
                    const LoadingShimmer(),
                  ] else if (dashboard.error != null) ...[
                    _buildErrorWidget(context, dashboard),
                  ] else ...[
                    _buildDailyChallengeCard(context, dashboard),
                    const SizedBox(height: 16),
                    _buildStreakSection(context, dashboard),
                    const SizedBox(height: 16),
                    _buildStatsGrid(context, dashboard),
                    const SizedBox(height: 16),
                    _buildAccuracySection(context, dashboard),
                    const SizedBox(height: 16),
                    if (dashboard.weakTopics.isNotEmpty) ...[
                      _buildWeakTopics(context, dashboard),
                      const SizedBox(height: 16),
                    ],
                    _buildCategoriesSection(context, dashboard),
                    const SizedBox(height: 16),
                    _buildSuggestedPractice(context),
                  ],
                  const SizedBox(height: 80),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildHeader(BuildContext context, AuthProvider auth) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Hello,',
              style: GoogleFonts.inter(
                fontSize: 14,
                color: Theme.of(context)
                    .textTheme
                    .bodyMedium
                    ?.color
                    ?.withOpacity(0.7),
              ),
            ),
            Text(
              auth.user?.displayName ?? 'Doctor',
              style: GoogleFonts.inter(
                fontSize: 24,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
        CircleAvatar(
          radius: 28,
          backgroundColor: Theme.of(context).colorScheme.primary,
          child: Text(
            (auth.user?.displayName ?? 'D')[0].toUpperCase(),
            style: GoogleFonts.inter(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
        ),
      ],
    ).animate().fadeIn(duration: 400.ms).slideX(
          begin: -0.1,
          end: 0,
          duration: 400.ms,
        );
  }

  Widget _buildErrorWidget(BuildContext context, DashboardProvider dashboard) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).cardTheme.color,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          const Icon(Icons.cloud_off, size: 48, color: Colors.grey),
          const SizedBox(height: 16),
          Text(dashboard.error!,
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(fontSize: 14)),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: dashboard.loadDashboard,
            icon: const Icon(Icons.refresh),
            label: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildDailyChallengeCard(
      BuildContext context, DashboardProvider dashboard) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E3A5F), Color(0xFF0D9488)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF0D9488).withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Daily Challenge',
                style: GoogleFonts.inter(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '${dashboard.streakDays} day streak',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            dashboard.dailyChallengeCompleted
                ? "Great job! You've completed today's challenge."
                : 'Answer 5 nephrology questions to maintain your streak.',
            style: GoogleFonts.inter(
              fontSize: 14,
              color: Colors.white70,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                Navigator.of(context).pushNamed(AppRoutes.dailyChallenge);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: const Color(0xFF1E3A5F),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: Text(
                dashboard.dailyChallengeCompleted
                    ? 'View Results'
                    : 'Start Challenge',
              ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 500.ms);
  }

  Widget _buildStreakSection(
      BuildContext context, DashboardProvider dashboard) {
    return StreakIndicator(days: dashboard.streakDays)
        .animate()
        .fadeIn(duration: 400.ms, delay: 100.ms);
  }

  Widget _buildStatsGrid(BuildContext context, DashboardProvider dashboard) {
    return Row(
      children: [
        Expanded(
          child: StatsCard(
            icon: Icons.quiz_outlined,
            label: 'Quizzes',
            value: '${dashboard.totalQuizzes}',
            color: Theme.of(context).colorScheme.primary,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: StatsCard(
            icon: Icons.check_circle_outline,
            label: 'Correct',
            value: '${dashboard.correctAnswers}',
            color: const Color(0xFF22C55E),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: StatsCard(
            icon: Icons.emoji_events_outlined,
            label: 'Points',
            value: '${dashboard.points}',
            color: const Color(0xFFF59E0B),
          ),
        ),
      ],
    ).animate().fadeIn(duration: 400.ms, delay: 200.ms);
  }

  Widget _buildAccuracySection(
      BuildContext context, DashboardProvider dashboard) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardTheme.color,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Theme.of(context).dividerTheme.color!,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          CircularPercentIndicator(
            radius: 40,
            lineWidth: 8,
            percent: dashboard.accuracy / 100,
            center: Text(
              '${dashboard.accuracy.toStringAsFixed(0)}%',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: dashboard.accuracy >= 60
                    ? const Color(0xFF22C55E)
                    : const Color(0xFFEF4444),
              ),
            ),
            progressColor: dashboard.accuracy >= 60
                ? const Color(0xFF22C55E)
                : const Color(0xFFF59E0B),
            backgroundColor: Theme.of(context).dividerTheme.color!,
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Overall Accuracy',
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${dashboard.totalQuestions} questions answered',
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    color: Theme.of(context)
                        .textTheme
                        .bodyMedium
                        ?.color
                        ?.withOpacity(0.7),
                  ),
                ),
                const SizedBox(height: 8),
                LinearPercentIndicator(
                  percent: dashboard.accuracy / 100,
                  lineHeight: 6,
                  backgroundColor: Theme.of(context).dividerTheme.color!,
                  progressColor: dashboard.accuracy >= 60
                      ? const Color(0xFF22C55E)
                      : const Color(0xFFF59E0B),
                  barRadius: const Radius.circular(3),
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 400.ms, delay: 300.ms);
  }

  Widget _buildWeakTopics(
      BuildContext context, DashboardProvider dashboard) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardTheme.color,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Theme.of(context).dividerTheme.color!,
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.trending_down, color: Color(0xFFEF4444)),
              const SizedBox(width: 8),
              Text(
                'Weak Topics',
                style: GoogleFonts.inter(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...dashboard.weakTopics.take(4).map((topic) {
            final name = topic['name'] as String? ?? '';
            final acc = (topic['accuracy'] as num?)?.toDouble() ?? 0.0;
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Row(
                children: [
                  Expanded(
                    child: Text(name,
                        style: GoogleFonts.inter(fontSize: 14)),
                  ),
                  const SizedBox(width: 12),
                  SizedBox(
                    width: 100,
                    child: LinearPercentIndicator(
                      percent: acc / 100,
                      lineHeight: 6,
                      backgroundColor: Theme.of(context).dividerTheme.color!,
                      progressColor: const Color(0xFFEF4444),
                      barRadius: const Radius.circular(3),
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 40,
                    child: Text(
                      '${acc.toStringAsFixed(0)}%',
                      textAlign: TextAlign.right,
                      style: GoogleFonts.inter(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: const Color(0xFFEF4444),
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    ).animate().fadeIn(duration: 400.ms, delay: 400.ms);
  }

  Widget _buildCategoriesSection(
      BuildContext context, DashboardProvider dashboard) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Categories',
              style: GoogleFonts.inter(
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pushNamed(AppRoutes.categories);
              },
              child: const Text('See All'),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 110,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: dashboard.categories.length.clamp(0, 8),
            separatorBuilder: (_, __) => const SizedBox(width: 12),
            itemBuilder: (context, index) {
              final cat = dashboard.categories[index];
              return CategoryCard(
                name: cat.name,
                questionCount: cat.questionCount,
                accuracy: cat.accuracy,
                isLocked: cat.isLocked,
                onTap: () {
                  if (!cat.isLocked) {
                    Navigator.of(context).pushNamed(
                      AppRoutes.categoryQuestions,
                      arguments: cat,
                    );
                  }
                },
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildSuggestedPractice(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF0D9488).withOpacity(0.1),
            const Color(0xFF1E3A5F).withOpacity(0.1),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFF0D9488).withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF0D9488).withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.auto_awesome,
              color: Color(0xFF0D9488),
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AI Tutor',
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Ask questions and get detailed explanations',
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    color: Theme.of(context)
                        .textTheme
                        .bodyMedium
                        .color
                        ?.withOpacity(0.7),
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: () {
              Navigator.of(context).pushNamed(AppRoutes.aiTutor);
            },
            icon: const Icon(Icons.arrow_forward_ios, size: 18),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 400.ms, delay: 500.ms);
  }
}
