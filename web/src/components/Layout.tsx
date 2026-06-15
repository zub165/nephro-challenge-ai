import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Disclaimer from './Disclaimer';
import { motion } from 'framer-motion';

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8"
        >
          <Outlet />
        </motion.div>
      </main>
      <Disclaimer />
    </div>
  );
}
