import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { MessageSquare, Zap, Shield, ArrowRight } from "lucide-react";
import Button from "../components/ui/button";
import Footer from "../components/layout/Footer";

const HomePage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  return (
    <div className="h-screen flex flex-col bg-secondary-50 dark:bg-dark-background overflow-hidden">

      {/* Header */}
      <header className="border-b border-secondary-200 dark:border-dark-border bg-white dark:bg-dark-surface px-6 py-3 shrink-0">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center">
              <span className="text-white font-bold text-sm">AI</span>
            </div>
            <span className="font-bold text-secondary-800 dark:text-dark-text">
              ChatBot IA
            </span>
          </div>
          <div className="flex items-center gap-2">
            {isAuthenticated ? (
              <Button onClick={() => navigate("/chat")}>
                Hiditra amin'ny resaka
              </Button>
            ) : (
              <>
                <Button variant="ghost" className="cursor-pointer" onClick={() => navigate("/login")}>
                  Hiditra
                </Button>
                <Button className="cursor-pointer" onClick={() => navigate("/register")}>
                  Misoratra anarana
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Body */}
      <div className="flex-1 flex flex-col items-center justify-between max-w-5xl mx-auto w-full px-6 py-8">

        {/* Hero */}
        <div className="flex flex-col items-center text-center gap-4 flex-1 justify-center">
          <div className="w-14 h-14 rounded-2xl bg-primary-500 flex items-center justify-center">
            <MessageSquare size={28} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-secondary-900 dark:text-dark-text">
            Ny mpanampy AI mahiratra anao
          </h1>
          <p className="text-base text-secondary-500 dark:text-dark-text-muted max-w-md">
            Manontania, mahazo valiny avy hatrany amin'ny alalan'ny chatbot AI mahery vaika.
          </p>
          <div className="flex items-center gap-3 mt-2">
            <Button
              size="lg"
              className="cursor-pointer"
              onClick={() => navigate(isAuthenticated ? "/chat" : "/register")}
            >
              Manomboka maimaimpoana
              <ArrowRight size={18} />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="cursor-pointer"
              onClick={() => navigate("/login")}
            >
              Hiditra
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
          {[
            {
              icon: <Zap size={20} className="text-primary-500" />,
              title: "Haingana",
              description: "Valiny avy hatrany amin'ny fotoana izy io",
            },
            {
              icon: <MessageSquare size={20} className="text-primary-500" />,
              title: "Mahiratra",
              description: "Mahazo ny tontolon'ny resaka atao",
            },
            {
              icon: <Shield size={20} className="text-primary-500" />,
              title: "Voaro",
              description: "Voatahiry sy voaro ny angonao",
            },
          ].map((feature, index) => (
            <div
              key={index}
              className="
                bg-white dark:bg-dark-surface
                border border-secondary-200 dark:border-dark-border
                rounded-2xl p-4 flex items-center gap-4
              "
            >
              <div className="w-9 h-9 rounded-xl bg-primary-50 dark:bg-dark-background flex items-center justify-center shrink-0">
                {feature.icon}
              </div>
              <div>
                <h3 className="font-semibold text-secondary-800 dark:text-dark-text text-sm">
                  {feature.title}
                </h3>
                <p className="text-xs text-secondary-500 dark:text-dark-text-muted mt-0.5">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>

      </div>

      <Footer />

    </div>
  );
};

export default HomePage;