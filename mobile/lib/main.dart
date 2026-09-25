import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/routes.dart';
import 'config/theme.dart';
import 'providers/auth_provider.dart';
import 'providers/dashboard_provider.dart';
import 'providers/leaderboard_provider.dart';
import 'providers/navigation_provider.dart';
import 'providers/notes_provider.dart';
import 'providers/quiz_provider.dart';
import 'providers/theme_provider.dart';
import 'screens/ai_tutor_screen.dart';
import 'screens/board_prep_screen.dart';
import 'screens/categories_screen.dart';
import 'screens/category_questions_screen.dart';
import 'screens/daily_challenge_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/explanation_screen.dart';
import 'screens/leaderboard_screen.dart';
import 'screens/login_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/quiz_screen.dart';
import 'screens/register_screen.dart';
import 'screens/chapters_screen.dart';
import 'screens/chapter_detail_screen.dart';
import 'screens/lesson_screen.dart';
import 'screens/library_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/performance_analytics_screen.dart';
import 'screens/study_history_screen.dart';
import 'screens/about_screen.dart';
import 'screens/splash_screen.dart';
import 'services/storage_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await StorageService.instance.init();
  runApp(const NephroChallengeApp());
}

class NephroChallengeApp extends StatelessWidget {
  const NephroChallengeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => QuizProvider()),
        ChangeNotifierProvider(create: (_) => DashboardProvider()),
        ChangeNotifierProvider(create: (_) => LeaderboardProvider()),
        ChangeNotifierProvider(create: (_) => NotesProvider()),
        ChangeNotifierProvider(create: (_) => NavigationProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, _) {
          return MaterialApp(
            title: 'Nephro Challenge AI',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeProvider.themeMode,
            initialRoute: AppRoutes.splash,
            onGenerateRoute: (settings) {
              return _buildRoute(settings);
            },
          );
        },
      ),
    );
  }

  Route<dynamic>? _buildRoute(RouteSettings settings) {
    final args = settings.arguments;

    switch (settings.name) {
      case AppRoutes.splash:
        return MaterialPageRoute(
          builder: (_) => const SplashScreen(),
          settings: settings,
        );
      case AppRoutes.login:
        return MaterialPageRoute(
          builder: (_) => const LoginScreen(),
          settings: settings,
        );
      case AppRoutes.register:
        return MaterialPageRoute(
          builder: (_) => const RegisterScreen(),
          settings: settings,
        );
      case AppRoutes.dashboard:
        return MaterialPageRoute(
          builder: (_) => const MainShell(),
          settings: settings,
        );
      case AppRoutes.quiz:
        return MaterialPageRoute(
          builder: (_) => const QuizScreen(),
          settings: settings,
        );
      case AppRoutes.explanation:
        return MaterialPageRoute(
          builder: (_) => const ExplanationScreen(),
          settings: settings,
        );
      case AppRoutes.leaderboard:
        return MaterialPageRoute(
          builder: (_) => const LeaderboardScreen(),
          settings: settings,
        );
      case AppRoutes.profile:
        return MaterialPageRoute(
          builder: (_) => const ProfileScreen(),
          settings: settings,
        );
      case AppRoutes.categories:
        return MaterialPageRoute(
          builder: (_) => const CategoriesScreen(),
          settings: settings,
        );
      case AppRoutes.categoryQuestions:
        return MaterialPageRoute(
          builder: (_) => const CategoryQuestionsScreen(),
          settings: settings,
        );
      case AppRoutes.dailyChallenge:
        return MaterialPageRoute(
          builder: (_) => const DailyChallengeScreen(),
          settings: settings,
        );
      case AppRoutes.aiTutor:
        return MaterialPageRoute(
          builder: (_) => const AITutorScreen(),
          settings: settings,
        );
      case AppRoutes.boardPrep:
        return MaterialPageRoute(
          builder: (_) => const BoardPrepScreen(),
          settings: settings,
        );
      case AppRoutes.chapters:
        return MaterialPageRoute(builder: (_) => const ChaptersScreen(), settings: settings);
      case AppRoutes.chapterDetail:
        return MaterialPageRoute(builder: (_) => const ChapterDetailScreen(), settings: settings);
      case AppRoutes.lesson:
        return MaterialPageRoute(builder: (_) => const LessonScreen(), settings: settings);
      case AppRoutes.library:
        final tab = args is int ? args : 0;
        return MaterialPageRoute(
          builder: (_) => LibraryScreen(initialTab: tab),
          settings: settings,
        );
      case AppRoutes.settings:
        return MaterialPageRoute(
          builder: (_) => const SettingsScreen(),
          settings: settings,
        );
      case AppRoutes.performanceAnalytics:
        return MaterialPageRoute(
          builder: (_) => const PerformanceAnalyticsScreen(),
          settings: settings,
        );
      case AppRoutes.studyHistory:
        return MaterialPageRoute(
          builder: (_) => const StudyHistoryScreen(),
          settings: settings,
        );
      case AppRoutes.about:
        return MaterialPageRoute(
          builder: (_) => const AboutScreen(),
          settings: settings,
        );
      default:
        return MaterialPageRoute(
          builder: (_) => const SplashScreen(),
          settings: settings,
        );
    }
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  @override
  Widget build(BuildContext context) {
    final nav = context.watch<NavigationProvider>();
    final libraryTab = nav.libraryTabIndex;

    final screens = [
      const DashboardScreen(),
      LibraryScreen(key: ValueKey('library-$libraryTab'), initialTab: libraryTab),
      const QuizScreen(),
      const LeaderboardScreen(),
      const ProfileScreen(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: nav.shellIndex,
        children: screens,
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: 10,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: nav.shellIndex,
          onTap: (index) => nav.goToShellTab(index),
          type: BottomNavigationBarType.fixed,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.dashboard_outlined),
              activeIcon: Icon(Icons.dashboard),
              label: 'Dashboard',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.menu_book_outlined),
              activeIcon: Icon(Icons.menu_book),
              label: 'Library',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.quiz_outlined),
              activeIcon: Icon(Icons.quiz),
              label: 'Quiz',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.emoji_events_outlined),
              activeIcon: Icon(Icons.emoji_events),
              label: 'Leaderboard',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.person_outlined),
              activeIcon: Icon(Icons.person),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}
