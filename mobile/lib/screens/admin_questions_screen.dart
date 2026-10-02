import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../models/category.dart';
import '../services/admin_service.dart';
import '../services/quiz_service.dart';
import '../utils/json_helpers.dart';

class AdminQuestionsScreen extends StatefulWidget {
  const AdminQuestionsScreen({super.key});

  @override
  State<AdminQuestionsScreen> createState() => _AdminQuestionsScreenState();
}

class _AdminQuestionsScreenState extends State<AdminQuestionsScreen> {
  final _service = AdminService.instance;
  final _search = TextEditingController();
  List<Map<String, dynamic>> _questions = [];
  List<Category> _categories = [];
  int _page = 1;
  int _totalPages = 1;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final payload = await _service
          .fetchQuestions(page: _page, search: _search.text)
          .timeout(const Duration(seconds: 20));
      final categories = await QuizService.instance.fetchCategories();
      if (!mounted) return;
      setState(() {
        _questions = JsonHelpers.listOfMaps(payload['questions']);
        _totalPages = JsonHelpers.integer(payload['totalPages'], 1);
        _categories = categories;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'Could not load questions.';
      });
    }
  }

  Future<void> _edit([Map<String, dynamic>? existing]) async {
    final saved = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (_) => _QuestionEditor(
        categories: _categories,
        existing: existing,
      ),
    );
    if (saved == true) _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Questions')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _edit(),
        child: const Icon(Icons.add),
      ),
      body: Column(
        children: [
          if (_loading) const LinearProgressIndicator(minHeight: 3),
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              controller: _search,
              decoration: const InputDecoration(
                hintText: 'Search questions',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
              onSubmitted: (_) {
                _page = 1;
                _load();
              },
            ),
          ),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(_error!),
            ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: _load,
              child: ListView.builder(
                itemCount: _questions.length,
                itemBuilder: (context, index) {
                  final item = _questions[index];
                  return ListTile(
                    title: Text(
                      JsonHelpers.str(item['text'] ?? item['question_text']),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    subtitle: Text(JsonHelpers.str(item['difficulty'])),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete_outline),
                      onPressed: () async {
                        await _service.deleteQuestion(JsonHelpers.str(item['id']));
                        _load();
                      },
                    ),
                    onTap: () => _edit(item),
                  );
                },
              ),
            ),
          ),
          if (_totalPages > 1)
            Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  TextButton(
                    onPressed: _page <= 1
                        ? null
                        : () {
                            setState(() => _page -= 1);
                            _load();
                          },
                    child: const Text('Previous'),
                  ),
                  Text('$_page / $_totalPages', style: GoogleFonts.inter()),
                  TextButton(
                    onPressed: _page >= _totalPages
                        ? null
                        : () {
                            setState(() => _page += 1);
                            _load();
                          },
                    child: const Text('Next'),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class _QuestionEditor extends StatefulWidget {
  final List<Category> categories;
  final Map<String, dynamic>? existing;

  const _QuestionEditor({required this.categories, this.existing});

  @override
  State<_QuestionEditor> createState() => _QuestionEditorState();
}

class _QuestionEditorState extends State<_QuestionEditor> {
  late final TextEditingController _text;
  late final TextEditingController _explanation;
  late final List<TextEditingController> _choices;
  String _difficulty = 'medium';
  String? _categoryId;
  String? _correctId;
  bool _saving = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final existing = widget.existing;
    _text = TextEditingController(
      text: JsonHelpers.str(existing?['text'] ?? existing?['question_text']),
    );
    _explanation = TextEditingController(
      text: JsonHelpers.str(existing?['explanation']),
    );
    final rawChoices = JsonHelpers.listOfMaps(existing?['choices']);
    _choices = List.generate(4, (index) {
      if (index < rawChoices.length) {
        return TextEditingController(
          text: JsonHelpers.str(rawChoices[index]['text']),
        );
      }
      return TextEditingController();
    });
    _difficulty = JsonHelpers.str(existing?['difficulty'], 'medium');
    _categoryId = JsonHelpers.str(existing?['categoryId']).isEmpty
        ? (widget.categories.isNotEmpty ? widget.categories.first.id : null)
        : JsonHelpers.str(existing?['categoryId']);
    final keys = ['a', 'b', 'c', 'd'];
    _correctId = 'a';
    final existingCorrect = JsonHelpers.str(existing?['correctAnswer']);
    for (var i = 0; i < rawChoices.length && i < keys.length; i++) {
      if (JsonHelpers.str(rawChoices[i]['id']) == existingCorrect) {
        _correctId = keys[i];
      }
    }
  }

  @override
  void dispose() {
    _text.dispose();
    _explanation.dispose();
    for (final c in _choices) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _save() async {
    setState(() {
      _saving = true;
      _error = null;
    });
    final keys = ['a', 'b', 'c', 'd'];
    final choices = [
      for (var i = 0; i < _choices.length; i++)
        {'id': keys[i], 'text': _choices[i].text.trim()},
    ];
    try {
      await AdminService.instance.saveQuestion(
        {
          'text': _text.text.trim(),
          'explanation': _explanation.text.trim(),
          'categoryId': _categoryId,
          'difficulty': _difficulty,
          'choices': choices,
          'correctAnswer': _correctId ?? 'a',
        },
        id: JsonHelpers.str(widget.existing?['id']).isEmpty
            ? null
            : JsonHelpers.str(widget.existing?['id']),
      );
      if (!mounted) return;
      Navigator.pop(context, true);
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _saving = false;
        _error = 'Could not save. Check every field and the correct choice.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(widget.existing == null ? 'New question' : 'Edit question',
                style: GoogleFonts.inter(fontWeight: FontWeight.w700, fontSize: 18)),
            const SizedBox(height: 12),
            TextField(
              controller: _text,
              maxLines: 4,
              decoration: const InputDecoration(
                labelText: 'Stem',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            ...List.generate(4, (index) {
              final key = ['a', 'b', 'c', 'd'][index];
              final selected = _correctId == key;
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  IconButton(
                    icon: Icon(
                      selected
                          ? Icons.radio_button_checked
                          : Icons.radio_button_off,
                    ),
                    onPressed: () => setState(() => _correctId = key),
                  ),
                  Expanded(
                    child: TextField(
                      controller: _choices[index],
                      decoration: InputDecoration(
                        labelText: 'Choice ${key.toUpperCase()}',
                      ),
                    ),
                  ),
                ],
              );
            }),
            InputDecorator(
              decoration: const InputDecoration(labelText: 'Category'),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  isExpanded: true,
                  value: widget.categories.any((c) => c.id == _categoryId)
                      ? _categoryId
                      : (widget.categories.isNotEmpty
                          ? widget.categories.first.id
                          : null),
                  items: widget.categories
                      .map((c) =>
                          DropdownMenuItem(value: c.id, child: Text(c.name)))
                      .toList(),
                  onChanged: (value) => setState(() => _categoryId = value),
                ),
              ),
            ),
            InputDecorator(
              decoration: const InputDecoration(labelText: 'Difficulty'),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  isExpanded: true,
                  value: ['easy', 'medium', 'hard', 'board'].contains(_difficulty)
                      ? _difficulty
                      : 'medium',
                  items: const [
                    DropdownMenuItem(value: 'easy', child: Text('easy')),
                    DropdownMenuItem(value: 'medium', child: Text('medium')),
                    DropdownMenuItem(value: 'hard', child: Text('hard')),
                    DropdownMenuItem(value: 'board', child: Text('board')),
                  ],
                  onChanged: (value) =>
                      setState(() => _difficulty = value ?? 'medium'),
                ),
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _explanation,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Explanation',
                border: OutlineInputBorder(),
              ),
            ),
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              ),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: _saving ? null : _save,
              child: Text(_saving ? 'Saving…' : 'Save'),
            ),
          ],
        ),
      ),
    );
  }
}
