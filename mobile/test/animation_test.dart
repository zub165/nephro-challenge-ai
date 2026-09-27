import 'package:flutter_test/flutter_test.dart';
import 'package:nephro_challenge_ai/models/lesson_animation.dart';
import 'package:nephro_challenge_ai/services/animation_service.dart';

void main() {
  group('LessonAnimation parsing', () {
    test('parses title, subtitle and steps', () {
      final animation = LessonAnimation.fromJson({
        'title': 'Anion Gap Metabolic Acidosis',
        'subtitle': 'MUDPILES mnemonic workflow',
        'steps': [
          {
            'title': 'Confirm metabolic acidosis',
            'body': 'Low pH with low bicarbonate.',
            'tip': 'Correct for albumin.',
          },
          {
            'title': 'High anion gap?',
            'body': 'MUDPILES.',
            'visual': 'pressures',
            'metrics': {'access': '-165', 'return': '265', 'tmp': '210'},
          },
        ],
      });

      expect(animation.title, 'Anion Gap Metabolic Acidosis');
      expect(animation.subtitle, 'MUDPILES mnemonic workflow');
      expect(animation.steps, hasLength(2));
      expect(animation.isCrrt, isFalse);
      expect(animation.steps.first.tip, 'Correct for albumin.');
      expect(animation.steps.first.visual, isEmpty);
      expect(animation.steps.first.hasMetrics, isFalse);
      expect(animation.steps.last.visual, 'pressures');
      expect(animation.steps.last.metrics['access'], '-165');
      expect(animation.steps.last.metrics['return'], '265');
    });

    test('detects the crrt theme', () {
      final animation = LessonAnimation.fromJson({
        'theme': 'crrt',
        'steps': [
          {'title': 'a', 'body': 'b'},
        ],
      });
      expect(animation.isCrrt, isTrue);
    });

    test('tolerates missing and malformed fields', () {
      final animation = LessonAnimation.fromJson({
        'steps': [
          {'title': null, 'body': 12},
          'not-a-map',
        ],
      });

      expect(animation.title, isEmpty);
      expect(animation.subtitle, isEmpty);
      expect(animation.steps, hasLength(1));
      expect(animation.steps.first.title, isEmpty);
      // JsonHelpers.str coerces scalars, so a numeric body renders as text
      // instead of crashing the player.
      expect(animation.steps.first.body, '12');
    });

    test('empty steps list is reported as empty', () {
      expect(LessonAnimation.fromJson({'steps': []}).steps, isEmpty);
      expect(LessonAnimation.fromJson({}).steps, isEmpty);
    });
  });

  group('AnimationService URL resolution', () {
    test('extracts the filename from a full url', () {
      expect(
        AnimationService.animationFilename(
          'https://zub165.github.io/nephro-challenge-ai/animations/anion-gap-acidosis.json',
        ),
        'anion-gap-acidosis.json',
      );
    });

    test('ignores query strings when extracting the filename', () {
      expect(
        AnimationService.animationFilename('https://example.com/a/b.json?v=2'),
        'b.json',
      );
    });

    test('returns null for non-json and empty urls', () {
      expect(AnimationService.animationFilename(''), isNull);
      expect(
        AnimationService.animationFilename('https://example.com/page.html'),
        isNull,
      );
    });

    test('absolute url is tried first, then the github pages fallback', () {
      final candidates = AnimationService.candidateUrls(
        'https://zub165.github.io/nephro-challenge-ai/animations/ckd-mbd-pathway.json',
      );
      expect(candidates.first,
          'https://zub165.github.io/nephro-challenge-ai/animations/ckd-mbd-pathway.json');
      expect(candidates.last, endsWith('/animations/ckd-mbd-pathway.json'));
    });

    test('bare filename resolves to the remote animation host', () {
      final candidates = AnimationService.candidateUrls('hd-complications.json');
      expect(candidates, hasLength(1));
      expect(candidates.single, endsWith('/animations/hd-complications.json'));
      expect(candidates.single, startsWith('https://'));
    });

    test('no candidates for an unusable url', () {
      expect(AnimationService.candidateUrls(''), isEmpty);
      expect(AnimationService.candidateUrls('not-a-json-file'), isEmpty);
    });
  });
}
