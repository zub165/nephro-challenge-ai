import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../config/constants.dart';
import '../models/chapter.dart';
import '../screens/animation_screen.dart';
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
    if (url.isEmpty) return;
    final lesson = _lesson;
    if (lesson == null) return;
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => AnimationScreen(
          animationUrl: url,
          fallbackTitle: lesson.title,
          fallbackSummary: lesson.summary,
        ),
      ),
    );
  }

  Future<void> _openInteractive(String url) async {
    if (url.isEmpty) return;
    final uri = Uri.tryParse(url);
    if (uri == null) return;
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not open the interactive lesson')),
      );
    }
  }

  Widget _buildImage(String url) {
    if (url.toLowerCase().endsWith('.svg')) {
      return SvgPicture.network(url, fit: BoxFit.contain);
    }
    return CachedNetworkImage(
      imageUrl: url,
      fit: BoxFit.contain,
      placeholder: (_, __) => const Center(child: CircularProgressIndicator()),
      errorWidget: (_, __, ___) => const Center(
        child: Icon(Icons.broken_image_outlined, size: 48, color: Colors.grey),
      ),
    );
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
          if (lesson.imageUrl.isNotEmpty) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.grey.shade300),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: AspectRatio(
                  aspectRatio: 3 / 4,
                  child: _buildImage(lesson.imageUrl),
                ),
              ),
            ),
          ],
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
                icon: const Icon(Icons.play_circle_outline),
                label: const Text('Open Animation'),
              ),
            ),
          if (lesson.interactiveUrl.isNotEmpty) ...[
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () => _openInteractive(lesson.interactiveUrl),
                icon: const Icon(Icons.touch_app_outlined),
                label: const Text('Open Interactive Lesson'),
              ),
            ),
          ],
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
