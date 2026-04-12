import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";
import MainLayout from "../components/layout/MainLayout";
import Card from "../components/ui/card";
import Button from "../components/ui/button";
import Input from "../components/ui/input";
import Avatar from "../components/ui/avatar";
import Separator from "../components/ui/separator";
import { ArrowLeft, LogOut } from "lucide-react";

const ProfilePage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { showToast } = useToast();

  const [form, setForm] = useState({
    name:  user?.name  ?? "",
    email: user?.email ?? "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO : antso API hamafisana ny mombamomba
    showToast("Voaova ny mombamomba !", "success");
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <MainLayout>
      <div className="max-w-xl mx-auto flex flex-col gap-6">

        {/* Hiverina */}
        <button
          onClick={() => navigate("/chat")}
          className="flex items-center gap-2 text-sm text-secondary-500 dark:text-dark-text-muted hover:text-secondary-800 dark:hover:text-dark-text transition-colors w-fit"
        >
          <ArrowLeft size={16} />
          Hiverina amin'ny resaka
        </button>

        {/* Avatar + mombamomba */}
        <Card>
          <div className="flex flex-col items-center gap-3 py-4">
            <Avatar name={user?.name} size="lg" />
            <div className="text-center">
              <p className="font-semibold text-secondary-800 dark:text-dark-text">
                {user?.name}
              </p>
              <p className="text-sm text-secondary-500 dark:text-dark-text-muted">
                {user?.email}
              </p>
            </div>
          </div>
        </Card>

        {/* Formy */}
        <Card>
          <h3 className="font-semibold text-secondary-800 dark:text-dark-text mb-4">
            Ovay ny mombamomba
          </h3>
          <form onSubmit={handleSave} className="flex flex-col gap-4">
            <Input
              label="Anarana feno"
              name="name"
              value={form.name}
              onChange={handleChange}
            />
            <Input
              label="Email"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
            />
            <Button type="submit" fullWidth>
              Tehirizo
            </Button>
          </form>
        </Card>

        <Separator />

        {/* Hivoaka */}
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-secondary-800 dark:text-dark-text text-sm">
                Hivoaka
              </p>
              <p className="text-xs text-secondary-500 dark:text-dark-text-muted mt-0.5">
                Hiverina amin'ny pejy hiditra ianao
              </p>
            </div>
            <Button variant="danger" onClick={handleLogout}>
              <LogOut size={16} />
              Hivoaka
            </Button>
          </div>
        </Card>

      </div>
    </MainLayout>
  );
};

export default ProfilePage;