class StudyNote {
  final String id;
  final String? chapterId;
  final String? chapterSlug;
  final String? chapterTitle;
  final String topicTitle;
  final String content;
  final int orderIndex;
  final DateTime? createdAt;

  const StudyNote({
    required this.id,
    this.chapterId,
    this.chapterSlug,
    this.chapterTitle,
    this.topicTitle = '',
    required this.content,
    this.orderIndex = 0,
    this.createdAt,
  });

  factory StudyNote.fromJson(Map<String, dynamic> json) {
    return StudyNote(
      id: json['id']?.toString() ?? '',
      chapterId: json['chapter']?.toString(),
      chapterSlug: json['chapter_slug'] as String?,
      chapterTitle: json['chapter_title'] as String?,
      topicTitle: json['topic_title'] as String? ?? '',
      content: json['content'] as String? ?? '',
      orderIndex: json['order_index'] as int? ?? 0,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'chapter': chapterId,
        'chapter_slug': chapterSlug,
        'chapter_title': chapterTitle,
        'topic_title': topicTitle,
        'content': content,
        'order_index': orderIndex,
      };

  bool get isPearl => content.length <= 220;
}

class NotesChapterGroup {
  final String key;
  final String title;
  final int order;
  final List<StudyNote> notes;

  const NotesChapterGroup({
    required this.key,
    required this.title,
    this.order = 0,
    this.notes = const [],
  });

  List<StudyNote> get pearls =>
      notes.where((n) => n.content.length <= 220).toList();

  List<StudyNote> get clinicalNotes =>
      notes.where((n) => n.content.length > 220).toList();
}

class NotesReview {
  final List<NotesChapterGroup> chapters;
  final List<StudyNote> uncategorized;
  final int total;

  const NotesReview({
    this.chapters = const [],
    this.uncategorized = const [],
    this.total = 0,
  });

  factory NotesReview.fromJson(Map<String, dynamic> json) {
    final chapterList = (json['chapters'] as List<dynamic>? ?? [])
        .map((c) {
          final m = c as Map<String, dynamic>;
          final ch = m['chapter'] as Map<String, dynamic>? ?? {};
          final notes = (m['notes'] as List<dynamic>? ?? [])
              .map((n) => StudyNote.fromJson(n as Map<String, dynamic>))
              .toList();
          return NotesChapterGroup(
            key: ch['slug'] as String? ?? 'other',
            title: ch['title'] as String? ?? 'Other',
            order: ch['order_index'] as int? ?? 99,
            notes: notes,
          );
        })
        .toList();
    final uncategorized = (json['uncategorized'] as List<dynamic>? ?? [])
        .map((n) => StudyNote.fromJson(n as Map<String, dynamic>))
        .toList();
    return NotesReview(
      chapters: chapterList,
      uncategorized: uncategorized,
      total: json['total'] as int? ?? 0,
    );
  }
}

class PearlItem {
  final String topic;
  final String pearl;
  final String? mnemonic;
  final String source;
  final String? reference;
  final bool verified;

  const PearlItem({
    required this.topic,
    required this.pearl,
    this.mnemonic,
    this.source = 'curated',
    this.reference,
    this.verified = false,
  });

  factory PearlItem.fromJson(Map<String, dynamic> json) {
    return PearlItem(
      topic: json['topic'] as String? ?? '',
      pearl: json['pearl'] as String? ?? '',
      mnemonic: json['mnemonic'] as String?,
      source: json['source'] as String? ?? 'curated',
      reference: json['reference'] as String?,
      verified: json['verified'] as bool? ?? false,
    );
  }
}

class PearlChapterGroup {
  final String title;
  final String slug;
  final List<PearlItem> pearls;

  const PearlChapterGroup({
    required this.title,
    required this.slug,
    this.pearls = const [],
  });
}
