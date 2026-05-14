import Swal from "sweetalert2";

export const toast = (message: string, type: "success" | "error" | "warning" | "info") => {
  Swal.fire({
    toast:             true,
    position:          "top-end",
    icon:              type,
    title:             message,
    showConfirmButton: false,
    timer:             3000,
    timerProgressBar:  true,
  });
};

export const confirm = async (title: string, text: string): Promise<boolean> => {
  const result = await Swal.fire({
    title,
    text,
    icon:               "warning",
    showCancelButton:   true,
    confirmButtonColor: "#3b82f6",
    cancelButtonColor:  "#ef4444",
    confirmButtonText:  "Eny",
    cancelButtonText:   "Tsia",
  });
  return result.isConfirmed;
};

export const alert = (title: string, text: string, type: "success" | "error" | "warning" | "info") => {
  Swal.fire({
    title,
    text,
    icon:               type,
    confirmButtonColor: "#3b82f6",
    confirmButtonText:  "Ekena",
  });
};