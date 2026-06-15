import 'package:flutter/material.dart';
import '../services/storage_service.dart';

class ThemeProvider extends ChangeNotifier {
  final StorageService _storage = StorageService.instance;
  late ThemeMode _themeMode;

  ThemeProvider() {
    _themeMode =
        _storage.getDarkMode() ? ThemeMode.dark : ThemeMode.light;
  }

  ThemeMode get themeMode => _themeMode;

  bool get isDarkMode => _themeMode == ThemeMode.dark;

  void toggleTheme() {
    _themeMode =
        _themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    _storage.setDarkMode(_themeMode == ThemeMode.dark);
    notifyListeners();
  }

  void setThemeMode(ThemeMode mode) {
    _themeMode = mode;
    _storage.setDarkMode(mode == ThemeMode.dark);
    notifyListeners();
  }
}
