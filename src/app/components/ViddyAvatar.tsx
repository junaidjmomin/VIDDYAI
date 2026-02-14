import React from 'react';
import { motion } from 'motion/react';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface ViddyAvatarProps {
  size?: number;
  className?: string;
}

export const ViddyAvatar = ({ size = 80, className = "" }: ViddyAvatarProps) => {
  return (
    <motion.div
      className={`relative ${className}`}
      animate={{ y: [0, -10, 0] }}
      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      style={{ width: size, height: size }}
    >
      <div className="absolute inset-0 rounded-full bg-[#8B5CF6]/20 blur-xl animate-pulse" />
      <div className="relative h-full w-full overflow-hidden rounded-full border-2 border-[#8B5CF6]/30">
        <ImageWithFallback
          src="https://images.unsplash.com/photo-1639628735078-ed2f038a193e"
          alt="Viddy Owl Mascot"
          className="h-full w-full object-cover"
        />
      </div>
      <div className="absolute -bottom-1 -right-1 h-4 w-4 rounded-full border-2 border-[#0A0E1A] bg-green-500" />
    </motion.div>
  );
};
