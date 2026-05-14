export interface FormErrors {
  name?:     string;
  email?:    string;
  password?: string;
  confirm?:  string;
}

// Validation email
export const isValidEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

// Validation mot de passe
export const isValidPassword = (password: string): boolean => {
  return password.length >= 6;
};

// Validation formulaire login
export const validateLoginForm = (
  email: string,
  password: string
): FormErrors => {
  const errors: FormErrors = {};

  if (!email)
    errors.email = "L'email est requis";
  else if (!isValidEmail(email))
    errors.email = "L'email n'est pas valide";

  if (!password)
    errors.password = "Le mot de passe est requis";
  else if (!isValidPassword(password))
    errors.password = "Le mot de passe doit contenir au moins 6 caractères";

  return errors;
};

// Validation formulaire inscription
export const validateRegisterForm = (
  name: string,
  email: string,
  password: string,
  confirm: string
): FormErrors => {
  const errors: FormErrors = {};

  if (!name)
    errors.name = "Le nom est requis";
  else if (name.trim().length < 2)
    errors.name = "Le nom doit contenir au moins 2 caractères";

  if (!email)
    errors.email = "L'email est requis";
  else if (!isValidEmail(email))
    errors.email = "L'email n'est pas valide";

  if (!password)
    errors.password = "Le mot de passe est requis";
  else if (!isValidPassword(password))
    errors.password = "Le mot de passe doit contenir au moins 6 caractères";

  if (!confirm)
    errors.confirm = "La confirmation est requise";
  else if (confirm !== password)
    errors.confirm = "Les mots de passe ne correspondent pas";

  return errors;
};