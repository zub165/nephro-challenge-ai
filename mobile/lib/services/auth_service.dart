import 'package:google_sign_in/google_sign_in.dart';
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
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
  );

  AuthService._();

  static AuthService get instance {
    _instance ??= AuthService._();
    return _instance!;
  }

  Future<AuthResult> login(String email, String password) async {
    try {
      final response = await _api.post('/auth/login', data: {
        'email': email,
        'password': password,
      });

      final data = response.data as Map<String, dynamic>;
      final token = data['token'] as String;
      final refreshToken = data['refresh_token'] as String?;
      final user = User.fromJson(data['user'] as Map<String, dynamic>);

      await _storage.setToken(token);
      if (refreshToken != null) {
        await _storage.setRefreshToken(refreshToken);
      }
      await _storage.setUserData(data['user'] as Map<String, dynamic>);

      return AuthResult(success: true, user: user, token: token);
    } catch (e) {
      return AuthResult(
        success: false,
        message: _parseError(e),
      );
    }
  }

  Future<AuthResult> register(
      String email, String password, String? displayName) async {
    try {
      final response = await _api.post('/auth/register', data: {
        'email': email,
        'password': password,
        'display_name': displayName,
      });

      final data = response.data as Map<String, dynamic>;
      final token = data['token'] as String;
      final refreshToken = data['refresh_token'] as String?;
      final user = User.fromJson(data['user'] as Map<String, dynamic>);

      await _storage.setToken(token);
      if (refreshToken != null) {
        await _storage.setRefreshToken(refreshToken);
      }
      await _storage.setUserData(data['user'] as Map<String, dynamic>);

      return AuthResult(success: true, user: user, token: token);
    } catch (e) {
      return AuthResult(
        success: false,
        message: _parseError(e),
      );
    }
  }

  Future<AuthResult> signInWithGoogle() async {
    try {
      final googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        return AuthResult(success: false, message: 'Google sign-in cancelled');
      }

      final googleAuth = await googleUser.authentication;
      final response = await _api.post('/auth/google', data: {
        'id_token': googleAuth.idToken,
        'access_token': googleAuth.accessToken,
      });

      final data = response.data as Map<String, dynamic>;
      final token = data['token'] as String;
      final refreshToken = data['refresh_token'] as String?;
      final user = User.fromJson(data['user'] as Map<String, dynamic>);

      await _storage.setToken(token);
      if (refreshToken != null) {
        await _storage.setRefreshToken(refreshToken);
      }
      await _storage.setUserData(data['user'] as Map<String, dynamic>);

      return AuthResult(success: true, user: user, token: token);
    } catch (e) {
      return AuthResult(
        success: false,
        message: _parseError(e),
      );
    }
  }

  Future<AuthResult> signInWithApple() async {
    try {
      final response = await _api.post('/auth/apple', data: {});

      final data = response.data as Map<String, dynamic>;
      final token = data['token'] as String;
      final refreshToken = data['refresh_token'] as String?;
      final user = User.fromJson(data['user'] as Map<String, dynamic>);

      await _storage.setToken(token);
      if (refreshToken != null) {
        await _storage.setRefreshToken(refreshToken);
      }
      await _storage.setUserData(data['user'] as Map<String, dynamic>);

      return AuthResult(success: true, user: user, token: token);
    } catch (e) {
      return AuthResult(
        success: false,
        message: _parseError(e),
      );
    }
  }

  Future<void> logout() async {
    try {
      await _api.post('/auth/logout');
    } catch (_) {}
    await _googleSignIn.signOut();
    await _storage.clearAuth();
  }

  Future<bool> isLoggedIn() async {
    final token = await _storage.getToken();
    return token != null;
  }

  Future<User?> getCurrentUser() async {
    final userData = await _storage.getUserData();
    if (userData != null) {
      return User.fromJson(userData);
    }
    return null;
  }

  Future<User?> fetchProfile() async {
    try {
      final response = await _api.get('/auth/profile');
      final user = User.fromJson(response.data['user'] as Map<String, dynamic>);
      await _storage.setUserData(response.data['user'] as Map<String, dynamic>);
      return user;
    } catch (_) {
      return null;
    }
  }

  Future<AuthResult> updateProfile(Map<String, dynamic> updates) async {
    try {
      final response = await _api.patch('/auth/profile', data: updates);
      final user = User.fromJson(response.data['user'] as Map<String, dynamic>);
      await _storage.setUserData(response.data['user'] as Map<String, dynamic>);
      return AuthResult(success: true, user: user);
    } catch (e) {
      return AuthResult(success: false, message: _parseError(e));
    }
  }

  Future<bool> forgotPassword(String email) async {
    try {
      await _api.post('/auth/forgot-password', data: {'email': email});
      return true;
    } catch (_) {
      return false;
    }
  }

  String _parseError(dynamic error) {
    if (error is Exception) {
      final errStr = error.toString();
      if (errStr.contains('SocketException') ||
          errStr.contains('HandshakeException')) {
        return 'No internet connection. Please try again.';
      }
      if (errStr.contains('401') || errStr.contains('Unauthorized')) {
        return 'Invalid email or password.';
      }
      if (errStr.contains('409') || errStr.contains('already exists')) {
        return 'An account with this email already exists.';
      }
      if (errStr.contains('422') || errStr.contains('Validation')) {
        return 'Please check your input and try again.';
      }
      if (errStr.contains('timeout')) {
        return 'Request timed out. Please try again.';
      }
    }
    return 'Something went wrong. Please try again.';
  }
}
