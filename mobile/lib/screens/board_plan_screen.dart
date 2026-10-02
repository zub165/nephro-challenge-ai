import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/routes.dart';
import '../services/board_prep_service.dart';
import 'board_prep_screen.dart';

class BoardPlanScreen extends StatefulWidget {
  const BoardPlanScreen({super.key});

  @override
  State<BoardPlanScreen> createState() => _BoardPlanScreenState();
}

class _BoardPlanScreenState extends State<BoardPlanScreen>
    with SingleTickerProviderStateMixin {
  final _service = BoardPrepService.instance;
  late final TabController _tabs;
  Map<String, dynamic> _plan = {};
  Map<String, dynamic> _review = {};
  Map<String, dynamic> _sheet = {};
  bool _loading = true;
  String _reviewTag = 'review';
  final _factController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 4, vsync: this);
    _load();
  }

  @override
  void dispose() {
    _tabs.dispose();
    _factController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final plan = await _service.fetchPlan();
    final review = await _service.fetchReview(tag: _reviewTag);
    final sheet = await _service.fetchLast48();
    if (!mounted) return;
    setState(() {
      _plan = plan;
      _review = review;
      _sheet = sheet;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('25-Day Board Plan'),
        bottom: TabBar(
          controller: _tabs,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Today'),
            Tab(text: 'Calendar'),
            Tab(text: 'Review'),
            Tab(text: 'Last 48h'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.auto_awesome),
            tooltip: 'AI questions',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const BoardPrepScreen()),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          if (_loading) const LinearProgressIndicator(minHeight: 3),
          Expanded(
            child: TabBarView(
              controller: _tabs,
              children: [
                _todayTab(),
                _calendarTab(),
                _reviewTab(),
                _sheetTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _todayTab() {
    final session = Map<String, dynamic>.from(_plan['today_session'] as Map? ?? {});
    final day = session['day'] ?? 1;
    final focus = session['focus']?.toString() ?? 'Board review';
    final highYield = List.from(session['high_yield'] ?? []);
    final target = session['question_target'] ?? 25;
    final answered = _plan['today_answered'] ?? 0;
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            'Day $day of 25 · $focus',
            style: GoogleFonts.inter(fontSize: 20, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
            '${_plan['days_until_exam'] ?? '—'} days until exam · '
            '$answered / $target questions today',
            style: GoogleFonts.inter(fontSize: 13, color: Colors.grey[600]),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: highYield
                .map((item) => Chip(label: Text(item.toString())))
                .toList(),
          ),
          const SizedBox(height: 16),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pushNamed(
                AppRoutes.quiz,
                arguments: {
                  'boardDay': day is int ? day : int.tryParse('$day') ?? 1,
                  'limit': session['morning_questions'] ?? 18,
                },
              );
            },
            child: const Text('Start morning questions'),
          ),
          const SizedBox(height: 8),
          OutlinedButton.icon(
            onPressed: () {
              Navigator.of(context).pushNamed(AppRoutes.boardExams);
            },
            icon: const Icon(Icons.timer_outlined),
            label: const Text('Timed board simulation'),
          ),
          const SizedBox(height: 8),
          Text(
            _plan['method']?.toString() ?? '',
            style: GoogleFonts.inter(fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  Widget _calendarTab() {
    final days = List.from(_plan['days'] ?? []);
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: days.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final day = Map<String, dynamic>.from(days[index] as Map);
        return Card(
          child: ListTile(
            title: Text('Day ${day['day']}: ${day['focus']}'),
            subtitle: Text(List.from(day['high_yield'] ?? []).join(' · ')),
            onTap: () {
              Navigator.of(context).pushNamed(
                AppRoutes.quiz,
                arguments: {
                  'boardDay': day['day'],
                  'limit': day['morning_questions'] ?? 18,
                },
              );
            },
          ),
        );
      },
    );
  }

  Widget _reviewTab() {
    final items = List.from(_review['items'] ?? []);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(8),
          child: Wrap(
            spacing: 8,
            children: ['review', 'wrong', 'guessed'].map((tag) {
              return ChoiceChip(
                label: Text(tag),
                selected: _reviewTag == tag,
                onSelected: (_) async {
                  setState(() => _reviewTag = tag);
                  final review = await _service.fetchReview(tag: tag);
                  if (mounted) setState(() => _review = review);
                },
              );
            }).toList(),
          ),
        ),
        Expanded(
          child: items.isEmpty
              ? const Center(child: Text('No review items yet'))
              : ListView.builder(
                  itemCount: items.length,
                  itemBuilder: (context, index) {
                    final item = Map<String, dynamic>.from(items[index] as Map);
                    return Card(
                      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                      child: ListTile(
                        title: Text(item['question_text']?.toString() ?? ''),
                        subtitle: Text(
                          '${item['tag']} · ${item['clinical_pearl'] ?? item['explanation'] ?? ''}',
                          maxLines: 4,
                        ),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }

  Widget _sheetTab() {
    final items = List.from(_sheet['items'] ?? []);
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _factController,
                  decoration: const InputDecoration(
                    hintText: 'Formula, biopsy, toxicity…',
                    border: OutlineInputBorder(),
                  ),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.add),
                onPressed: () async {
                  final text = _factController.text.trim();
                  if (text.isEmpty) return;
                  await _service.addFact(kind: 'formula', text: text);
                  _factController.clear();
                  final sheet = await _service.fetchLast48();
                  if (mounted) setState(() => _sheet = sheet);
                },
              ),
            ],
          ),
        ),
        Expanded(
          child: ListView.builder(
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = Map<String, dynamic>.from(items[index] as Map);
              return ListTile(
                title: Text(item['text']?.toString() ?? ''),
                subtitle: Text(item['kind']?.toString() ?? ''),
                trailing: IconButton(
                  icon: const Icon(Icons.delete_outline),
                  onPressed: () async {
                    await _service.deleteFact(item['id'].toString());
                    final sheet = await _service.fetchLast48();
                    if (mounted) setState(() => _sheet = sheet);
                  },
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
