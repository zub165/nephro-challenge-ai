import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:percent_indicator/percent_indicator.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:share_plus/share_plus.dart';
import '../config/constants.dart';
import '../config/routes.dart';
import '../providers/auth_provider.dart';
import '../providers/dashboard_provider.dart';
import '../providers/navigation_provider.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      context.read<DashboardProvider>().loadDashboard();
      context.read<AuthProvider>().refreshProfile();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer2<AuthProvider, DashboardProvider>(
        builder: (context, auth, dashboard, _) {
          final user = auth.user;
          if (user == null) {
            return const Center(child: CircularProgressIndicator());
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                const SizedBox(height: 20),
                _buildProfileHeader(context, user, auth, dashboard),
                const SizedBox(height: 24),
                _buildStatsSection(context, dashboard),
                const SizedBox(height: 24),
                _buildMenuItems(context),
                const SizedBox(height: 80),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildProfileHeader(
    BuildContext context,
    dynamic user,
    AuthProvider auth,
    DashboardProvider dashboard,
  ) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E3A5F), Color(0xFF0D9488)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(24),
      ),
      child: Column(
        children: [
          CircleAvatar(
            radius: 48,
            backgroundColor: Colors.white.withValues(alpha: 0.2),
            child: Text(
              (user.displayName ?? 'U')[0].toUpperCase(),
              style: GoogleFonts.inter(
                fontSize: 40,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
          ).animate().scale(
                begin: const Offset(0, 0),
                end: const Offset(1, 1),
                duration: 400.ms,
                curve: Curves.easeOutBack,
              ),
          const SizedBox(height: 16),
          Text(
            user.displayName ?? 'User',
            style: GoogleFonts.inter(
              fontSize: 22,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ).animate().fadeIn(duration: 400.ms, delay: 100.ms),
          const SizedBox(height: 4),
          Text(
            user.email,
            style: GoogleFonts.inter(
              fontSize: 14,
              color: Colors.white70,
            ),
          ).animate().fadeIn(duration: 400.ms, delay: 200.ms),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              dashboard.userRank > 0
                  ? 'Rank #${dashboard.userRank}'
                  : 'Rank —',
              style: GoogleFonts.inter(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.white,
              ),
            ),
          ).animate().fadeIn(duration: 400.ms, delay: 300.ms),
        ],
      ),
    );
  }

  Widget _buildStatsSection(BuildContext context, DashboardProvider dashboard) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardTheme.color,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Theme.of(context).dividerTheme.color!),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem(Icons.quiz_outlined, '${dashboard.totalQuizzes}', 'Quizzes'),
              _buildStatItem(Icons.check_circle_outline, '${dashboard.correctAnswers}', 'Correct'),
              _buildStatItem(Icons.emoji_events_outlined, '${dashboard.points}', 'Points'),
            ],
          ),
          const SizedBox(height: 16),
          const Divider(),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Accuracy',
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        color: Theme.of(context)
                            .textTheme
                            .bodyMedium
                            ?.color
                            ?.withValues(alpha: 0.7),
                      ),
                    ),
                    const SizedBox(height: 8),
                    LinearPercentIndicator(
                      percent: dashboard.accuracy / 100,
                      lineHeight: 8,
                      backgroundColor: Theme.of(context).dividerTheme.color!,
                      progressColor: dashboard.accuracy >= 60
                          ? const Color(0xFF22C55E)
                          : const Color(0xFFF59E0B),
                      barRadius: const Radius.circular(4),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Text(
                '${dashboard.accuracy.toStringAsFixed(0)}%',
                style: GoogleFonts.inter(
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                  color: dashboard.accuracy >= 60
                      ? const Color(0xFF22C55E)
                      : const Color(0xFFF59E0B),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Streak Days',
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        color: Theme.of(context)
                            .textTheme
                            .bodyMedium
                            ?.color
                            ?.withValues(alpha: 0.7),
                      ),
                    ),
                    const SizedBox(height: 8),
                    LinearPercentIndicator(
                      percent: (dashboard.streakDays / 30).clamp(0.0, 1.0),
                      lineHeight: 8,
                      backgroundColor: Theme.of(context).dividerTheme.color!,
                      progressColor: const Color(0xFFF59E0B),
                      barRadius: const Radius.circular(4),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Text(
                '${dashboard.streakDays}d',
                style: GoogleFonts.inter(
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                  color: const Color(0xFFF59E0B),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: Theme.of(context).colorScheme.primary, size: 28),
        const SizedBox(height: 8),
        Text(
          value,
          style: GoogleFonts.inter(
            fontSize: 20,
            fontWeight: FontWeight.w700,
          ),
        ),
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 12,
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

  Widget _buildMenuItems(BuildContext context) {
    final items = [
      {
        'icon': Icons.auto_stories_outlined,
        'title': 'My Book',
        'action': () => context.read<NavigationProvider>().goToLibrary(1),
      },
      {
        'icon': Icons.lightbulb_outline,
        'title': 'Board Pearls',
        'action': () => context.read<NavigationProvider>().goToLibrary(2),
      },
      {
        'icon': Icons.settings_outlined,
        'title': 'Settings',
        'route': AppRoutes.settings,
      },
      {
        'icon': Icons.bar_chart_outlined,
        'title': 'Performance Analytics',
        'route': AppRoutes.performanceAnalytics,
      },
      {
        'icon': Icons.book_outlined,
        'title': 'Study History',
        'route': AppRoutes.studyHistory,
      },
      {
        'icon': Icons.share_outlined,
        'title': 'Share Profile',
        'action': () => _shareProfile(context),
      },
      {
        'icon': Icons.info_outline,
        'title': 'About',
        'route': AppRoutes.about,
      },
      {
        'icon': Icons.logout,
        'title': 'Logout',
        'route': null,
      },
    ];

    return Column(
      children: items.asMap().entries.map((entry) {
        final index = entry.key;
        final item = entry.value;
        final isLogout = item['title'] == 'Logout';
        return Container(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Icon(
              item['icon'] as IconData,
              color: isLogout
                  ? const Color(0xFFEF4444)
                  : Theme.of(context).colorScheme.primary,
            ),
            title: Text(
              item['title'] as String,
              style: GoogleFonts.inter(
                fontSize: 16,
                color: isLogout
                    ? const Color(0xFFEF4444)
                    : null,
              ),
            ),
            trailing: const Icon(Icons.chevron_right, size: 20),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            tileColor: Theme.of(context).cardTheme.color,
            onTap: () {
              if (isLogout) {
                _showLogoutDialog(context);
              } else if (item['action'] != null) {
                (item['action'] as VoidCallback)();
              } else if (item['route'] != null) {
                Navigator.of(context).pushNamed(item['route'] as String);
              }
            },
          ),
        ).animate().fadeIn(
              duration: 300.ms,
              delay: (100 * index).ms,
            );
      }).toList(),
    );
  }

  Future<void> _shareProfile(BuildContext context) async {
    final auth = context.read<AuthProvider>();
    final dash = context.read<DashboardProvider>();
    final user = auth.user;
    if (user == null) return;

    if (dash.totalQuestions == 0 && !dash.isLoading) {
      await dash.loadDashboard();
    }

    final rankText =
        dash.userRank > 0 ? 'Rank #${dash.userRank}' : 'Not ranked yet';
    final text = '''
${user.displayName ?? 'Nephro Challenge AI User'} — Nephro Challenge AI

$rankText · ${dash.accuracy.toStringAsFixed(0)}% accuracy
${dash.totalQuizzes} quizzes · ${dash.streakDays}-day streak
${dash.points} points

Study nephrology board review: ${AppConstants.webAppUrl}
''';

    await Share.share(text.trim());
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              context.read<AuthProvider>().logout();
              Navigator.of(context).pushNamedAndRemoveUntil(
                AppRoutes.login,
                (route) => false,
              );
            },
            child: const Text('Logout', style: TextStyle(color: Color(0xFFEF4444))),
          ),
        ],
      ),
    );
  }
}
