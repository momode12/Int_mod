import type { ReactNode } from "react";

interface AuthLayoutProps {
  children: ReactNode;
}

const AuthLayout = ({ children }: AuthLayoutProps) => {
  return (
    <div className="
      min-h-screen bg-auth-background dark:bg-dark-background
      flex items-center justify-center p-4
    ">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-primary-500 flex items-center justify-center mx-auto mb-3">
            <span className="text-white font-bold text-xl">AI</span>
          </div>
          <h1 className="text-2xl font-bold text-secondary-800 dark:text-dark-text">
            ChatBot IA
          </h1>
          <p className="text-sm text-secondary-500 dark:text-dark-text-muted mt-1">
            Votre assistant intelligent
          </p>
        </div>

        {/* Contenu (login ou register) */}
        <div className="
          bg-auth-card-bg dark:bg-dark-surface
          border border-auth-card-border dark:border-dark-border
          rounded-2xl p-6 shadow-sm
        ">
          {children}
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;