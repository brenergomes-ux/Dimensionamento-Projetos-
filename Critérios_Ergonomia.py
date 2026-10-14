import math
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------------------------------------------------
# BANCO DE DADOS DE MATERIAIS
# ----------------------------------------------------------------------
MATERIAIS = {
    "Nylon (PA6/PA66)": {"E": 1800.0, "e_max": 2.0, "mu_al": 0.16, "mu_pvc": 0.25},
    "ABS":              {"E": 2200.0, "e_max": 2.0, "mu_al": 0.30, "mu_pvc": 0.35},
    "POM (Acetal / Delrin)": {"E": 2800.0, "e_max": 2.5, "mu_al": 0.18, "mu_pvc": 0.22},
    "Polipropileno (PP)": {"E": 1200.0, "e_max": 3.0, "mu_al": 0.22, "mu_pvc": 0.28}
}

ALOJAMENTOS = {
    "Alumínio Usinado": "mu_al",
    "Perfil de PVC Usinado": "mu_pvc"
}

# ----------------------------------------------------------------------
# LÓGICA DE CÁLCULO
# ----------------------------------------------------------------------
def calcular_encaixe():
    try:
        # Captura de Inputs
        mat_bucha = combo_mat_bucha.get()
        mat_aloj = combo_mat_aloj.get()
        
        d_ext = float(entry_dext.get())
        d_furo = float(entry_dfuro.get())
        d_int = float(entry_dint.get())
        L = float(entry_L.get())
        eta = float(entry_eta.get()) / 100.0  # Converte % para decimal
        
        # Propriedades do Material Selecionado
        prop_bucha = MATERIAIS[mat_bucha]
        E_modulo = prop_bucha["E"]
        e_limite = prop_bucha["e_max"]
        mu_key = ALOJAMENTOS[mat_aloj]
        mu = prop_bucha[mu_key]

        # ETAPA 1: Deformação Elástica
        interferencia = d_ext - d_furo
        if interferencia <= 0:
            messagebox.showwarning("Aviso de Geometria", "O diâmetro do furo deve ser MENOR que o diâmetro externo (Interferência > 0).")
            return

        deformacao = (interferencia / d_ext) * 100.0
        status_mat = "APROVADO" if deformacao <= e_limite else "ALERTA (Risco de Escoamento/Trinca)"

        # ETAPA 2: Pressão de Contato e Força Normal
        razao_d = (d_int / d_ext) ** 2
        pressao = (E_modulo * interferencia / d_ext) * ((1.0 - razao_d) / 2.0) * eta
        area_efetiva = math.pi * d_ext * L * eta
        forca_normal = pressao * area_efetiva

        # ETAPA 3: Forças de Inserção e Ergonomia
        forca_pico = mu * forca_normal
        forca_media = forca_pico * 0.55  # Considera alívio do chanfro/guia cônica de entrada

        # Exibição dos Resultados na Interface
        lbl_val_interferencia.config(text=f"{interferencia:.3f} mm")
        lbl_val_deformacao.config(text=f"{deformacao:.2f}% (Limite: {e_limite}%)")
        lbl_val_mat_status.config(text=status_mat, foreground="green" if deformacao <= e_limite else "red")
        
        lbl_val_pressao.config(text=f"{pressao:.2f} MPa")
        lbl_val_fn.config(text=f"{forca_normal:.1f} N")
        
        lbl_val_fpico.config(text=f"{forca_pico:.1f} N ({forca_pico/9.81:.2f} kgf)")
        lbl_val_fmedia.config(text=f"{forca_media:.1f} N ({forca_media/9.81:.2f} kgf)")

        # Diagnóstico Ergonômico (MIL-STD-1472 / ISO 9241-410)
        if forca_media <= 45.0:
            diag_txt = "MONTAGEM MANUAL OK (Polegar)"
            diag_det = "Força ≤ 45 N. O operador pode montar continuamente usando o polegar (MIL-STD-1472)."
            bg_color = "#2e7d32"  # Verde
        elif forca_media <= 85.0:
            diag_txt = "MONTAGEM MANUAL COM PALMA DA MÃO"
            diag_det = "Força entre 45 N e 85 N. Requer uso da palma da mão ou batida leve."
            bg_color = "#ef6c00"  # Laranja
        else:
            diag_txt = "DISPOSITIVO / PRENSA OBRIGATÓRIO"
            diag_det = "Força > 85 N. Exige gabarito pneumático, prensa de bancada ou martelo de borracha."
            bg_color = "#c62828"  # Vermelho

        frame_diag.config(bg=bg_color)
        lbl_diag_titulo.config(text=diag_txt, bg=bg_color)
        lbl_diag_desc.config(text=diag_det, bg=bg_color)

    except ValueError:
        messagebox.showerror("Erro de Entrada", "Insira apenas números válidos nos campos dimensionais.")

# ----------------------------------------------------------------------
# INTERFACE GRÁFICA (TKINTER)
# ----------------------------------------------------------------------
root = tk.Tk()
root.title("Dimensionamento de Encaixes por Interferência - Engenharia")
root.geometry("780x620")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

# --- PAINEL DE ENTRADA (INPUTS) ---
frame_inputs = ttk.LabelFrame(root, text=" 1. Seleção de Materiais e Dimensões Geométricas ", padding=12)
frame_inputs.pack(fill="x", padx=15, pady=10)

# Materiais
ttk.Label(frame_inputs, text="Material da Bucha/Componente:").grid(row=0, column=0, sticky="w", pady=4)
combo_mat_bucha = ttk.Combobox(frame_inputs, values=list(MATERIAIS.keys()), state="readonly", width=25)
combo_mat_bucha.set("Nylon (PA6/PA66)")
combo_mat_bucha.grid(row=0, column=1, sticky="w", pady=4, padx=8)

ttk.Label(frame_inputs, text="Material do Alojamento/Perfil:").grid(row=0, column=2, sticky="w", pady=4)
combo_mat_aloj = ttk.Combobox(frame_inputs, values=list(ALOJAMENTOS.keys()), state="readonly", width=22)
combo_mat_aloj.set("Alumínio Usinado")
combo_mat_aloj.grid(row=0, column=3, sticky="w", pady=4)

# Dimensões
ttk.Label(frame_inputs, text="Diâmetro Ext. Bucha (mm):").grid(row=1, column=0, sticky="w", pady=4)
entry_dext = ttk.Entry(frame_inputs, width=12)
entry_dext.insert(0, "12.80")
entry_dext.grid(row=1, column=1, sticky="w", pady=4, padx=8)

ttk.Label(frame_inputs, text="Diâmetro do Furo (mm):").grid(row=1, column=2, sticky="w", pady=4)
entry_dfuro = ttk.Entry(frame_inputs, width=12)
entry_dfuro.insert(0, "12.65")
entry_dfuro.grid(row=1, column=3, sticky="w", pady=4)

ttk.Label(frame_inputs, text="Diâmetro Int. Bucha (mm):").grid(row=2, column=0, sticky="w", pady=4)
entry_dint = ttk.Entry(frame_inputs, width=12)
entry_dint.insert(0, "7.10")
entry_dint.grid(row=2, column=1, sticky="w", pady=4, padx=8)

ttk.Label(frame_inputs, text="Comprimento Útil L (mm):").grid(row=2, column=2, sticky="w", pady=4)
entry_L = ttk.Entry(frame_inputs, width=12)
entry_L.insert(0, "18.00")
entry_L.grid(row=2, column=3, sticky="w", pady=4)

ttk.Label(frame_inputs, text="Área Ranhurada η (%):").grid(row=3, column=0, sticky="w", pady=4)
entry_eta = ttk.Entry(frame_inputs, width=12)
entry_eta.insert(0, "30")
entry_eta.grid(row=3, column=1, sticky="w", pady=4, padx=8)

btn_calcular = ttk.Button(frame_inputs, text="CALCULAR E ANALISAR ENCAIXE", command=calcular_encaixe)
btn_calcular.grid(row=3, column=2, columnspan=2, sticky="ew", pady=6)

# --- PAINEL DE RESULTADOS (3 ETAPAS) ---
frame_res = ttk.LabelFrame(root, text=" 2. Resultados da Avaliação de Engenharia ", padding=12)
frame_res.pack(fill="x", padx=15, pady=5)

# Etapa 1
ttk.Label(frame_res, text="[Etapa 1] Deformação:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=2)
ttk.Label(frame_res, text="Interferência Nominal:").grid(row=1, column=0, sticky="w")
lbl_val_interferencia = ttk.Label(frame_res, text="-", font=("Arial", 9, "bold"))
lbl_val_interferencia.grid(row=1, column=1, sticky="w", padx=10)

ttk.Label(frame_res, text="Deformação Radial (ε):").grid(row=1, column=2, sticky="w")
lbl_val_deformacao = ttk.Label(frame_res, text="-", font=("Arial", 9, "bold"))
lbl_val_deformacao.grid(row=1, column=3, sticky="w", padx=10)

lbl_val_mat_status = ttk.Label(frame_res, text="-", font=("Arial", 9, "bold"))
lbl_val_mat_status.grid(row=1, column=4, sticky="w")

# Etapa 2
ttk.Label(frame_res, text="[Etapa 2] Tensões e Contato:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w", pady=(8,2))
ttk.Label(frame_res, text="Pressão de Contato (p):").grid(row=3, column=0, sticky="w")
lbl_val_pressao = ttk.Label(frame_res, text="-", font=("Arial", 9, "bold"))
lbl_val_pressao.grid(row=3, column=1, sticky="w", padx=10)

ttk.Label(frame_res, text="Força Normal Total (Fn):").grid(row=3, column=2, sticky="w")
lbl_val_fn = ttk.Label(frame_res, text="-", font=("Arial", 9, "bold"))
lbl_val_fn.grid(row=3, column=3, sticky="w", padx=10)

# Etapa 3
ttk.Label(frame_res, text="[Etapa 3] Inserção e Ergonomia:", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky="w", pady=(8,2))
ttk.Label(frame_res, text="Força de Pico:").grid(row=5, column=0, sticky="w")
lbl_val_fpico = ttk.Label(frame_res, text="-", font=("Arial", 9, "bold"))
lbl_val_fpico.grid(row=5, column=1, sticky="w", padx=10)

ttk.Label(frame_res, text="Força Média (Guia Cônica):").grid(row=5, column=2, sticky="w")
lbl_val_fmedia = ttk.Label(frame_res, text="-", font=("Arial", 9, "bold"))
lbl_val_fmedia.grid(row=5, column=3, sticky="w", padx=10)

# --- PAINEL DIAGNÓSTICO ERGONÔMICO (PAINEL COLORIDO) ---
frame_diag = tk.Frame(root, bg="#424242", bd=2, relief="groove")
frame_diag.pack(fill="x", padx=15, pady=15)

lbl_diag_titulo = tk.Label(frame_diag, text="AGUARDANDO CÁLCULO", font=("Arial", 11, "bold"), fg="white", bg="#424242")
lbl_diag_titulo.pack(anchor="w", padx=10, pady=(8,2))

lbl_diag_desc = tk.Label(frame_diag, text="Preencha os parâmetros acima e clique em 'Calcular e Analisar Encaixe'.", font=("Arial", 9), fg="white", bg="#424242")
lbl_diag_desc.pack(anchor="w", padx=10, pady=(0,8))

# Execução Inicial
calcular_encaixe()
root.mainloop()