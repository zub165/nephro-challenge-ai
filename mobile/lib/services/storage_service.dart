import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class StorageService {
  static StorageService? _instance;
  late final FlutterSecureStorage _secureStorage;
  SharedPreferences? _prefs;

  StorageService._() {
    _secureStorage = const FlutterSecureStorage(
      aOptions: AndroidOptions(encryptedSharedPreferences: true),
    );
  }

  static StorageService get instance {
    _instance ??= StorageService._();
    return _instance!;
  }

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  Future<void> setToken(String token) async {
    await _secureStorage.write(key: 'auth_token', value: token);
  }

  Future<String?> getToken() async {
    return await _secureStorage.read(key: 'auth_token');
  }

  Future<void> setRefreshToken(String token) async {
    await _secureStorage.write(key: 'refresh_token', value: token);
  }

  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: 'refresh_token');
  }

  Future<void> setUserData(Map<String, dynamic> userData) async {
    await _secureStorage.write(
      key: 'user_data',
      value: jsonEncode(userData),
    );
  }

  Future<Map<String, dynamic>?> getUserData() async {
    final data = await _secureStorage.read(key: 'user_data');
    if (data != null) {
      return jsonDecode(data) as Map<String, dynamic>;
    }
    return null;
  }

  Future<void> clearAuth() async {
    await _secureStorage.deleteAll();
    await _prefs?.clear();
  }

  Future<void> setDarkMode(bool value) async {
    await _prefs?.setBool('dark_mode', value);
  }

  bool getDarkMode() {
    return _prefs?.getBool('dark_mode') ?? false;
  }

  Future<void> setNotificationsEnabled(bool value) async {
    await _prefs?.setBool('notifications_enabled', value);
  }

  bool getNotificationsEnabled() {
    return _prefs?.getBool('notifications_enabled') ?? true;
  }

  Future<void> setDailyChallengeCompleted(DateTime date) async {
    await _prefs?.setString(
      'daily_challenge_date',
      date.toIso8601String(),
    );
  }

  DateTime? getDailyChallengeCompleted() {
    final dateStr = _prefs?.getString('daily_challenge_date');
    if (dateStr != null) {
      return DateTime.parse(dateStr);
    }
    return null;
  }

  Future<void> setLastOpened(DateTime date) async {
    await _prefs?.setString('last_opened', date.toIso8601String());
  }

  DateTime? getLastOpened() {
    final dateStr = _prefs?.getString('last_opened');
    if (dateStr != null) {
      return DateTime.parse(dateStr);
    }
    return null;
  }

  Future<void> setOnboardingComplete() async {
    await _prefs?.setBool('onboarding_complete', true);
  }

  bool isOnboardingComplete() {
    return _prefs?.getBool('onboarding_complete') ?? false;
  }

  Future<void> setInt(String key, int value) async {
    await _prefs?.setInt(key, value);
  }

  int getInt(String key, {int defaultValue = 0}) {
    return _prefs?.getInt(key) ?? defaultValue;
  }

  Future<void> setString(String key, String value) async {
    await _prefs?.setString(key, value);
  }

  String? getString(String key) {
    return _prefs?.getString(key);
  }
}
