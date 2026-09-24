import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/routes.dart';
import '../models/chapter.dart';
import '../services/quiz_service.dart';

class ChapterDetailScreen extends StatefulWidget {
  const ChapterDetailScreen({super.key});

  @override
  State<ChapterDetailScreen> createState() => _ChapterDetailScreenState();
}

class _ChapterDetailScreenState extends State<ChapterDetailScreen> {
  final _service = QuizService.instance;
  Chapter? _chapter;
  bool _loading = true;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final slug = ModalRoute.of(context)?.settings.arguments as String?;
    if (slug != null && _chapter == null) _load(slug);
  }

  Future<void> _load(String slug) async {
    final chapter = await _service.fetchChapterDetail(slug);
    if (mounted) setState(() { _chapter = chapter; _loading = false; });
  }

  void _startQuiz(String chapterId) {
    Navigator.pushNamed(context, AppRoutes.quiz, arguments: {
      'chapterId': chapterId,
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    final chapter = _chapter;
    if (chapter == null) {
      return const Scaffold(body: Center(child: Text('Chapter not found')));
    }

    return Scaffold(
      appBar: AppBar(title: Text(chapter.title)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(chapter.description,
              style: GoogleFonts.inter(fontSize: 14, color: Colors.grey[700])),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => _startQuiz(chapter.id),
              icon: const Icon(Icons.quiz),
              label: const Text('Start Chapter Quiz'),
            ),
          ),
          const SizedBox(height: 24),
          Text('Topics & Lessons',
              style: GoogleFonts.inter(
                  fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          ...(chapter.topics ?? []).map((topic) => Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ExpansionTile(
                  title: Text(topic.title,
                      style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                  subtitle: Text(topic.description,
                      style: GoogleFonts.inter(fontSize: 12)),
                  children: [
                    ...(topic.lessons ?? []).map((lesson) => ListTile(
                          leading: const Icon(Icons.play_circle_outline),
                          title: Text(lesson.title),
                          subtitle: Text(lesson.summary, maxLines: 2),
                          onTap: () => Navigator.pushNamed(
                            context,
                            AppRoutes.lesson,
                            arguments: lesson.id,
                          ),
                        )),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}
