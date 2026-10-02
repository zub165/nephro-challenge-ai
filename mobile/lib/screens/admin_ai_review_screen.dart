import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../services/admin_service.dart';
import '../utils/json_helpers.dart';

class AdminAiReviewScreen extends StatefulWidget {
  const AdminAiReviewScreen({super.key});

  @override
  State<AdminAiReviewScreen> createState() => _AdminAiReviewScreenState();
}

class _AdminAiReviewScreenState extends State<AdminAiReviewScreen>
    with SingleTickerProviderStateMixin {
  final _service = AdminService.instance;
  late final TabController _tabs;
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;
  String? _error;

  static const _statuses = ['pending', 'approved', 'rejected'];

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 3, vsync: this);
    _tabs.addListener(() {
      if (!_tabs.indexIsChanging) _load();
    });
    _load();
  }

  @override
  void dispose() {
    _tabs.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final items = await _service
          .fetchAi(status: _statuses[_tabs.index])
          .timeout(const Duration(seconds: 20));
      if (!mounted) return;
      setState(() {
        _items = items;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = 'Could not load AI drafts.';
      });
    }
  }

  Future<void> _review(String id, String status) async {
    try {
      await _service.reviewAi(id, status);
      _load();
    } catch (_) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not update review status.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Review'),
        bottom: TabBar(
          controller: _tabs,
          tabs: const [
            Tab(text: 'Pending'),
            Tab(text: 'Approved'),
            Tab(text: 'Rejected'),
          ],
        ),
      ),
      body: Column(
        children: [
          if (_loading) const LinearProgressIndicator(minHeight: 3),
          if (_error != null)
            Padding(
              padding: const EdgeInsets.all(12),
              child: Text(_error!),
            ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: _load,
              child: _items.isEmpty
                  ? ListView(
                      children: const [
                        SizedBox(height: 80),
                        Center(child: Text('No drafts in this tab.')),
                      ],
                    )
                  : ListView.builder(
                      itemCount: _items.length,
                      itemBuilder: (context, index) {
                        final item = _items[index];
                        final id = JsonHelpers.str(item['id']);
                        final pending = _tabs.index == 0;
                        return Card(
                          margin: const EdgeInsets.fromLTRB(12, 8, 12, 8),
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  JsonHelpers.str(item['text'] ?? item['question_text']),
                                  style: GoogleFonts.inter(fontWeight: FontWeight.w600),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  JsonHelpers.str(item['explanation']),
                                  style: GoogleFonts.inter(fontSize: 13, height: 1.35),
                                ),
                                if (pending) ...[
                                  const SizedBox(height: 8),
                                  Row(
                                    children: [
                                      FilledButton(
                                        onPressed: () => _review(id, 'approved'),
                                        child: const Text('Approve'),
                                      ),
                                      const SizedBox(width: 8),
                                      OutlinedButton(
                                        onPressed: () => _review(id, 'rejected'),
                                        child: const Text('Reject'),
                                      ),
                                    ],
                                  ),
                                ],
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ),
        ],
      ),
    );
  }
}
