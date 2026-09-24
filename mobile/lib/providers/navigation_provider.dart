import 'package:flutter/foundation.dart';

class NavigationProvider extends ChangeNotifier {
  int shellIndex = 0;
  int libraryTabIndex = 0;

  void goToShellTab(int index, {int libraryTab = 0}) {
    shellIndex = index;
    libraryTabIndex = libraryTab;
    notifyListeners();
  }

  void goToLibrary(int tab) => goToShellTab(1, libraryTab: tab);
}
