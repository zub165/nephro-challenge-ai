import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nephro_challenge_ai/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const NephroChallengeApp());
    await tester.pump();
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
