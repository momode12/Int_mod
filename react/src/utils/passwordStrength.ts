export const passwordRules = {
  minLength: (password: string) => password.length >= 6,
  hasUppercase: (password: string) => /[A-Z]/.test(password),
  hasNumber: (password: string) => /[0-9]/.test(password),
  hasSpecial: (password: string) => /[^A-Za-z0-9]/.test(password),
};

export const getPasswordStrength = (password: string) => {
  const checks = [
    passwordRules.minLength(password),
    passwordRules.hasUppercase(password),
    passwordRules.hasNumber(password),
    passwordRules.hasSpecial(password),
  ];

  const score = checks.filter(Boolean).length;

  return {
    score,
    checks: {
      length: checks[0],
      uppercase: checks[1],
      number: checks[2],
      special: checks[3],
    },
  };
};