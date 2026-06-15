import 'package:flutter/foundation.dart';
import '../models/leaderboard_entry.dart';
import '../services/leaderboard_service.dart';

class LeaderboardProvider extends ChangeNotifier {
  final LeaderboardService _leaderboardService = LeaderboardService.instance;

  bool _isLoading = false;
  String? _error;
  List<LeaderboardEntry> _entries = [];
  LeaderboardEntry? _currentUserEntry;
  String _selectedPeriod = 'all_time';

  bool get isLoading => _isLoading;
  String? get error => _error;
  List<LeaderboardEntry> get entries => _entries;
  LeaderboardEntry? get currentUserEntry => _currentUserEntry;
  String get selectedPeriod => _selectedPeriod;

  Future<void> loadLeaderboard({String? period}) async {
    if (period != null) _selectedPeriod = period;
    _isLoading = true;
    _error = null;
    notifyListeners();

    _entries = await _leaderboardService.fetchLeaderboard(
      period: _selectedPeriod,
    );

    _currentUserEntry = await _leaderboardService.fetchCurrentUserRank(
      period: _selectedPeriod,
    );

    _isLoading = false;
    notifyListeners();
  }

  void setPeriod(String period) {
    _selectedPeriod = period;
    loadLeaderboard();
  }
}
