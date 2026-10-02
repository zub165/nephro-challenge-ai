class AppConstants {
  static const String appName = 'Nephro Challenge AI';
  static const String appVersion = '1.3.10';
  static const int buildNumber = 17;

  /// Production API (GoDaddy VPS / custom domain)
  static const String baseUrl = 'https://nephro-api.schedulemygroup.com/api';

  /// Privacy & support (App Store / Play Store required URLs)
  static const String privacyUrl =
      'https://zub165.github.io/nephro-challenge-ai/privacy.html';
  static const String supportUrl =
      'https://zub165.github.io/nephro-challenge-ai/support.html';
  static const String webAppUrl =
      'https://zub165.github.io/nephro-challenge-ai/app/';
  static const String deleteAccountUrl =
      'https://zub165.github.io/nephro-challenge-ai/delete.html';

  /// Lesson animation JSON is hosted on GitHub Pages, not bundled in the app
  /// binary, so animations can be corrected without a new store release.
  static const String animationBaseUrl =
      'https://zub165.github.io/nephro-challenge-ai/animations';

  static const Duration quizTimerDuration = Duration(minutes: 30);
  static const int dailyChallengeQuestions = 5;
  static const int maxStreakDays = 365;
  static const double passPercentage = 60.0;

  static const String disclaimerText =
      'This app is for medical education purposes only. '
      'It does not provide medical advice, diagnosis, or treatment. '
      'Always consult qualified healthcare professionals. '
      'Do not submit identifiable patient information.';
}
