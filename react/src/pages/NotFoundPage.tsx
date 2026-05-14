import { useNavigate } from "react-router-dom";
import Button from "../components/ui/button";
import { Home, ArrowLeft } from "lucide-react";

const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-dark-background flex items-center justify-center p-6">
      <div className="text-center flex flex-col items-center gap-6">

        {/* 404 */}
        <div className="text-8xl font-bold text-primary-500 select-none">
          404
        </div>

        <div>
          <h1 className="text-2xl font-bold text-secondary-800 dark:text-dark-text mb-2">
            Tsy hita ny pejy
          </h1>
          <p className="text-secondary-500 dark:text-dark-text-muted text-sm max-w-sm">
            Tsy misy na nafindra ny pejy tadiavina.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={() => navigate(-1)}>
            <ArrowLeft size={16} />
            Hiverina
          </Button>
          <Button onClick={() => navigate("/")}>
            <Home size={16} />
            Pejy fandraisana
          </Button>
        </div>

      </div>
    </div>
  );
};

export default NotFoundPage;