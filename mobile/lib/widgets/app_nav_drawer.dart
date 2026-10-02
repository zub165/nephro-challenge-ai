import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

import '../config/routes.dart';
import '../providers/auth_provider.dart';
import '../providers/navigation_provider.dart';

class AppMenuButton extends StatelessWidget {
  const AppMenuButton({super.key});

  @override
  Widget build(BuildContext context) {
    if (Navigator.of(context).canPop()) {
      return const BackButton();
    }
    return IconButton(
      icon: const Icon(Icons.menu),
      tooltip: 'Menu',
      onPressed: () => context.read<NavigationProvider>().openMenu(),
    );
  }
}

class AppNavDrawer extends StatelessWidget {
  const AppNavDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    final nav = context.read<NavigationProvider>();
    final user = context.watch<AuthProvider>().user;
    final isAdmin = user?.role == 'admin';

    final navigator = Navigator.of(context);
    void goNamed(String route) {
      navigator.pop();
      navigator.pushNamed(route);
    }

    void goTab(int index, {int libraryTab = 0}) {
      navigator.pop();
      nav.goToShellTab(index, libraryTab: libraryTab);
    }

    return Drawer(
      child: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(vertical: 8),
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 16),
              child: Text(
                'NephroChallenge',
                style: GoogleFonts.inter(
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            _item(context, Icons.dashboard_outlined, 'Dashboard',
                () => goTab(0)),
            _item(context, Icons.calendar_today_outlined, 'Board Plan',
                () => goNamed(AppRoutes.boardPrep)),
            _item(context, Icons.menu_book_outlined, 'Chapters',
                () => goTab(1, libraryTab: 0)),
            _item(context, Icons.lightbulb_outline, 'Board Pearls',
                () => goTab(1, libraryTab: 2)),
            _item(context, Icons.auto_stories_outlined, 'My Book',
                () => goTab(1, libraryTab: 1)),
            _item(context, Icons.wb_sunny_outlined, 'Daily Challenge',
                () => goNamed(AppRoutes.dailyChallenge)),
            _item(context, Icons.category_outlined, 'Categories',
                () => goNamed(AppRoutes.categories)),
            _item(context, Icons.emoji_events_outlined, 'Leaderboard',
                () => goTab(3)),
            _item(context, Icons.person_outline, 'Profile', () => goTab(4)),
            if (isAdmin) ...[
              const Divider(),
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 8, 20, 4),
                child: Text(
                  'Admin',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: Colors.grey,
                  ),
                ),
              ),
              _item(context, Icons.admin_panel_settings_outlined, 'Admin',
                  () => goNamed(AppRoutes.admin)),
              _item(context, Icons.quiz_outlined, 'Questions',
                  () => goNamed(AppRoutes.adminQuestions)),
              _item(context, Icons.auto_awesome_outlined, 'AI Review',
                  () => goNamed(AppRoutes.adminAiReview)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _item(
    BuildContext context,
    IconData icon,
    String label,
    VoidCallback onTap,
  ) {
    return ListTile(
      leading: Icon(icon),
      title: Text(label, style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
      onTap: onTap,
    );
  }
}
