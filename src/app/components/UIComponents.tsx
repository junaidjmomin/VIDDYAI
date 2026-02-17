import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const GlassCard = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={cn(
    "bg-popover/5 border border-border backdrop-blur-xl rounded-[32px] shadow-2xl text-foreground",
    className
  )}>
    {children}
  </div>
);

export const Button = ({ children, variant = 'primary', className, ...props }: any) => {
  const variants = {
    primary: "bg-linear-to-br from-[#8B5CF6] to-[#6D28D9] hover:from-[#9D70FF] hover:to-[#7E3AF2] shadow-[0_0_20px_rgba(139,92,246,0.4)]",
    success: "bg-linear-to-br from-[#10B981] to-[#059669] hover:from-[#14D393] hover:to-[#06B17D] shadow-[0_0_20px_rgba(16,185,129,0.4)]",
    ghost: "bg-white/5 border border-white/10 hover:bg-white/10",
  };
  
  return (
    <button 
      className={cn(
        "px-8 py-4 rounded-full font-nunito font-bold text-primary-foreground transition-all active:scale-95 disabled:opacity-50",
        variants[variant as keyof typeof variants],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};

export const Input = ({ icon: Icon, className, ...props }: any) => (
  <div className="relative group">
    {Icon && (
      <div className="absolute left-6 top-1/2 -translate-y-1/2 text-muted-foreground/50 group-focus-within:text-primary transition-colors">
        <Icon size={20} />
      </div>
    )}
    <input
      className={cn(
        "w-full bg-input-background border border-border rounded-full px-14 py-4 text-foreground placeholder:text-muted-foreground focus:outline-hidden focus:border-ring focus:ring-ring/20 transition-all",
        !Icon && "px-8",
        className
      )}
      {...props}
    />
  </div>
);
