import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../models/lesson_animation.dart';

const _teal = Color(0xFF2dd4bf);
const _amber = Color(0xFFfbbf24);
const _red = Color(0xFFf87171);
const _blue = Color(0xFF93c5fd);
const _emerald = Color(0xFF6ee7b7);

class AnimationStepVisual extends StatelessWidget {
  final AnimationStep step;

  const AnimationStepVisual({super.key, required this.step});

  @override
  Widget build(BuildContext context) {
    if (step.visual.isEmpty) return const SizedBox.shrink();

    switch (step.visual) {
      case 'pressures':
        return _buildPressures();
      case 'dose-summary':
        return _buildDoseSummary();
      case 'monitoring':
        return _buildMonitoring();
      case 'circuit-cvvh':
      case 'circuit-cvvhd':
      case 'circuit-scuf':
        return _buildCircuit(step.visual);
      default:
        return _buildMetrics();
    }
  }

  int? _num(String key) {
    final raw = step.metrics[key];
    if (raw == null) return null;
    return int.tryParse(raw.replaceAll(RegExp(r'[^0-9\-]'), ''));
  }

  Widget _buildPressures() {
    final access = _num('access');
    final ret = _num('return');
    final tmp = _num('tmp');

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 8,
      crossAxisSpacing: 8,
      childAspectRatio: 1.9,
      children: [
        _gauge('Access', step.metrics['access'], access != null && access < -150),
        _gauge('Pre-filter', step.metrics['prefilter'], false),
        _gauge('Return', step.metrics['return'], ret != null && ret > 250),
        _gauge('TMP', step.metrics['tmp'], tmp != null && tmp > 200),
      ],
    );
  }

  Widget _gauge(String label, String? value, bool warn) {
    final num = int.tryParse((value ?? '').replaceAll(RegExp(r'[^0-9\-]'), ''));
    final pct = num == null
        ? 0.08
        : (num.abs() / 300).clamp(0.08, 1.0);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: warn ? const Color(0x33ef4444) : const Color(0x14ffffff),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: warn ? const Color(0x66f87171) : const Color(0x1fffffff),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            label.toUpperCase(),
            style: GoogleFonts.inter(
              fontSize: 9,
              letterSpacing: 0.6,
              color: _teal.withValues(alpha: 0.85),
            ),
          ),
          const SizedBox(height: 2),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                (value == null || value.isEmpty) ? '—' : value,
                style: GoogleFonts.inter(
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                  color: warn ? _red : Colors.white,
                ),
              ),
              const SizedBox(width: 3),
              Text(
                'mmHg',
                style: GoogleFonts.inter(fontSize: 10, color: _teal.withValues(alpha: 0.7)),
              ),
            ],
          ),
          const SizedBox(height: 5),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: LinearProgressIndicator(
              value: pct,
              minHeight: 4,
              backgroundColor: const Color(0x1fffffff),
              valueColor: AlwaysStoppedAnimation<Color>(warn ? _red : _teal),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDoseSummary() {
    final items = <(String, String, Color)>[
      ('Effluent', '${step.metrics['effluent'] ?? '—'} mL/hr', _teal),
      ('Dose', '${step.metrics['dose'] ?? '—'} mL/kg/hr', _amber),
      ('Total input', '${step.metrics['input'] ?? '—'} mL/hr', _blue),
      ('Net balance', '${step.metrics['balance'] ?? '—'} mL/hr', _emerald),
    ];

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 8,
      crossAxisSpacing: 8,
      childAspectRatio: 2.4,
      children: [
        for (final (label, value, color) in items)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0x14ffffff),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0x1fffffff)),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  label.toUpperCase(),
                  style: GoogleFonts.inter(
                    fontSize: 9,
                    letterSpacing: 0.6,
                    color: _teal.withValues(alpha: 0.75),
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  textAlign: TextAlign.center,
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    color: color,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  static const _monitoringItems = [
    'q4h: Ionized Ca2+ (if citrate)',
    'q6h: K+, Na+, HCO3-, BUN, Cr',
    'q2h: Filter pressures',
    'Daily: Mg2+, PO4 3-, weight',
  ];

  Widget _buildMonitoring() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0x14ffffff),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0x1fffffff)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final item in _monitoringItems)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 3),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('●', style: TextStyle(color: _teal, fontSize: 9)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      item,
                      style: GoogleFonts.inter(
                        fontSize: 12,
                        color: const Color(0xFFCCFBF1).withValues(alpha: 0.9),
                      ),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildCircuit(String mode) {
    final showDialysate = mode == 'circuit-cvvhd';
    final showReplacement = mode != 'circuit-scuf';

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: const Color(0x0dffffff),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0x1fffffff)),
      ),
      child: Column(
        children: [
          SizedBox(
            height: 92,
            width: double.infinity,
            child: CustomPaint(
              painter: _CircuitPainter(
                showDialysate: showDialysate,
                showReplacement: showReplacement,
              ),
            ),
          ),
          const SizedBox(height: 6),
          const Wrap(
            spacing: 12,
            runSpacing: 4,
            alignment: WrapAlignment.center,
            children: [
              _LegendDot(color: Color(0xFFef4444), label: 'Blood'),
              _LegendDot(color: Color(0xFF2dd4bf), label: 'Dialysate'),
              _LegendDot(color: Color(0xFF60a5fa), label: 'Replacement'),
            ],
          ),
        ],
      ),
    );
  }

  /// Fallback for any newer visual type: render the metrics generically so
  /// new content still shows its numbers instead of rendering nothing.
  Widget _buildMetrics() {
    if (!step.hasMetrics) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0x0dffffff),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0x1fffffff)),
      ),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: [
          for (final entry in step.metrics.entries)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: const Color(0x14ffffff),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0x1fffffff)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    entry.key.replaceAll('_', ' ').toUpperCase(),
                    style: GoogleFonts.inter(
                      fontSize: 9,
                      letterSpacing: 0.6,
                      color: _teal.withValues(alpha: 0.75),
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    entry.value,
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class _LegendDot extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendDot({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 5),
        Text(
          label,
          style: GoogleFonts.inter(fontSize: 10, color: Colors.white.withValues(alpha: 0.7)),
        ),
      ],
    );
  }
}

class _CircuitPainter extends CustomPainter {
  final bool showDialysate;
  final bool showReplacement;

  _CircuitPainter({required this.showDialysate, required this.showReplacement});

  @override
  void paint(Canvas canvas, Size size) {
    final centerY = size.height / 2;
    final filterWidth = size.width * 0.22;
    final filterLeft = (size.width - filterWidth) / 2;
    final filterRect = Rect.fromLTWH(
      filterLeft,
      centerY - 24,
      filterWidth,
      48,
    );

    final blood = Paint()
      ..color = const Color(0xFFef4444)
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    final fluid = Paint()
      ..color = const Color(0xFF2dd4bf)
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;
    final replace = Paint()
      ..color = const Color(0xFF60a5fa)
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(Offset(8, centerY), Offset(filterLeft, centerY), blood);
    canvas.drawLine(
      Offset(filterRect.right, centerY),
      Offset(size.width - 8, centerY),
      blood,
    );

    canvas.drawRRect(
      RRect.fromRectAndRadius(filterRect, const Radius.circular(6)),
      Paint()..color = const Color(0xFF1e3a5f),
    );
    canvas.drawRRect(
      RRect.fromRectAndRadius(filterRect, const Radius.circular(6)),
      Paint()
        ..color = _teal
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2,
    );

    if (showReplacement) {
      final y = centerY - 40;
      canvas.drawLine(Offset(filterLeft + 10, y), Offset(8, y), replace);
      canvas.drawArc(
        Rect.fromCircle(center: Offset(filterLeft + 10, y), radius: 22),
        -3.14,
        3.14,
        false,
        replace,
      );
    }
    if (showDialysate) {
      final y = centerY + 40;
      canvas.drawLine(Offset(filterLeft + 10, y), Offset(8, y), fluid);
      canvas.drawArc(
        Rect.fromCircle(center: Offset(filterLeft + 10, y), radius: 22),
        0,
        3.14,
        false,
        fluid,
      );
    }

    final textPainter = TextPainter(
      text: const TextSpan(
        text: 'Filter',
        style: TextStyle(color: Color(0xFF99f6e4), fontSize: 10),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    textPainter.paint(
      canvas,
      Offset(
        filterRect.center.dx - textPainter.width / 2,
        filterRect.center.dy - textPainter.height / 2,
      ),
    );
  }

  @override
  bool shouldRepaint(_CircuitPainter oldDelegate) {
    return oldDelegate.showDialysate != showDialysate ||
        oldDelegate.showReplacement != showReplacement;
  }
}
