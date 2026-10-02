import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../config/routes.dart';
import '../services/board_exam_service.dart';
import '../utils/json_helpers.dart';

class BoardExamsScreen extends StatefulWidget {
  const BoardExamsScreen({super.key});

  @override
  State<BoardExamsScreen> createState() => _BoardExamsScreenState();
}

class _BoardExamsScreenState extends State<BoardExamsScreen> {
  final _service = BoardExamService.instance;
  List<Map<String, dynamic>> _exams = [];
  bool _loading = true;
  String? _startingSlug;
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
      final exams = await _service.fetchExams().timeout(const Duration(seconds: 20));
      if (!mounted) return;
      setState(() {
        _exams = exams;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'Could not load exams. Pull to retry.';
      });
    }
  }

  Future<void> _start(String slug) async {
    setState(() => _startingSlug = slug);
    try {
      final payload = await _service.startOrResume(slug);
      if (!mounted) return;
      final attemptId = _service.attemptIdOf(payload);
      Navigator.of(context).pushNamed(
        AppRoutes.boardExamTake,
        arguments: {'slug': slug, 'attemptId': attemptId},
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not start exam. Check that it is published.')),
      );
    } finally {
      if (mounted) setState(() => _startingSlug = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Timed board simulation')),
      body: Column(
        children: [
          if (_loading) const LinearProgressIndicator(minHeight: 3),
          Expanded(
            child: RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  Text(
                    'Day 24 of the plan. Answers save on the server. Explanations appear after you submit — not after each pick.',
                    style: GoogleFonts.inter(fontSize: 13, height: 1.4),
                  ),
                  const SizedBox(height: 16),
                  if (_error != null)
                    Card(
                      color: Colors.orange.withValues(alpha: 0.12),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Text(_error!, style: GoogleFonts.inter(fontSize: 13)),
                      ),
                    ),
                  if (!_loading && _exams.isEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 32),
                      child: Text(
                        'No published exams yet. Use morning questions on the 25-day plan until an exam is live.',
                        style: GoogleFonts.inter(color: Colors.grey[600]),
                      ),
                    ),
                  ..._exams.map(_examCard),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () =>
                        Navigator.of(context).pushReplacementNamed(AppRoutes.boardPrep),
                    child: const Text('← Back to 25-day plan'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _examCard(Map<String, dynamic> exam) {
    final slug = JsonHelpers.str(exam['slug']);
    final starting = _startingSlug == slug;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              JsonHelpers.str(exam['title'], 'Board exam'),
              style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 6),
            Text(
              JsonHelpers.str(exam['description']),
              style: GoogleFonts.inter(fontSize: 13, color: Colors.grey[600]),
            ),
            const SizedBox(height: 8),
            Text(
              '${JsonHelpers.integer(exam['question_count'])} questions · '
              '${JsonHelpers.integer(exam['duration_minutes'])} minutes',
              style: GoogleFonts.inter(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: starting || slug.isEmpty ? null : () => _start(slug),
              child: Text(starting ? 'Starting…' : 'Start / resume'),
            ),
          ],
        ),
      ),
    );
  }
}
