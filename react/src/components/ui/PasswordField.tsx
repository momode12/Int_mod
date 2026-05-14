import { Eye, EyeOff, CheckCircle, XCircle } from "lucide-react";
import { getPasswordStrength } from "../../utils/passwordStrength";

type Props = {
  name: string;
  label: string;
  value: string;
  show: boolean;
  toggleShow: () => void;
  error?: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

const PasswordField = ({
  name,
  label,
  value,
  show,
  toggleShow,
  error,
  onChange,
}: Props) => {
  const { score, checks } = getPasswordStrength(value);

  const isStrong = score === 4;

  const getStrengthColor = () => {
    if (score <= 1) return "bg-red-500";
    if (score === 2) return "bg-yellow-500";
    if (score === 3) return "bg-blue-500";
    return "bg-green-500";
  };

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-secondary-700 dark:text-dark-text">
        {label}
      </label>

      {/* INPUT */}
      <div className="relative">
        <input
          name={name}
          type={show ? "text" : "password"}
          value={value}
          onChange={onChange}
          placeholder="••••••••"
          className={`
            w-full px-4 py-2 pr-10 rounded-xl text-sm outline-none
            border 
            ${error ? "border-red-500" : "border-chat-input-border"}
          `}
        />

        <button
          type="button"
          onClick={toggleShow}
          className="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer"
        >
          {show ? <EyeOff size={16} /> : <Eye size={16} />}
        </button>
      </div>

      {/* BARRE DE FORCE */}
      {value && (
        <div className="w-full h-1 rounded bg-gray-200">
          <div
            className={`h-1 rounded transition-all ${getStrengthColor()}`}
            style={{ width: `${(score / 4) * 100}%` }}
          />
        </div>
      )}

      {/* CONTENU DYNAMIQUE */}
      {value && !error && (
        <>
          {/* ✅ SI OK → MESSAGE VERT */}
          {isStrong ? (
            <div className="flex items-center gap-1 text-green-500 text-xs mt-1">
              <CheckCircle size={14} />
              <span>Teny miafina matanjaka</span>
            </div>
          ) : (
            /* ❌ SI PAS OK → CHECKLIST */
            <div className="text-xs flex flex-col gap-1 mt-1">
              <Rule ok={checks.length} label="Farafahakeliny 6 tarehintsoratra" />
              <Rule ok={checks.uppercase} label="Misy litera lehibe (A-Z)" />
              <Rule ok={checks.number} label="Misy isa (0-9)" />
              <Rule ok={checks.special} label="Misy marika manokana (@, #, ...)" />
            </div>
          )}
        </>
      )}

      {/* ERREUR */}
      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  );
};

const Rule = ({ ok, label }: { ok: boolean; label: string }) => (
  <div className={`flex items-center gap-1 ${ok ? "text-green-500" : "text-red-500"}`}>
    {ok ? <CheckCircle size={14} /> : <XCircle size={14} />}
    <span>{label}</span>
  </div>
);

export default PasswordField;