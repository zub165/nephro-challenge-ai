/// Helpers for parsing Django REST API JSON (ids may be int or string).
class JsonHelpers {
  static String str(dynamic value, [String fallback = '']) {
    if (value == null) return fallback;
    return value.toString();
  }

  static int integer(dynamic value, [int fallback = 0]) {
    if (value is int) return value;
    if (value is num) return value.toInt();
    if (value is String) return int.tryParse(value) ?? fallback;
    return fallback;
  }

  static double decimal(dynamic value, [double fallback = 0.0]) {
    if (value is double) return value;
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? fallback;
    return fallback;
  }

  static List<Map<String, dynamic>> listOfMaps(dynamic value) {
    if (value is! List) return [];
    return value
        .whereType<Map>()
        .map((e) => Map<String, dynamic>.from(e))
        .toList();
  }

  static String? firstNonBlankString(Iterable<dynamic> values) {
    for (final value in values) {
      if (value is! String) continue;
      final normalized = value.trim();
      if (normalized.isNotEmpty) return normalized;
    }
    return null;
  }

  static String initial(dynamic value, {String fallback = '?'}) {
    final text = firstNonBlankString([value, fallback]) ?? '?';
    return text.substring(0, 1).toUpperCase();
  }
}
