import 'dart:convert';

import 'package:dio/dio.dart';

import '../config/constants.dart';
import '../models/lesson_animation.dart';

/// Loads lesson animation step data from the remote JSON files.
///
/// These files are intentionally not bundled in the app binary: they are
/// served from GitHub Pages so content fixes ship without a store release.
class AnimationService {
  AnimationService._();

  static final AnimationService instance = AnimationService._();

  /// Deliberately separate from [ApiService]: the app Dio client attaches the
  /// user's JWT to every request, and these URLs are third-party hosts.
  final Dio _dio = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 12),
      receiveTimeout: const Duration(seconds: 12),
      responseType: ResponseType.plain,
    ),
  );

  /// Extracts the bare filename from an animation URL or path.
  static String? animationFilename(String animationUrl) {
    if (animationUrl.isEmpty) return null;
    final withoutQuery = animationUrl.split('?').first;
    if (!withoutQuery.endsWith('.json')) return null;
    final segments = withoutQuery.split('/');
    if (segments.isEmpty) return null;
    final name = segments.last;
    return name.isEmpty ? null : name;
  }

  /// Builds the candidate URLs to try, in order. Absolute URLs are used as
  /// given; a bare filename falls back to the GitHub Pages copy.
  static List<String> candidateUrls(String animationUrl) {
    final filename = animationFilename(animationUrl);
    if (filename == null) {
      if (animationUrl.contains('://')) return [animationUrl];
      return const [];
    }
    if (animationUrl.contains('://')) {
      return [
        animationUrl,
        '${AppConstants.animationBaseUrl}/$filename',
      ];
    }
    return ['${AppConstants.animationBaseUrl}/$filename'];
  }

  Future<LessonAnimation> load(String animationUrl) async {
    final candidates = candidateUrls(animationUrl);
    if (candidates.isEmpty) {
      throw AnimationLoadException('Invalid animation URL');
    }

    Object? lastError;
    for (final url in candidates) {
      try {
        final response = await _dio.get<String>(url);
        final body = response.data;
        if (body == null || body.trim().isEmpty) {
          throw AnimationLoadException('Empty animation file');
        }
        final decoded = jsonDecode(body);
        if (decoded is! Map) {
          throw AnimationLoadException('Unexpected animation format');
        }
        final animation = LessonAnimation.fromJson(
          Map<String, dynamic>.from(decoded),
        );
        if (animation.steps.isEmpty) {
          throw AnimationLoadException('Animation has no steps');
        }
        return animation;
      } catch (e) {
        lastError = e;
      }
    }

    throw AnimationLoadException('Could not load animation: $lastError');
  }
}

class AnimationLoadException implements Exception {
  final String message;

  AnimationLoadException(this.message);

  @override
  String toString() => message;
}
