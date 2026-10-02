import 'package:flutter/material.dart';

class NavigationProvider extends ChangeNotifier {
  int shellIndex = 0;
  int libraryTabIndex = 0;
  final scaffoldKey = GlobalKey<ScaffoldState>();

  void goToShellTab(int index, {int libraryTab = 0}) {
    shellIndex = index;
    libraryTabIndex = libraryTab;
    notifyListeners();
  }

  void goToLibrary(int tab) => goToShellTab(1, libraryTab: tab);

  void openMenu() => scaffoldKey.currentState?.openDrawer();
}
