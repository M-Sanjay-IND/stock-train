import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Home, Search } from 'lucide-react';

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 200 }}
        className="text-8xl font-bold gradient-text"
      >
        404
      </motion.div>
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="text-center"
      >
        <h2 className="text-xl font-semibold text-foreground mb-2">Page Not Found</h2>
        <p className="text-muted-foreground">The page you're looking for doesn't exist or has been moved.</p>
      </motion.div>
      <motion.div
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex gap-3"
      >
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 px-4 py-2 rounded-lg gradient-primary text-white text-sm font-medium"
        >
          <Home className="w-4 h-4" /> Go Home
        </button>
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-secondary text-foreground text-sm font-medium border border-border"
        >
          <Search className="w-4 h-4" /> Dashboard
        </button>
      </motion.div>
    </div>
  );
};

export default NotFound;
