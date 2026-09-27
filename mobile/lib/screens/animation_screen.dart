import 'dart:async';

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../config/constants.dart';
import '../models/lesson_animation.dart';
import '../services/animation_service.dart';
import '../widgets/animation_step_visual.dart';

const _teal50 = Color(0xFFF0FDFA);
const _teal100 = Color(0xFFCCFBF1);
const _teal200 = Color(0xFF99F6E4);
const _teal300 = Color(0xFF5EEAD4);
const _amber50 = Color(0xFFFFFBEB);
const _amber300 = Color(0xFFFCD34D);

class AnimationScreen extends StatefulWidget {
  final String animationUrl;
  final String fallbackTitle;
  final String fallbackSummary;

  /// Overrides the network load. Used by tests to render the player without
  /// hitting the animation host.
  final Future<LessonAnimation> Function(String url)? loader;

  const AnimationScreen({
    super.key,
    required this.animationUrl,
    required this.fallbackTitle,
    this.fallbackSummary = '',
    this.loader,
  });

  @override
  State<AnimationScreen> createState() => _AnimationScreenState();
}

class _AnimationScreenState extends State<AnimationScreen> {
  static const Duration _stepInterval = Duration(milliseconds: 4500);

  final _service = AnimationService.instance;

  LessonAnimation? _animation;
  bool _loading = true;
  String? _error;
  int _stepIndex = 0;
  bool _playing = false;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
      _animation = null;
      _stepIndex = 0;
      _playing = false;
    });

    try {
      final load = widget.loader ?? _service.load;
      final animation = await load(widget.animationUrl);
      if (!mounted) return;
      setState(() {
        _animation = animation;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  void _togglePlaying() {
    if (_playing) {
      _timer?.cancel();
      setState(() => _playing = false);
      return;
    }
    final steps = _animation?.steps.length ?? 0;
    if (steps == 0) return;
    if (_stepIndex >= steps - 1) {
      setState(() => _stepIndex = 0);
    }
    setState(() => _playing = true);
    _startTimer();
  }

  void _startTimer() {
    _timer?.cancel();
    _timer = Timer.periodic(_stepInterval, (_) {
      final steps = _animation?.steps ?? const <AnimationStep>[];
      if (steps.isEmpty) return;
      if (!mounted) return;
      if (_stepIndex >= steps.length - 1) {
        _timer?.cancel();
        setState(() => _playing = false);
        return;
      }
      setState(() => _stepIndex = _stepIndex + 1);
    });
  }

  void _goTo(int index) {
    final steps = _animation?.steps ?? const <AnimationStep>[];
    if (steps.isEmpty) return;
    final clamped = index.clamp(0, steps.length - 1);
    setState(() => _stepIndex = clamped);
    if (_playing) _startTimer();
  }

  List<Color> get _gradient {
    if (_animation?.isCrrt ?? false) {
      return const [Color(0xFF0f172a), Color(0xFF172554), Color(0xFF134e4a)];
    }
    return const [Color(0xFF1e3a5f), Color(0xFF134e4a), Color(0xFF111827)];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: _gradient,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: _loading
              ? const Center(
                  child: Text(
                    'Loading animation...',
                    style: TextStyle(color: _teal100),
                  ),
                )
              : _error != null
                  ? _buildError()
                  : _buildPlayer(),
        ),
      ),
    );
  }

  Widget _buildError() {
    return Padding(
      padding: const EdgeInsets.all(28),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.animation_outlined, size: 56, color: Colors.white38),
          const SizedBox(height: 16),
          Text(
            widget.fallbackTitle,
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
          if (widget.fallbackSummary.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              widget.fallbackSummary,
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                fontSize: 14,
                color: _teal100.withValues(alpha: 0.8),
              ),
            ),
          ],
          const SizedBox(height: 12),
          Text(
            'Animation file unavailable',
            style: GoogleFonts.inter(
              fontSize: 12,
              color: _amber300.withValues(alpha: 0.9),
            ),
          ),
          const SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              TextButton.icon(
                onPressed: _load,
                icon: const Icon(Icons.refresh, color: Colors.white),
                label: const Text('Retry', style: TextStyle(color: Colors.white)),
              ),
              TextButton.icon(
                onPressed: () => Navigator.of(context).maybePop(),
                icon: const Icon(Icons.arrow_back, color: Colors.white70),
                label: const Text(
                  'Back to lesson',
                  style: TextStyle(color: Colors.white70),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPlayer() {
    final animation = _animation!;
    final steps = animation.steps;
    if (steps.isEmpty) return _buildError();

    final step = steps[_stepIndex];
    final progress = ((_stepIndex + 1) / steps.length) * 100;

    return Column(
      children: [
        _buildHeader(animation),
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(20, 20, 20, 8),
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 350),
              child: Column(
                key: ValueKey(_stepIndex),
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Container(
                        width: 36,
                        height: 36,
                        alignment: Alignment.center,
                        decoration: const BoxDecoration(
                          color: Color(0xFF14b8a6),
                          shape: BoxShape.circle,
                        ),
                        child: Text(
                          '${_stepIndex + 1}',
                          style: GoogleFonts.inter(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          step.title,
                          style: GoogleFonts.inter(
                            fontSize: 19,
                            fontWeight: FontWeight.w600,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Text(
                    step.body,
                    style: GoogleFonts.inter(
                      fontSize: 15,
                      height: 1.5,
                      color: _teal50.withValues(alpha: 0.95),
                    ),
                  ),
                  if (step.visual.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0x33000000),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0x1fffffff)),
                      ),
                      child: AnimationStepVisual(step: step),
                    ),
                  ],
                  if (step.tip.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                      decoration: BoxDecoration(
                        color: const Color(0x1af59e0b),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0x4dfbbf24)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'PEARL',
                            style: GoogleFonts.inter(
                              fontSize: 10,
                              fontWeight: FontWeight.w600,
                              letterSpacing: 0.8,
                              color: _amber300,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            step.tip,
                            style: GoogleFonts.inter(
                              fontSize: 13,
                              color: _amber50.withValues(alpha: 0.9),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                  const SizedBox(height: 12),
                  Text(
                    AppConstants.disclaimerText,
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      color: Colors.white.withValues(alpha: 0.35),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        _buildControls(steps.length, progress),
      ],
    );
  }

  Widget _buildHeader(LessonAnimation animation) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(20, 14, 8, 14),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Color(0x1fffffff))),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'ANIMATED ALGORITHM',
                  style: GoogleFonts.inter(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 1.4,
                    color: _teal300,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  animation.title.isNotEmpty ? animation.title : widget.fallbackTitle,
                  style: GoogleFonts.inter(
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                ),
                if (animation.subtitle.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 2),
                    child: Text(
                      animation.subtitle,
                      style: GoogleFonts.inter(
                        fontSize: 12,
                        color: _teal100.withValues(alpha: 0.7),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          IconButton(
            onPressed: () => Navigator.of(context).maybePop(),
            icon: const Icon(Icons.close, color: Colors.white70),
            tooltip: 'Close',
          ),
        ],
      ),
    );
  }

  Widget _buildControls(int stepCount, double progress) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(20, 14, 20, 18),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Color(0x1fffffff))),
      ),
      child: Column(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: LinearProgressIndicator(
              value: progress / 100,
              minHeight: 6,
              backgroundColor: const Color(0x1fffffff),
              valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF2dd4bf)),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Text(
                'Step ${_stepIndex + 1} of $stepCount',
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: _teal200.withValues(alpha: 0.7),
                ),
              ),
              const Spacer(),
              _controlButton(Icons.replay, () => _goTo(0), 'Restart'),
              _controlButton(Icons.chevron_left, () => _goTo(_stepIndex - 1), 'Previous step',
                  enabled: _stepIndex > 0),
              const SizedBox(width: 4),
              IconButton.filled(
                onPressed: _togglePlaying,
                icon: Icon(_playing ? Icons.pause : Icons.play_arrow),
                style: IconButton.styleFrom(backgroundColor: const Color(0xFF0d9488)),
                tooltip: _playing ? 'Pause' : 'Play',
              ),
              _controlButton(Icons.chevron_right, () => _goTo(_stepIndex + 1), 'Next step',
                  enabled: _stepIndex < stepCount - 1),
            ],
          ),
        ],
      ),
    );
  }

  Widget _controlButton(IconData icon, VoidCallback onPressed, String tooltip,
      {bool enabled = true}) {
    return IconButton(
      onPressed: enabled ? onPressed : null,
      icon: Icon(icon, size: 22),
      color: _teal200,
      disabledColor: _teal200.withValues(alpha: 0.35),
      tooltip: tooltip,
    );
  }
}
