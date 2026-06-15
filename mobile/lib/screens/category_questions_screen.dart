import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/routes.dart';
import '../models/category.dart';
import '../providers/quiz_provider.dart';

class CategoryQuestionsScreen extends StatelessWidget {
  const CategoryQuestionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final category = ModalRoute.of(context)?.settings.arguments as Category?;
    if (category == null) {
      return const Scaffold(
        body: Center(child: Text('Category not found')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(category.name),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 20),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(32),
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
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Icon(
                      Icons.book,
                      size: 40,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    category.name,
                    style: GoogleFonts.inter(
                      fontSize: 22,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  if (category.description != null) ...[
                    const SizedBox(height: 8),
                    Text(
                      category.description!,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        color: Colors.white70,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                  const SizedBox(height: 16),
                  Text(
                    '${category.questionCount} questions available',
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      color: Colors.white70,
                    ),
                  ),
                  if (category.completedCount > 0) ...[
                    const SizedBox(height: 8),
                    Text(
                      '${category.completedCount} completed',
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                  if (category.accuracy > 0) ...[
                    const SizedBox(height: 8),
                    Text(
                      'Accuracy: ${category.accuracy.toStringAsFixed(0)}%',
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: category.accuracy >= 60
                            ? const Color(0xFF22C55E)
                            : const Color(0xFFF59E0B),
                      ),
                    ),
                  ],
                ],
              ),
            ).animate().fadeIn(duration: 400.ms),
            const SizedBox(height: 32),
            Text(
              'Choose difficulty',
              style: GoogleFonts.inter(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ).animate().fadeIn(duration: 400.ms, delay: 100.ms),
            const SizedBox(height: 16),
            _buildDifficultyButton(
              context,
              category,
              'Easy',
              Icons.sentiment_satisfied,
              const Color(0xFF22C55E),
              5,
            ).animate().fadeIn(duration: 400.ms, delay: 200.ms),
            const SizedBox(height: 12),
            _buildDifficultyButton(
              context,
              category,
              'Medium',
              Icons.sentiment_neutral,
              const Color(0xFFF59E0B),
              10,
            ).animate().fadeIn(duration: 400.ms, delay: 300.ms),
            const SizedBox(height: 12),
            _buildDifficultyButton(
              context,
              category,
              'Hard',
              Icons.sentiment_very_dissatisfied,
              const Color(0xFFEF4444),
              10,
            ).animate().fadeIn(duration: 400.ms, delay: 400.ms),
            const SizedBox(height: 12),
            _buildDifficultyButton(
              context,
              category,
              'Random',
              Icons.shuffle,
              Theme.of(context).colorScheme.primary,
              10,
            ).animate().fadeIn(duration: 400.ms, delay: 500.ms),
          ],
        ),
      ),
    );
  }

  Widget _buildDifficultyButton(
    BuildContext context,
    Category category,
    String label,
    IconData icon,
    Color color,
    int questions,
  ) {
    return OutlinedButton(
      onPressed: () {
        Navigator.of(context).pushNamed(
          AppRoutes.quiz,
          arguments: {
            'category_id': category.id,
            'is_daily_challenge': false,
          },
        );
      },
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.all(20),
        side: BorderSide(color: color.withOpacity(0.5)),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  '$questions questions',
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    color: Theme.of(context)
                        .textTheme
                        .bodyMedium
                        ?.color
                        ?.withOpacity(0.7),
                  ),
                ),
              ],
            ),
          ),
          const Icon(Icons.arrow_forward_ios, size: 16),
        ],
      ),
    );
  }
}
