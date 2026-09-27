import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nephro_challenge_ai/models/lesson_animation.dart';
import 'package:nephro_challenge_ai/screens/animation_screen.dart';

LessonAnimation _animation({String theme = 'default'}) {
  return LessonAnimation.fromJson({
    'title': 'Anion Gap Metabolic Acidosis',
    'subtitle': 'MUDPILES mnemonic workflow',
    'theme': theme,
    'steps': [
      {
        'title': 'Confirm metabolic acidosis',
        'body': 'Low pH with low bicarbonate.',
        'tip': 'Always correct for albumin.',
      },
      {
        'title': 'High anion gap?',
        'body': 'Think MUDPILES.',
        'visual': 'pressures',
        'metrics': {'access': '-165', 'return': '265'},
      },
      {
        'title': 'Treat the cause',
        'body': 'DKA or lactic acidosis.',
        'visual': 'lab-table',
        'metrics': {'egfr': '32', 'dose_reduction': '50%'},
      },
    ],
  });
}

Widget _host(Widget child) => MaterialApp(home: child);

void main() {
  testWidgets('renders title, step, pearl and step counter', (tester) async {
    await tester.pumpWidget(_host(AnimationScreen(
      animationUrl: 'https://example.com/animations/a.json',
      fallbackTitle: 'Fallback',
      loader: (_) async => _animation(),
    )));
    await tester.pumpAndSettle();

    expect(find.text('Anion Gap Metabolic Acidosis'), findsOneWidget);
    expect(find.text('MUDPILES mnemonic workflow'), findsOneWidget);
    expect(find.text('ANIMATED ALGORITHM'), findsOneWidget);
    expect(find.text('Confirm metabolic acidosis'), findsOneWidget);
    expect(find.text('Low pH with low bicarbonate.'), findsOneWidget);
    expect(find.text('PEARL'), findsOneWidget);
    expect(find.text('Always correct for albumin.'), findsOneWidget);
    expect(find.text('Step 1 of 3'), findsOneWidget);
  });

  testWidgets('next and previous move between steps', (tester) async {
    await tester.pumpWidget(_host(AnimationScreen(
      animationUrl: 'https://example.com/animations/a.json',
      fallbackTitle: 'Fallback',
      loader: (_) async => _animation(),
    )));
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip('Next step'));
    await tester.pumpAndSettle();
    expect(find.text('Step 2 of 3'), findsOneWidget);
    expect(find.text('High anion gap?'), findsOneWidget);

    await tester.tap(find.byTooltip('Previous step'));
    await tester.pumpAndSettle();
    expect(find.text('Step 1 of 3'), findsOneWidget);
  });

  testWidgets('previous is disabled on the first step', (tester) async {
    await tester.pumpWidget(_host(AnimationScreen(
      animationUrl: 'https://example.com/animations/a.json',
      fallbackTitle: 'Fallback',
      loader: (_) async => _animation(),
    )));
    await tester.pumpAndSettle();

    final previous = tester.widget<IconButton>(
      find.widgetWithIcon(IconButton, Icons.chevron_left),
    );
    expect(previous.onPressed, isNull);

    final next = tester.widget<IconButton>(
      find.widgetWithIcon(IconButton, Icons.chevron_right),
    );
    expect(next.onPressed, isNotNull);
  });

  testWidgets('renders metric values for the pressures visual', (tester) async {
    await tester.pumpWidget(_host(AnimationScreen(
      animationUrl: 'https://example.com/animations/a.json',
      fallbackTitle: 'Fallback',
      loader: (_) async => _animation(),
    )));
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip('Next step'));
    await tester.pumpAndSettle();

    expect(find.text('-165'), findsOneWidget);
    expect(find.text('265'), findsOneWidget);
    expect(find.text('ACCESS'), findsOneWidget);
    expect(find.text('RETURN'), findsOneWidget);
  });

  testWidgets('unknown visual types still show their metrics', (tester) async {
    await tester.pumpWidget(_host(AnimationScreen(
      animationUrl: 'https://example.com/animations/a.json',
      fallbackTitle: 'Fallback',
      loader: (_) async => _animation(),
    )));
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip('Next step'));
    await tester.pumpAndSettle();
    await tester.tap(find.byTooltip('Next step'));
    await tester.pumpAndSettle();

    // lab-table is not a known visual, so the generic metric chips are used.
    expect(find.text('EGFR'), findsOneWidget);
    expect(find.text('32'), findsOneWidget);
    expect(find.text('DOSE REDUCTION'), findsOneWidget);
    expect(find.text('50%'), findsOneWidget);
  });

  testWidgets('autoplay advances steps on its own', (tester) async {
    await tester.pumpWidget(_host(AnimationScreen(
      animationUrl: 'https://example.com/animations/a.json',
      fallbackTitle: 'Fallback',
      loader: (_) async => _animation(),
    )));
    await tester.pumpAndSettle();

    expect(find.text('Step 1 of 3'), findsOneWidget);
    await tester.tap(find.byTooltip('Play'));
    await tester.pump(const Duration(milliseconds: 4600));
    await tester.pump();
    expect(find.text('Step 2 of 3'), findsOneWidget);

    await tester.pump(const Duration(milliseconds: 4600));
    await tester.pump();
    expect(find.text('Step 3 of 3'), findsOneWidget);
  });

  testWidgets('shows the fallback message when loading fails', (tester) async {
    await tester.pumpWidget(_host(AnimationScreen(
      animationUrl: 'https://example.com/animations/missing.json',
      fallbackTitle: 'Missing Animation',
      fallbackSummary: 'A short summary',
      loader: (_) async => throw Exception('boom'),
    )));
    await tester.pumpAndSettle();

    expect(find.text('Missing Animation'), findsOneWidget);
    expect(find.text('A short summary'), findsOneWidget);
    expect(find.text('Animation file unavailable'), findsOneWidget);
    expect(find.text('Retry'), findsOneWidget);
  });

  testWidgets('crrt theme is parsed from the payload', (tester) async {
    await tester.pumpWidget(_host(AnimationScreen(
      animationUrl: 'https://example.com/animations/a.json',
      fallbackTitle: 'Fallback',
      loader: (_) async => _animation(theme: 'crrt'),
    )));
    await tester.pumpAndSettle();

    expect(find.text('Anion Gap Metabolic Acidosis'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
