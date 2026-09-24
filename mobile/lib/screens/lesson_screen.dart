import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../config/constants.dart';
import '../models/chapter.dart';
import '../services/quiz_service.dart';

class LessonScreen extends StatefulWidget {
  const LessonScreen({super.key});

  @override
  State<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends State<LessonScreen> {
  final _service = QuizService.instance;
  Lesson? _lesson;
  bool _loading = true;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final id = ModalRoute.of(context)?.settings.arguments as String?;
    if (id != null && _lesson == null) _load(id);
  }

  Future<void> _load(String id) async {
    final lesson = await _service.fetchLesson(id);
    if (mounted) setState(() { _lesson = lesson; _loading = false; });
  }

  Future<void> _openAnimation(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final lesson = _lesson;
    if (lesson == null) {
      return const Scaffold(body: Center(child: Text('Lesson not found')));
    }

    return Scaffold(
      appBar: AppBar(title: Text(lesson.title)),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Container(
            height: 180,
            width: double.infinity,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1e3a5f), Color(0xFF0d9488)],
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Center(
              child: Icon(Icons.animation, size: 64, color: Colors.white70),
            ),
          ),
          const SizedBox(height: 20),
          Text(lesson.title,
              style: GoogleFonts.inter(
                  fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(lesson.summary, style: GoogleFonts.inter(fontSize: 15)),
          const SizedBox(height: 24),
          if (lesson.animationUrl.isNotEmpty)
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _openAnimation(lesson.animationUrl),
                icon: const Icon(Icons.open_in_new),
                label: const Text('Open Animation'),
              ),
            ),
          const SizedBox(height: 12),
          Text(
            AppConstants.disclaimerText,
            style: GoogleFonts.inter(fontSize: 12, color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }
}
