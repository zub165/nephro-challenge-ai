import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/question.dart';

class ChoiceButton extends StatelessWidget {
  final Choice choice;
  final bool isSelected;
  final bool isAnswered;
  final String? correctAnswerId;
  final VoidCallback onTap;
  final bool readOnly;

  const ChoiceButton({
    super.key,
    required this.choice,
    required this.isSelected,
    required this.isAnswered,
    this.correctAnswerId,
    required this.onTap,
    this.readOnly = false,
  });

  @override
  Widget build(BuildContext context) {
    Color? backgroundColor;
    Color? borderColor;
    Color? textColor;
    IconData? icon;

    if (isAnswered) {
      if (choice.id == correctAnswerId) {
        backgroundColor = const Color(0xFF22C55E).withOpacity(0.1);
        borderColor = const Color(0xFF22C55E);
        textColor = const Color(0xFF22C55E);
        icon = Icons.check_circle;
      } else if (isSelected && choice.id != correctAnswerId) {
        backgroundColor = const Color(0xFFEF4444).withOpacity(0.1);
        borderColor = const Color(0xFFEF4444);
        textColor = const Color(0xFFEF4444);
        icon = Icons.cancel;
      } else {
        backgroundColor = Theme.of(context).cardTheme.color;
        borderColor = Theme.of(context).dividerTheme.color!;
        textColor = Theme.of(context).textTheme.bodyLarge?.color;
      }
    } else if (isSelected) {
      backgroundColor = Theme.of(context).colorScheme.primary.withOpacity(0.1);
      borderColor = Theme.of(context).colorScheme.primary;
      textColor = Theme.of(context).colorScheme.primary;
    } else {
      backgroundColor = Theme.of(context).cardTheme.color;
      borderColor = Theme.of(context).dividerTheme.color!;
      textColor = Theme.of(context).textTheme.bodyLarge?.color;
    }

    return GestureDetector(
      onTap: (readOnly || isAnswered) ? null : onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: borderColor,
            width: isSelected || (isAnswered && (choice.id == correctAnswerId || (isSelected && choice.id != correctAnswerId))) ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                choice.text,
                style: GoogleFonts.inter(
                  fontSize: 15,
                  fontWeight:
                      isSelected || (isAnswered && choice.id == correctAnswerId)
                          ? FontWeight.w600
                          : FontWeight.w400,
                  color: textColor,
                  height: 1.4,
                ),
              ),
            ),
            if (icon != null) ...[
              const SizedBox(width: 12),
              Icon(icon, color: textColor, size: 24),
            ],
          ],
        ),
      ),
    ).animate().fadeIn(duration: 200.ms);
  }
}
