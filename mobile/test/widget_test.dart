import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nephro_challenge_ai/main.dart';
import 'package:nephro_challenge_ai/models/leaderboard_entry.dart';
import 'package:nephro_challenge_ai/models/user.dart';
import 'package:nephro_challenge_ai/utils/json_helpers.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const NephroChallengeApp());
    await tester.pump();
    expect(find.byType(MaterialApp), findsOneWidget);
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump(const Duration(milliseconds: 600));
  });

  test('normalizes blank user names', () {
    final user = User.fromJson({
      'id': 1,
      'email': 'ada@example.com',
      'display_name': '   ',
      'name': 'Ada Lovelace',
      'username': 'ada',
    });

    expect(user.displayName, 'Ada Lovelace');
  });

  test('normalizes blank leaderboard names', () {
    final entry = LeaderboardEntry.fromJson({
      'user_id': 1,
      'display_name': '',
      'username': 'ada',
    });

    expect(entry.displayName, 'ada');
  });

  test('returns safe avatar initials', () {
    expect(JsonHelpers.initial('', fallback: 'D'), 'D');
    expect(JsonHelpers.initial('  ', fallback: 'U'), 'U');
    expect(JsonHelpers.initial(' nephrology '), 'N');
  });
}
