import type { ReactNode } from "react";
import Header from "./Header";
import Sidebar from "./Sidebar";

interface ChatLayoutProps {
  children: ReactNode;
}

const ChatLayout = ({ children }: ChatLayoutProps) => {
  return (
    <div className="h-screen flex flex-col bg-chat-background dark:bg-dark-background overflow-hidden">
      {/* Header */}
      <Header />

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar />

        {/* Contenu principal */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  );
};

export default ChatLayout;