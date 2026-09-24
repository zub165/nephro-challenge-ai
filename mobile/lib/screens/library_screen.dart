import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'chapters_screen.dart';
import 'my_book_screen.dart';
import 'pearls_screen.dart';

class LibraryScreen extends StatefulWidget {
  final int initialTab;

  const LibraryScreen({super.key, this.initialTab = 0});

  @override
  State<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends State<LibraryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: 3,
      vsync: this,
      initialIndex: widget.initialTab.clamp(0, 2),
    );
  }

  @override
  void didUpdateWidget(LibraryScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialTab != widget.initialTab) {
      _tabController.animateTo(widget.initialTab.clamp(0, 2));
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Study Library'),
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: [
            Tab(
              child: Text(
                'Board',
                style: GoogleFonts.inter(fontWeight: FontWeight.w600),
              ),
            ),
            Tab(
              child: Text(
                'My Book',
                style: GoogleFonts.inter(fontWeight: FontWeight.w600),
              ),
            ),
            Tab(
              child: Text(
                'Pearls',
                style: GoogleFonts.inter(fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          ChaptersScreen(embedded: true),
          MyBookScreen(),
          PearlsScreen(),
        ],
      ),
    );
  }
}
