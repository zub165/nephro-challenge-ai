import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/ai_service.dart';
import '../widgets/disclaimer_banner.dart';

const _accent = Color(0xFF6366F1);
const _teal = Color(0xFF0D9488);

class BoardPrepScreen extends StatefulWidget {
  const BoardPrepScreen({super.key});

  @override
  State<BoardPrepScreen> createState() => _BoardPrepScreenState();
}

class _BoardPrepScreenState extends State<BoardPrepScreen> {
  static const List<String> _topicSuggestions = [
    'Acute Kidney Injury',
    'Chronic Kidney Disease',
    'Glomerular diseases',
    'Acid-base disorders',
    'Electrolyte disorders',
    'Kidney stones',
    'Dialysis',
    'Transplantation',
  ];

  final _aiService = AIService.instance;
  final _topicController = TextEditingController();

  String _difficulty = 'medium';
  int _count = 3;
  bool _isLoading = false;
  List<Map<String, dynamic>> _questions = [];
  int _currentIndex = 0;
  int? _selectedIndex;
  int _score = 0;
  String _generatedTopic = '';

  @override
  void dispose() {
    _topicController.dispose();
    super.dispose();
  }

  Future<void> _generate() async {
    final topic = _topicController.text.trim();
    if (topic.isEmpty || _isLoading) return;
    FocusScope.of(context).unfocus();

    setState(() {
      _isLoading = true;
      _questions = [];
      _currentIndex = 0;
      _selectedIndex = null;
      _score = 0;
    });

    final result = await _aiService.generateBoardPrep(
      topic: topic,
      count: _count,
      difficulty: _difficulty,
    );

    if (!mounted) return;
    final questions = (result['questions'] as List<dynamic>? ?? [])
        .map((q) => q as Map<String, dynamic>)
        .toList();

    setState(() {
      _isLoading = false;
      _questions = questions;
      _generatedTopic =
          questions.isEmpty ? '' : (result['topic'] as String? ?? topic);
    });
  }

  void _selectChoice(int index) {
    if (_selectedIndex != null) return;
    setState(() {
      _selectedIndex = index;
      final q = _questions[_currentIndex];
      if (q['choices'][index] == q['correct_answer']) {
        _score++;
      }
    });
  }

  double get _progress => _questions.isEmpty
      ? 0
      : (_currentIndex + 1) / _questions.length;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: _accent.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.workspace_premium, size: 18, color: _accent),
            ),
            const SizedBox(width: 8),
            const Text('Board Prep'),
          ],
        ),
      ),
      body: Column(
        children: [
          const DisclaimerBanner(),
          Expanded(child: _buildBody()),
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (_isLoading) return _buildLoading();
    if (_questions.isNotEmpty) return _buildPractice();
    return _buildSetup();
  }

  Widget _buildLoading() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const SizedBox(
            height: 48,
            width: 48,
            child: CircularProgressIndicator(strokeWidth: 3),
          ),
          const SizedBox(height: 24),
          Text(
            'Generating $_count board questions…',
            style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 10),
          Text(
            'The on-device AI is drafting clinically accurate vignettes.\n'
            'Each question takes ~20-40 seconds.',
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(
              fontSize: 13,
              color: Theme.of(context)
                  .textTheme
                  .bodyMedium
                  ?.color
                  ?.withValues(alpha: 0.7),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms);
  }

  Widget _buildSetup() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: _accent.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: _accent.withValues(alpha: 0.3)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.workspace_premium, color: _accent),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'New practice questions written live by the built-in AI — '
                  'topics tuned to the nephrology board exam.',
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    height: 1.4,
                    color: Theme.of(context)
                        .textTheme
                        .bodyMedium
                        ?.color
                        ?.withValues(alpha: 0.85),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        Text('Topic', style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600)),
        const SizedBox(height: 10),
        TextField(
          controller: _topicController,
          textInputAction: TextInputAction.done,
          decoration: InputDecoration(
            hintText: 'e.g. Diabetic nephropathy',
            prefixIcon: const Icon(Icons.topic, color: _accent),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
            filled: true,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _topicSuggestions
              .map((s) => ActionChip(
                    label: Text(s),
                    onPressed: () {
                      _topicController.text = s;
                      setState(() {});
                    },
                  ))
              .toList(),
        ),
        const SizedBox(height: 24),
        Text('Difficulty', style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600)),
        const SizedBox(height: 10),
        _segmented(
          options: const {'easy': 'Easy', 'medium': 'Medium', 'hard': 'Hard'},
          selected: _difficulty,
          onChanged: (v) => setState(() => _difficulty = v),
        ),
        const SizedBox(height: 24),
        Text('Questions', style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600)),
        const SizedBox(height: 10),
        _segmented(
          options: const {'1': '1', '3': '3', '5': '5'},
          selected: _count.toString(),
          onChanged: (v) => setState(() => _count = int.parse(v)),
        ),
        const SizedBox(height: 28),
        SizedBox(
          height: 52,
          child: FilledButton.icon(
            onPressed: _generate,
            style: FilledButton.styleFrom(
              backgroundColor: _accent,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            ),
            icon: const Icon(Icons.auto_awesome),
            label: Text(
              'Generate Questions',
              style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ),
        ),
      ],
    );
  }

  Widget _segmented({
    required Map<String, String> options,
    required String selected,
    required ValueChanged<String> onChanged,
  }) {
    return Wrap(
      spacing: 8,
      children: options.entries.map((e) {
        final isSelected = selected == e.key;
        return ChoiceChip(
          label: Text(e.value),
          selected: isSelected,
          onSelected: (_) => onChanged(e.key),
          selectedColor: _accent.withValues(alpha: 0.2),
          labelStyle: GoogleFonts.inter(
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
          ),
        );
      }).toList(),
    );
  }

  Widget _buildPractice() {
    final q = _questions[_currentIndex];
    final choices = (q['choices'] as List<dynamic>).cast<String>();
    final correct = q['correct_answer'] as String? ?? '';
    final explanation = q['explanation'] as String? ?? '';
    final answered = _selectedIndex != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _generatedTopic,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: _accent,
                    ),
                  ),
                  Text(
                    '$_currentIndex/${_questions.length - 1} · Score $_score',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      color: Theme.of(context)
                          .textTheme
                          .bodyMedium
                          ?.color
                          ?.withValues(alpha: 0.7),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: _progress,
                  minHeight: 4,
                  backgroundColor: _accent.withValues(alpha: 0.15),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text(
                q['question_text'] as String? ?? '',
                style: GoogleFonts.inter(fontSize: 16, height: 1.45, fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 18),
              for (var i = 0; i < choices.length; i++) ...[
                _buildChoice(i, choices[i], answered, correct),
                const SizedBox(height: 10),
              ],
              if (answered) ...[
                const SizedBox(height: 6),
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: (_selectedIndex == q['choices'].indexOf(correct))
                        ? _teal.withValues(alpha: 0.12)
                        : const Color(0xFFE11D48).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: (_selectedIndex == q['choices'].indexOf(correct))
                          ? _teal.withValues(alpha: 0.4)
                          : const Color(0xFFE11D48).withValues(alpha: 0.3),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            _selectedIndex == q['choices'].indexOf(correct)
                                ? Icons.check_circle
                                : Icons.cancel,
                            size: 18,
                            color: _selectedIndex == q['choices'].indexOf(correct)
                                ? _teal
                                : const Color(0xFFE11D48),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            _selectedIndex == q['choices'].indexOf(correct)
                                ? 'Correct'
                                : 'Incorrect',
                            style: GoogleFonts.inter(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: _selectedIndex == q['choices'].indexOf(correct)
                                  ? _teal
                                  : const Color(0xFFE11D48),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      if (_selectedIndex != q['choices'].indexOf(correct)) ...[
                        Text(
                          'Correct answer: $correct',
                          style: GoogleFonts.inter(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: _teal,
                          ),
                        ),
                        const SizedBox(height: 6),
                      ],
                      if (explanation.isNotEmpty)
                        Text(
                          explanation,
                          style: GoogleFonts.inter(fontSize: 13, height: 1.45),
                        ),
                    ],
                  ),
                ).animate().fadeIn(duration: 250.ms),
              ],
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              if (_currentIndex > 0)
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      setState(() {
                        _currentIndex--;
                        _selectedIndex = null;
                      });
                    },
                    child: const Text('Previous'),
                  ),
                ),
              if (_currentIndex > 0) const SizedBox(width: 12),
              Expanded(
                flex: 2,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: _accent,
                    minimumSize: const Size.fromHeight(48),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: answered
                      ? () {
                          if (_currentIndex < _questions.length - 1) {
                            setState(() {
                              _currentIndex++;
                              _selectedIndex = null;
                            });
                          } else {
                            _showSummary(context);
                          }
                        }
                      : null,
                  child: Text(
                    _currentIndex < _questions.length - 1 ? 'Next' : 'Finish',
                    style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildChoice(int index, String choice, bool answered, String correct) {
    final isCorrect = choice == correct;
    final isSelected = index == _selectedIndex;
    Color bg = _accent.withValues(alpha: 0.04);
    Color border = _accent.withValues(alpha: 0.3);
    Color textColor = Theme.of(context).textTheme.bodyLarge?.color ?? Colors.black87;
    IconData? trailing;
    Color? trailingColor;

    if (answered) {
      if (isCorrect) {
        bg = _teal.withValues(alpha: 0.12);
        border = _teal.withValues(alpha: 0.5);
        textColor = _teal;
        trailing = Icons.check_circle;
        trailingColor = _teal;
      } else if (isSelected) {
        bg = const Color(0xFFE11D48).withValues(alpha: 0.1);
        border = const Color(0xFFE11D48).withValues(alpha: 0.4);
        textColor = const Color(0xFFE11D48);
        trailing = Icons.cancel;
        trailingColor = const Color(0xFFE11D48);
      }
    }

    return Material(
      color: bg,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: answered ? null : () => _selectChoice(index),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: border),
          ),
          child: Row(
            children: [
              Container(
                width: 26,
                height: 26,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: answered ? border : _accent.withValues(alpha: 0.6),
                  ),
                  color: isSelected && !answered
                      ? _accent.withValues(alpha: 0.2)
                      : Colors.transparent,
                ),
                child: Text(
                  String.fromCharCode(65 + index),
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    color: textColor,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  choice,
                  style: GoogleFonts.inter(fontSize: 15, height: 1.3, color: textColor),
                ),
              ),
              if (trailing != null) Icon(trailing, color: trailingColor, size: 20),
            ],
          ),
        ),
      ),
    );
  }

  void _showSummary(BuildContext context) {
    final total = _questions.length;
    final percent = total == 0 ? 0 : (_score / total * 100).round();
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Session complete',
            style: GoogleFonts.inter(fontWeight: FontWeight.w700)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '$_score / $total',
              style: GoogleFonts.inter(
                fontSize: 40,
                fontWeight: FontWeight.w800,
                color: _accent,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              '$percent% correct',
              style: GoogleFonts.inter(fontSize: 15),
            ),
            const SizedBox(height: 10),
            Text(
              percent >= 70
                  ? 'Excellent — you are exam ready on this topic.'
                  : 'Review the explanations above and try again to lock it in.',
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(fontSize: 13, height: 1.4),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              setState(() {
                _questions = [];
                _selectedIndex = null;
                _currentIndex = 0;
                _score = 0;
              });
            },
            child: const Text('New session'),
          ),
          FilledButton(
            onPressed: () async {
              Navigator.of(ctx).pop();
              setState(() => _isLoading = true);
              final result = await _aiService.generateBoardPrep(
                topic: _generatedTopic,
                count: _count,
                difficulty: _difficulty,
              );
              if (!mounted) return;
              setState(() {
                _isLoading = false;
                _questions = (result['questions'] as List<dynamic>? ?? [])
                    .map((q) => q as Map<String, dynamic>)
                    .toList();
                _selectedIndex = null;
                _currentIndex = 0;
                _score = 0;
              });
            },
            style: FilledButton.styleFrom(backgroundColor: _accent),
            child: const Text('Try again'),
          ),
        ],
      ),
    );
  }
}