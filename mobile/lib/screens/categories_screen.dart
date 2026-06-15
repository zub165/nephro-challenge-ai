import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/routes.dart';
import '../models/category.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/category_card.dart';
import '../widgets/loading_shimmer.dart';

class CategoriesScreen extends StatefulWidget {
  const CategoriesScreen({super.key});

  @override
  State<CategoriesScreen> createState() => _CategoriesScreenState();
}

class _CategoriesScreenState extends State<CategoriesScreen> {
  final _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Categories'),
      ),
      body: Consumer<DashboardProvider>(
        builder: (context, dashboard, _) {
          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: TextField(
                  controller: _searchController,
                  decoration: const InputDecoration(
                    hintText: 'Search categories...',
                    prefixIcon: Icon(Icons.search),
                  ),
                  onChanged: (v) => setState(() => _searchQuery = v.toLowerCase()),
                ),
              ),
              Expanded(
                child: dashboard.isLoading
                    ? const LoadingShimmer()
                    : _buildCategoriesGrid(context, dashboard),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildCategoriesGrid(
      BuildContext context, DashboardProvider dashboard) {
    if (dashboard.categories.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.category, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              'No categories available',
              style: GoogleFonts.inter(fontSize: 16),
            ),
          ],
        ),
      );
    }

    final categories = dashboard.categories.where((cat) {
      if (_searchQuery.isEmpty) return true;
      return cat.name.toLowerCase().contains(_searchQuery);
    }).toList();

    if (categories.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.search_off, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              'No categories match your search',
              style: GoogleFonts.inter(fontSize: 16),
            ),
          ],
        ),
      );
    }

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.85,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: categories.length,
      itemBuilder: (context, index) {
        final cat = categories[index];
        return _buildCategoryGridItem(context, cat).animate().fadeIn(
              duration: 300.ms,
              delay: (50 * index).ms,
            );
      },
    );
  }

  Widget _buildCategoryGridItem(BuildContext context, Category cat) {
    return GestureDetector(
      onTap: cat.isLocked
          ? null
          : () {
              Navigator.of(context).pushNamed(
                AppRoutes.categoryQuestions,
                arguments: cat,
              );
            },
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardTheme.color,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: cat.isLocked
                ? Colors.grey.withOpacity(0.3)
                : Theme.of(context).dividerTheme.color!,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: cat.isLocked
                        ? Colors.grey.withOpacity(0.2)
                        : Theme.of(context).colorScheme.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    cat.isLocked ? Icons.lock : Icons.book,
                    color: cat.isLocked
                        ? Colors.grey
                        : Theme.of(context).colorScheme.primary,
                    size: 20,
                  ),
                ),
                const Spacer(),
                if (cat.accuracy > 0)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: cat.accuracy >= 60
                          ? const Color(0xFF22C55E).withOpacity(0.1)
                          : const Color(0xFFF59E0B).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${cat.accuracy.toStringAsFixed(0)}%',
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: cat.accuracy >= 60
                            ? const Color(0xFF22C55E)
                            : const Color(0xFFF59E0B),
                      ),
                    ),
                  ),
              ],
            ),
            const Spacer(),
            Text(
              cat.name,
              style: GoogleFonts.inter(
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            Text(
              '${cat.questionCount} questions',
              style: GoogleFonts.inter(
                fontSize: 12,
                color: Theme.of(context)
                    .textTheme
                    .bodyMedium
                    ?.color
                    ?.withOpacity(0.7),
              ),
            ),
            if (cat.completedCount > 0) ...[
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: cat.completionPercentage,
                  backgroundColor: Theme.of(context).dividerTheme.color!,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
