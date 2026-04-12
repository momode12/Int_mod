import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { validateRegisterForm } from "../utils/validateForm";
import type { FormErrors } from "../utils/validateForm";
import { toast } from "../utils/sweetalert";

import AuthLayout from "../components/layout/AuthLayout";
import Button from "../components/ui/button";
import Input from "../components/ui/input";
import Separator from "../components/ui/separator";
import PasswordField from "../components/ui/PasswordField";

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuth();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirm: "",
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setErrors((prev) => ({ ...prev, [e.target.name]: undefined }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validation = validateRegisterForm(
      form.name,
      form.email,
      form.password,
      form.confirm
    );

    if (Object.keys(validation).length > 0) {
      setErrors(validation);
      return;
    }

    try {
      await register(form.name, form.email, form.password);
      toast("Vita ny fanoratana anarana !", "success");
      navigate("/chat");
    } catch (error: unknown) {
      const message =
        error instanceof Error
          ? error.message
          : "Nisy hadisoana, avereno !";
      toast(message, "error");
    }
  };

  return (
    <AuthLayout>
      <div className="flex flex-col gap-5">
        <div className="text-center">
          <h2 className="text-xl font-bold text-secondary-800 dark:text-dark-text">
            Mamorona kaonty
          </h2>
          <p className="text-sm text-secondary-500 dark:text-dark-text-muted mt-1">
            Tonga ao amin'ny ChatBot IA maimaimpoana
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Anarana feno"
            name="name"
            type="text"
            placeholder="John Doe"
            value={form.name}
            onChange={handleChange}
            error={errors.name}
          />

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

          <PasswordField
            name="confirm"
            label="Avereno ny teny miafina"
            value={form.confirm}
            show={showConfirm}
            toggleShow={() => setShowConfirm((p) => !p)}
            error={errors.confirm}
            onChange={handleChange}
          />

          <Button type="submit" className="cursor-pointer" fullWidth isLoading={isLoading}>
            Mamorona ny kaontiko
          </Button>
        </form>

        <Separator label="na" />

        <p className="text-sm text-center text-secondary-500 dark:text-dark-text-muted">
          Manana kaonty sahady ?{" "}
          <Link
            to="/login"
            className="text-primary-500 hover:text-primary-600 font-medium cursor-pointer"
          >
            Hiditra
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
};

export default RegisterPage;