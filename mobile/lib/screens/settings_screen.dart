import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../config/constants.dart';
import '../providers/theme_provider.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notificationsEnabled = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildSectionHeader('Appearance'),
          const SizedBox(height: 8),
          Consumer<ThemeProvider>(
            builder: (context, themeProvider, _) {
              return Container(
                margin: const EdgeInsets.only(bottom: 8),
                decoration: BoxDecoration(
                  color: Theme.of(context).cardTheme.color,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Theme.of(context).dividerTheme.color!),
                ),
                child: SwitchListTile(
                  title: Text(
                    'Dark Mode',
                    style: GoogleFonts.inter(fontSize: 16),
                  ),
                  subtitle: Text(
                    'Toggle dark theme',
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      color: Theme.of(context)
                          .textTheme
                          .bodyMedium
                          ?.color
                          ?.withOpacity(0.7),
                    ),
                  ),
                  secondary: Icon(
                    themeProvider.isDarkMode ? Icons.dark_mode : Icons.light_mode,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  value: themeProvider.isDarkMode,
                  onChanged: (_) => themeProvider.toggleTheme(),
                  activeColor: Theme.of(context).colorScheme.secondary,
                ),
              );
            },
          ),
          const SizedBox(height: 24),
          _buildSectionHeader('Notifications'),
          const SizedBox(height: 8),
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            decoration: BoxDecoration(
              color: Theme.of(context).cardTheme.color,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Theme.of(context).dividerTheme.color!),
            ),
            child: SwitchListTile(
              title: Text(
                'Push Notifications',
                style: GoogleFonts.inter(fontSize: 16),
              ),
              subtitle: Text(
                'Daily reminders and streak alerts',
                style: GoogleFonts.inter(
                  fontSize: 13,
                  color: Theme.of(context)
                      .textTheme
                      .bodyMedium
                      ?.color
                      ?.withOpacity(0.7),
                ),
              ),
              secondary: const Icon(Icons.notifications_outlined),
              value: _notificationsEnabled,
              onChanged: (v) => setState(() => _notificationsEnabled = v),
              activeColor: Theme.of(context).colorScheme.secondary,
            ),
          ),
          const SizedBox(height: 24),
          _buildSectionHeader('Quiz Settings'),
          const SizedBox(height: 8),
          _buildSettingTile(
            context,
            'Question Timer',
            '30 seconds per question',
            Icons.timer_outlined,
          ),
          _buildSettingTile(
            context,
            'Questions per Quiz',
            '10 questions',
            Icons.format_list_numbered,
          ),
          const SizedBox(height: 24),
          _buildSectionHeader('Account'),
          const SizedBox(height: 8),
          _buildSettingTile(
            context,
            'Change Password',
            'Update your password',
            Icons.lock_outlined,
          ),
          _buildSettingTile(
            context,
            'Delete Account',
            'Permanently delete your data',
            Icons.delete_forever_outlined,
            isDestructive: true,
          ),
          const SizedBox(height: 24),
          _buildSectionHeader('About'),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              color: Theme.of(context).cardTheme.color,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Theme.of(context).dividerTheme.color!),
            ),
            child: Column(
              children: [
                ListTile(
                  title: Text('Version',
                      style: GoogleFonts.inter(fontSize: 16)),
                  subtitle: Text(AppConstants.appVersion,
                      style: GoogleFonts.inter(fontSize: 13)),
                  leading: const Icon(Icons.info_outline),
                ),
                const Divider(height: 1),
                ListTile(
                  title: Text('Disclaimer',
                      style: GoogleFonts.inter(fontSize: 16)),
                  subtitle: Text(
                    AppConstants.disclaimerText,
                    style: GoogleFonts.inter(fontSize: 13),
                  ),
                  leading: const Icon(Icons.warning_amber_outlined),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title,
        style: GoogleFonts.inter(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: Theme.of(context)
              .textTheme
              .bodyMedium
              ?.color
              ?.withOpacity(0.7),
        ),
      ),
    );
  }

  Widget _buildSettingTile(
    BuildContext context,
    String title,
    String subtitle,
    IconData icon, {
    bool isDestructive = false,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Theme.of(context).cardTheme.color,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Theme.of(context).dividerTheme.color!),
      ),
      child: ListTile(
        title: Text(
          title,
          style: GoogleFonts.inter(
            fontSize: 16,
            color: isDestructive
                ? const Color(0xFFEF4444)
                : null,
          ),
        ),
        subtitle: Text(
          subtitle,
          style: GoogleFonts.inter(
            fontSize: 13,
            color: Theme.of(context)
                .textTheme
                .bodyMedium
                ?.color
                ?.withOpacity(0.7),
          ),
        ),
        leading: Icon(
          icon,
          color: isDestructive
              ? const Color(0xFFEF4444)
              : Theme.of(context).colorScheme.primary,
        ),
        trailing: const Icon(Icons.chevron_right, size: 20),
        onTap: () {},
      ),
    );
  }
}
