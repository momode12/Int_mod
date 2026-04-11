const Footer = () => {
  return (
    <footer className="
      border-t border-secondary-200 dark:border-dark-border
      bg-secondary-100 dark:bg-dark-surface
      py-3 px-6 shrink-0
    ">
      <p className="text-xs text-center text-secondary-500 dark:text-dark-text-muted">
        © {new Date().getFullYear()} ChatBot IA — Tous droits réservés
      </p>
    </footer>
  );
};

export default Footer;