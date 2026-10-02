import 'package:cached_network_image/cached_network_image.dart';
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
  Map<String, dynamic>? _knowledge;
  bool _loading = true;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final slug = ModalRoute.of(context)?.settings.arguments as String?;
    if (slug != null && _chapter == null) _load(slug);
  }

  Future<void> _load(String slug) async {
    final chapter = await _service.fetchChapterDetail(slug);
    final knowledge = await _service.fetchChapterKnowledge(slug);
    if (mounted) {
      setState(() {
        _chapter = chapter;
        _knowledge = knowledge;
        _loading = false;
      });
    }
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
          if ((_knowledge?['high_yield'] as List?)?.isNotEmpty == true) ...[
            const SizedBox(height: 20),
            Text('Exam knowledge — high yield',
                style: GoogleFonts.inter(
                    fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ...((_knowledge!['high_yield'] as List).map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text('• $item',
                      style: GoogleFonts.inter(fontSize: 14, height: 1.35)),
                ))),
          ],
          if ((_knowledge?['pearls'] as List?)?.isNotEmpty == true) ...[
            const SizedBox(height: 16),
            Text('Board pearls',
                style: GoogleFonts.inter(
                    fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ...((_knowledge!['pearls'] as List).take(8).map((raw) {
              final pearl = raw as Map<String, dynamic>;
              return Container(
                width: double.infinity,
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.amber.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${pearl['topic'] ?? ''}',
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: Colors.amber[900],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${pearl['pearl'] ?? ''}',
                      style: GoogleFonts.inter(fontSize: 14, height: 1.35),
                    ),
                  ],
                ),
              );
            })),
          ],
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
                          leading: lesson.thumbnailUrl.isEmpty
                              ? const Icon(Icons.play_circle_outline)
                              : ClipRRect(
                                  borderRadius: BorderRadius.circular(8),
                                  child: CachedNetworkImage(
                                    imageUrl: lesson.thumbnailUrl,
                                    width: 44,
                                    height: 44,
                                    fit: BoxFit.cover,
                                    errorWidget: (_, __, ___) => const Icon(
                                        Icons.play_circle_outline, size: 44),
                                  ),
                                ),
                          title: Text(lesson.title),
                          subtitle: Text(lesson.summary, maxLines: 2),
                          trailing: lesson.interactiveUrl.isEmpty
                              ? null
                              : const Icon(Icons.touch_app_outlined, size: 20),
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
