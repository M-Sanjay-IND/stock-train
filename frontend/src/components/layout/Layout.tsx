import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import Sidebar from './Sidebar';
import Header from './Header';

const Layout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      <motion.main
        initial={false}
        animate={{ marginLeft: sidebarCollapsed ? 72 : 240 }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="flex-1 flex flex-col min-h-screen"
      >
        <Header />

        <div className="flex-1 p-6 overflow-auto">
          <Outlet />
        </div>
      </motion.main>
    </div>
  );
};

export default Layout;
