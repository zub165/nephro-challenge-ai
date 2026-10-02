import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../config/routes.dart';
import '../services/admin_service.dart';
import '../utils/json_helpers.dart';

class AdminDashboardScreen extends StatefulWidget {
  const AdminDashboardScreen({super.key});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  final _service = AdminService.instance;
  Map<String, dynamic> _stats = {};
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
      final stats = await _service.fetchStats().timeout(const Duration(seconds: 20));
      if (!mounted) return;
      setState(() {
        _stats = stats;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'Could not load admin stats. Admin role is required.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final recent = JsonHelpers.listOfMaps(_stats['recentUsers']);
    return Scaffold(
      appBar: AppBar(title: const Text('Admin')),
      body: Column(
        children: [
          if (_loading) const LinearProgressIndicator(minHeight: 3),
          Expanded(
            child: RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (_error != null)
                    Card(
                      color: Colors.orange.withValues(alpha: 0.12),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Text(_error!),
                      ),
                    ),
                  Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      _stat('Users', JsonHelpers.integer(_stats['totalUsers'])),
                      _stat('Questions', JsonHelpers.integer(_stats['totalQuestions'])),
                      _stat('Pending AI', JsonHelpers.integer(_stats['aiGeneratedPending'])),
                      _stat('Quizzes', JsonHelpers.integer(_stats['totalQuizzes'])),
                    ],
                  ),
                  const SizedBox(height: 20),
                  FilledButton.icon(
                    onPressed: () =>
                        Navigator.of(context).pushNamed(AppRoutes.adminQuestions),
                    icon: const Icon(Icons.quiz_outlined),
                    label: const Text('Questions'),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: () =>
                        Navigator.of(context).pushNamed(AppRoutes.adminAiReview),
                    icon: const Icon(Icons.auto_awesome),
                    label: const Text('AI Review'),
                  ),
                  const SizedBox(height: 24),
                  Text('Recent users',
                      style: GoogleFonts.inter(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 8),
                  ...recent.map(
                    (user) => ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(JsonHelpers.str(user['name'] ?? user['email'])),
                      subtitle: Text(JsonHelpers.str(user['email'])),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _stat(String label, int value) {
    return SizedBox(
      width: 150,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('$value',
                  style: GoogleFonts.inter(
                      fontSize: 22, fontWeight: FontWeight.w800)),
              Text(label, style: GoogleFonts.inter(fontSize: 13)),
            ],
          ),
        ),
      ),
    );
  }
}
