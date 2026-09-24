import 'package:dio/dio.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:sign_in_with_apple/sign_in_with_apple.dart';
import '../models/user.dart';
import 'api_service.dart';
import 'storage_service.dart';

class AuthResult {
  final bool success;
  final String? message;
  final User? user;
  final String? token;

  AuthResult({
    required this.success,
    this.message,
    this.user,
    this.token,
  });
}

class AuthService {
  static AuthService? _instance;
  final ApiService _api = ApiService.instance;
  final StorageService _storage = StorageService.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn(scopes: ['email', 'profile']);

  AuthService._();

  static AuthService get instance {
    _instance ??= AuthService._();
    return _instance!;
  }

  Future<AuthResult> _saveAuthResponse(Map<String, dynamic> data) async {
    final token = (data['token'] ?? data['access']) as String;
    final refresh = data['refresh'] as String?;
    final user = User.fromJson(data['user'] as Map<String, dynamic>);
    await _storage.setToken(token);
    if (refresh != null) await _storage.setRefreshToken(refresh);
    await _storage.setUserData(user.toJson());
    return AuthResult(success: true, user: user, token: token);
  }

  Future<AuthResult> login(String email, String password) async {
    try {
      final response = await _api.post('/auth/login/', data: {
        'email': email,
        'password': password,
      });
      return await _saveAuthResponse(response.data as Map<String, dynamic>);
    } catch (e) {
      return AuthResult(success: false, message: _parseError(e));
    }
  }

  Future<AuthResult> register(
      String email, String password, String? displayName) async {
    try {
      final username = email.split('@').first;
      final response = await _api.post('/auth/register/', data: {
        'username': username,
        'email': email,
        'password': password,
      });
      return await _saveAuthResponse(response.data as Map<String, dynamic>);
    } catch (e) {
      return AuthResult(success: false, message: _parseError(e));
    }
  }

  Future<AuthResult> signInWithGoogle() async {
    try {
      final googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        return AuthResult(success: false, message: 'Google sign-in cancelled');
      }
      final googleAuth = await googleUser.authentication;
      final response = await _api.post('/auth/google/', data: {
        'id_token': googleAuth.idToken,
        'access_token': googleAuth.accessToken,
      });
      return await _saveAuthResponse(response.data as Map<String, dynamic>);
    } catch (e) {
      return AuthResult(
        success: false,
        message: 'Google sign-in unavailable. Use email login or try again later.',
      );
    }
  }

  Future<AuthResult> signInWithApple() async {
    try {
      final credential = await SignInWithApple.getAppleIDCredential(
        scopes: [
          AppleIDAuthorizationScopes.email,
          AppleIDAuthorizationScopes.fullName,
        ],
      );
      final response = await _api.post('/auth/apple/', data: {
        'identity_token': credential.identityToken,
        'authorization_code': credential.authorizationCode,
        'email': credential.email,
        'given_name': credential.givenName,
        'family_name': credential.familyName,
      });
      return await _saveAuthResponse(response.data as Map<String, dynamic>);
    } catch (e) {
      return AuthResult(
        success: false,
        message: 'Apple sign-in unavailable. Use email login or try again later.',
      );
    }
  }

  Future<void> logout() async {
    try {
      await _googleSignIn.signOut();
    } catch (_) {}
    await _storage.clearAuth();
  }

  Future<bool> deleteAccount() async {
    try {
      await _api.delete('/auth/account/');
      await logout();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> isLoggedIn() async {
    return (await _storage.getToken()) != null;
  }

  Future<User?> getCurrentUser() async {
    final userData = await _storage.getUserData();
    if (userData != null) return User.fromJson(userData);
    return null;
  }

  Future<User?> fetchProfile() async {
    try {
      final response = await _api.get('/auth/profile/');
      final user = User.fromJson(response.data as Map<String, dynamic>);
      await _storage.setUserData(user.toJson());
      return user;
    } catch (_) {
      return null;
    }
  }

  String _parseError(dynamic error) {
    if (error is DioException) {
      final data = error.response?.data;
      if (data is Map && data['detail'] != null) {
        return data['detail'].toString();
      }
      if (error.response?.statusCode == 401) {
        return 'Invalid email or password.';
      }
    }
    return 'Something went wrong. Please try again.';
  }
}
