import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { validateLoginForm } from "../utils/validateForm";
import type { FormErrors } from "../utils/validateForm";
import { toast } from "../utils/sweetalert";
import AuthLayout from "../components/layout/AuthLayout";
import Button from "../components/ui/button";
import Input from "../components/ui/input";
import Separator from "../components/ui/separator";
import PasswordField from "../components/ui/PasswordField";

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();

  const [form, setForm] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState<FormErrors>({});
  const [showPass, setShowPass] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setErrors((prev) => ({ ...prev, [e.target.name]: undefined }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validation = validateLoginForm(form.email, form.password);
    if (Object.keys(validation).length > 0) {
      setErrors(validation);
      return;
    }

    try {
      await login(form.email, form.password);
      toast("Tafiditra soa aman-tsara !", "success");
      navigate("/chat");
    } catch (error: unknown) {
      const message =
        error instanceof Error
          ? error.message
          : "Diso ny email na ny teny miafina";
      toast(message, "error");
    }
  };

  return (
    <AuthLayout>
      <div className="flex flex-col gap-5">
        <div className="text-center">
          <h2 className="text-xl font-bold text-secondary-800 dark:text-dark-text">
            Hiditra
          </h2>
          <p className="text-sm text-secondary-500 dark:text-dark-text-muted mt-1">
            Midira amin'ny kaontinao
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Email"
            name="email"
            type="email"
            placeholder="ohatra@email.com"
            value={form.email}
            onChange={handleChange}
            error={errors.email}
          />

          <PasswordField
            name="password"
            label="Teny miafina"
            value={form.password}
            show={showPass}
            toggleShow={() => setShowPass((p) => !p)}
            error={errors.password}
            onChange={handleChange}
          />

          <Button type="submit" className="cursor-pointer" fullWidth isLoading={isLoading}>
            Hiditra
          </Button>
        </form>

        <Separator label="na" />

        <p className="text-sm text-center text-secondary-500 dark:text-dark-text-muted">
          Tsy manana kaonty ?{" "}
          <Link
            to="/register"
            className="text-primary-500 hover:text-primary-600 font-medium cursor-pointer"
          >
            Misoratra anarana
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
};

export default LoginPage;
