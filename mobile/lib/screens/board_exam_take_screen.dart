import 'dart:async';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../config/routes.dart';
import '../services/board_exam_service.dart';
import '../utils/json_helpers.dart';

class BoardExamTakeScreen extends StatefulWidget {
  const BoardExamTakeScreen({super.key});

  @override
  State<BoardExamTakeScreen> createState() => _BoardExamTakeScreenState();
}

class _BoardExamTakeScreenState extends State<BoardExamTakeScreen> {
  final _service = BoardExamService.instance;
  String _attemptId = '';
  String _slug = '';
  Map<String, dynamic> _attempt = {};
  Map<String, dynamic>? _graded;
  int _index = 0;
  bool _loading = true;
  bool _saving = false;
  bool _submitting = false;
  String? _error;
  Timer? _ticker;
  int _remaining = 0;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_attemptId.isNotEmpty) return;
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map) {
      _slug = JsonHelpers.str(args['slug']);
      _attemptId = JsonHelpers.str(args['attemptId']);
    }
    _load();
  }

  @override
  void dispose() {
    _ticker?.cancel();
    super.dispose();
  }

  void _startTicker() {
    _ticker?.cancel();
    _ticker = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted || _graded != null) return;
      setState(() {
        if (_remaining > 0) _remaining -= 1;
      });
      if (_remaining <= 0) {
        _ticker?.cancel();
        _loadResultsAfterExpire();
      }
    });
  }

  Future<void> _load() async {
    if (_attemptId.isEmpty) {
      setState(() {
        _loading = false;
        _error = 'Missing attempt. Start again from the exam list.';
      });
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await _service.fetchAttempt(_attemptId).timeout(
            const Duration(seconds: 20),
          );
      if (!mounted) return;
      setState(() {
        _attempt = data;
        _remaining = JsonHelpers.integer(data['remaining_seconds']);
        _loading = false;
      });
      _startTicker();
    } catch (_) {
      try {
        final results = await _service.fetchResults(_attemptId);
        if (!mounted) return;
        setState(() {
          _graded = results;
          _loading = false;
        });
      } catch (_) {
        if (!mounted) return;
        setState(() {
          _loading = false;
          _error = 'This attempt is not active. Check results or start again.';
        });
      }
    }
  }

  Future<void> _loadResultsAfterExpire() async {
    try {
      final results = await _service.fetchResults(_attemptId);
      if (!mounted) return;
      setState(() => _graded = results);
    } catch (_) {}
  }

  List<Map<String, dynamic>> get _items =>
      JsonHelpers.listOfMaps(_attempt['items']);

  Future<void> _pick(String key) async {
    if (_index >= _items.length) return;
    final position = JsonHelpers.integer(_items[_index]['position'], _index + 1);
    setState(() {
      _saving = true;
      final items = JsonHelpers.listOfMaps(_attempt['items']);
      if (_index < items.length) {
        items[_index]['selected_choice_key'] = key;
        _attempt['items'] = items;
      }
    });
    try {
      await _service.saveAnswer(
        attemptId: _attemptId,
        position: position,
        choiceKey: key,
      );
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not save that answer. Try again.')),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _submit() async {
    setState(() => _submitting = true);
    try {
      final payload = await _service.submit(_attemptId);
      if (!mounted) return;
      setState(() => _graded = payload);
      _ticker?.cancel();
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not submit exam.')),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  String _clock(int seconds) {
    final m = (seconds ~/ 60).toString().padLeft(2, '0');
    final s = (seconds % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_slug.isEmpty ? 'Board exam' : _slug),
        actions: [
          if (_graded == null)
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Center(
                child: Text(
                  _clock(_remaining),
                  style: GoogleFonts.inter(fontWeight: FontWeight.w700),
                ),
              ),
            ),
        ],
      ),
      body: Column(
        children: [
          if (_loading || _saving || _submitting)
            const LinearProgressIndicator(minHeight: 3),
          Expanded(child: _body()),
        ],
      ),
    );
  }

  Widget _body() {
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(_error!, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              FilledButton(
                onPressed: () =>
                    Navigator.of(context).pushReplacementNamed(AppRoutes.boardExams),
                child: const Text('Exams'),
              ),
            ],
          ),
        ),
      );
    }

    if (_graded != null) {
      final correct = JsonHelpers.integer(
        _graded!['correct_count'] ?? _graded!['score'],
      );
      final total = JsonHelpers.integer(_graded!['total_questions']);
      return Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Exam submitted',
                style: GoogleFonts.inter(fontSize: 22, fontWeight: FontWeight.w800)),
            const SizedBox(height: 12),
            Text(
              'Score $correct / $total',
              style: GoogleFonts.inter(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              'Explanations and pearls are on the review queue and chapter knowledge — not during the timed block.',
              style: GoogleFonts.inter(fontSize: 13, height: 1.4),
            ),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: () => Navigator.of(context).pushNamedAndRemoveUntil(
                AppRoutes.boardPrep,
                (route) => route.settings.name == AppRoutes.dashboard,
              ),
              child: const Text('Review plan weak areas'),
            ),
          ],
        ),
      );
    }

    if (_items.isEmpty) {
      return const Center(child: Text('Loading exam…'));
    }

    final item = _items[_index];
    final question = Map<String, dynamic>.from(item['question'] as Map? ?? {});
    final choices = JsonHelpers.listOfMaps(question['choices']);
    final selected = JsonHelpers.str(item['selected_choice_key']);
    final caseText = JsonHelpers.str(question['case_text']);
    final stem = JsonHelpers.str(question['question_text']);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Question ${_index + 1} / ${_items.length}',
          style: GoogleFonts.inter(fontSize: 13, color: Colors.grey[600]),
        ),
        const SizedBox(height: 12),
        if (caseText.isNotEmpty) ...[
          Text(caseText, style: GoogleFonts.inter(fontSize: 14, height: 1.45)),
          const SizedBox(height: 12),
        ],
        Text(stem, style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600, height: 1.4)),
        const SizedBox(height: 16),
        ...choices.map((choice) {
          final key = JsonHelpers.str(choice['choice_key'] ?? choice['key']);
          final text = JsonHelpers.str(choice['choice_text'] ?? choice['text']);
          final isSelected = selected == key;
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: OutlinedButton(
              style: OutlinedButton.styleFrom(
                alignment: Alignment.centerLeft,
                padding: const EdgeInsets.all(16),
                backgroundColor: isSelected
                    ? Theme.of(context).colorScheme.primary.withValues(alpha: 0.12)
                    : null,
              ),
              onPressed: key.isEmpty ? null : () => _pick(key),
              child: Text(
                '$key. $text',
                style: GoogleFonts.inter(fontSize: 14, height: 1.35),
              ),
            ),
          );
        }),
        const SizedBox(height: 16),
        Row(
          children: [
            TextButton(
              onPressed: _index == 0 ? null : () => setState(() => _index -= 1),
              child: const Text('Previous'),
            ),
            const Spacer(),
            if (_index < _items.length - 1)
              FilledButton(
                onPressed: () => setState(() => _index += 1),
                child: const Text('Next'),
              )
            else
              FilledButton(
                onPressed: _submitting ? null : _submit,
                child: Text(_submitting ? 'Submitting…' : 'Submit exam'),
              ),
          ],
        ),
      ],
    );
  }
}
