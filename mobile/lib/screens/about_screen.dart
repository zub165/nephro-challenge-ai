import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../config/constants.dart';
import '../config/theme.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  static const _appVersion = '1.2.1';

  Future<void> _openUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('About')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Icon(Icons.medical_services_outlined,
              size: 72, color: AppColors.teal),
          const SizedBox(height: 16),
          Text(
            'Nephro Challenge AI',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            'Version $_appVersion',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 24),
          Text(
            'Board review MCQs, high-yield pearls, and AI-powered study tools '
            'for nephrology fellowship and board preparation.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[700], height: 1.5),
          ),
          const SizedBox(height: 28),
          _LinkTile(
            icon: Icons.language,
            title: 'Web App',
            subtitle: AppConstants.webAppUrl,
            onTap: () => _openUrl(AppConstants.webAppUrl),
          ),
          _LinkTile(
            icon: Icons.privacy_tip_outlined,
            title: 'Privacy Policy',
            subtitle: 'How we handle your data',
            onTap: () => _openUrl(AppConstants.privacyUrl),
          ),
          _LinkTile(
            icon: Icons.support_agent,
            title: 'Support',
            subtitle: 'Get help or send feedback',
            onTap: () => _openUrl(AppConstants.supportUrl),
          ),
          const SizedBox(height: 24),
          Card(
            color: Colors.amber.shade50,
            child: const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'Medical disclaimer: This app is for educational purposes only '
                'and does not replace clinical judgment or official guidelines. '
                'Always verify information with current KDIGO/KDOQI standards.',
                style: TextStyle(fontSize: 13, height: 1.4),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'API: ${AppConstants.baseUrl}',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 11, color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }
}

class _LinkTile extends StatelessWidget {
  const _LinkTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: AppColors.teal),
        title: Text(title),
        subtitle: Text(subtitle, maxLines: 1, overflow: TextOverflow.ellipsis),
        trailing: const Icon(Icons.open_in_new, size: 18),
        onTap: onTap,
      ),
    );
  }
}
