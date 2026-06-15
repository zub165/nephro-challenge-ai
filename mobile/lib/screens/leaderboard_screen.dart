import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/leaderboard_provider.dart';
import '../widgets/leaderboard_tile.dart';
import '../widgets/loading_shimmer.dart';

class LeaderboardScreen extends StatefulWidget {
  const LeaderboardScreen({super.key});

  @override
  State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final _periods = ['daily', 'weekly', 'monthly', 'all_time'];
  final _periodLabels = ['Daily', 'Weekly', 'Monthly', 'All Time'];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        context.read<LeaderboardProvider>().setPeriod(_periods[_tabController.index]);
      }
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<LeaderboardProvider>().loadLeaderboard();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Leaderboard'),
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: _periodLabels
              .map((label) => Tab(text: label))
              .toList(),
        ),
      ),
      body: Consumer<LeaderboardProvider>(
        builder: (context, leaderboard, _) {
          if (leaderboard.isLoading) {
            return const LoadingShimmer();
          }

          return RefreshIndicator(
            onRefresh: () => leaderboard.loadLeaderboard(),
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (leaderboard.currentUserEntry != null)
                  _buildCurrentUserCard(context, leaderboard.currentUserEntry!),
                const SizedBox(height: 16),
                if (leaderboard.entries.isEmpty)
                  _buildEmptyState(context)
                else
                  ...leaderboard.entries.map((entry) {
                    final isCurrentUser =
                        leaderboard.currentUserEntry?.userId == entry.userId;
                    return LeaderboardTile(
                      entry: entry,
                      isCurrentUser: isCurrentUser,
                    );
                  }),
                const SizedBox(height: 80),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCurrentUserCard(
      BuildContext context, LeaderboardEntry entry) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E3A5F), Color(0xFF0D9488)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Center(
              child: Text(
                '#${entry.rank}',
                style: GoogleFonts.inter(
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.displayName ?? 'You',
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${entry.quizzesCompleted} quizzes',
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    color: Colors.white70,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${entry.points}',
                style: GoogleFonts.inter(
                  fontSize: 20,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
              Text(
                'pts',
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: Colors.white70,
                ),
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(duration: 400.ms);
  }

  Widget _buildEmptyState(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(40),
      child: Column(
        children: [
          const Icon(Icons.emoji_events_outlined,
              size: 64, color: Colors.grey),
          const SizedBox(height: 16),
          Text(
            'No entries yet',
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Complete quizzes to appear on the leaderboard',
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(
              fontSize: 14,
              color: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.color
                  ?.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }
}
