import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import plotly.express as px
from pandastable import Table

# -------------------------------
# Función para limpiar datos
# -------------------------------
def limpiar_datos(df):
    df.columns = df.columns.str.strip()
    formato_fecha = '%m/%d/%Y %I:%M:%S %p'

    df['Fecha Ingreso'] = pd.to_datetime(df['Fecha Ingreso'], format=formato_fecha, errors='coerce')
    df['Fecha Egreso'] = pd.to_datetime(df['Fecha Egreso'], format=formato_fecha, errors='coerce')

    df['Fecha Ingreso'] = df['Fecha Ingreso'].dt.strftime('%d/%m/%Y')
    df['Fecha Egreso'] = df['Fecha Egreso'].dt.strftime('%d/%m/%Y')

    df['Donde se encontró'] = df['Donde se encontró'].str.strip().str.title()
    # Normalizo el nombre
    df['Nombre'] = df['Nombre'].str.replace('*', '', regex=False).str.strip()
    df['Nombre'] = df['Nombre'].replace('', 'Sin Nombre')
    df['Nombre'] = df['Nombre'].fillna('Sin Nombre')

    def separar_sexo_estado(valor):
        if pd.isna(valor): return pd.Series(["Desconocido", "Desconocido"])
        partes = valor.split()
        if len(partes) == 2:
            return pd.Series([partes[1], partes[0]])
        else:
            return pd.Series([valor, "Desconocido"])

    df[['Sexo Ingreso', 'Estado Reproductivo Ingreso']] = df['Sexo y estado Ingreso'].apply(separar_sexo_estado)
    df[['Sexo Egreso', 'Estado Reproductivo Egreso']] = df['Sexo y estado Egreso'].apply(separar_sexo_estado)

    df['Color'] = df['Color'].str.strip().str.title()
    df['Raza'] = df['Raza'].str.strip().str.title()
    df['Tipo de Animal'] = df['Tipo de Animal'].str.strip().str.title()
    df['Datos Faltantes'] = df.isnull().sum(axis=1)

    return df

# -------------------------------
# Función para mostrar gráficos
# -------------------------------
def mostrar_graficos(df):
    fig1 = px.histogram(df, x='Tipo de Animal', color='Tipo de Animal', title='Cantidad por tipo de animal')
    fig1.show()

    fig2 = px.histogram(df, x='Forma de egreso', color='Forma de egreso', title='Cantidad por forma de egreso')
    fig2.show()

    fig3 = px.histogram(df, x='Condición de ingreso', color='Condición de ingreso', title='Condición de ingreso')
    fig3.show()

# -------------------------------
# Interfaz Tkinter en modo Dark
# -------------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 Limpieza y Visualización de CSV")
        self.root.geometry("1000x700")

        # Fondo oscuro
        self.root.configure(bg="#2e2e2e")
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TFrame', background='#2e2e2e')
        style.configure('TLabel', background='#2e2e2e', foreground='white')
        style.configure('TButton', background='#444444', foreground='white')
        style.map('TButton', background=[('active','#555555')])
        style.configure('TCombobox', fieldbackground='#444444', background='#444444', foreground='white')
        style.map('TCombobox', fieldbackground=[('active','#555555')])

        self.df = None

        # Frame de controles arriba
        top = ttk.Frame(root)
        top.pack(side='top', fill='x', padx=10, pady=10)

        btn_cargar = ttk.Button(top, text="📂 Cargar CSV", command=self.cargar_csv)
        btn_cargar.pack(side='left', padx=5)

        self.combo_columna = ttk.Combobox(top, state="readonly", width=20)
        self.combo_columna.pack(side='left', padx=5)
        self.combo_columna.bind("<<ComboboxSelected>>", self.filtrar)

        self.combo_valor = ttk.Combobox(top, state="readonly", width=20)
        self.combo_valor.pack(side='left', padx=5)
        self.combo_valor.bind("<<ComboboxSelected>>", self.actualizar_tabla)

        btn_graficos = ttk.Button(top, text="📊 Gráficos", command=lambda: mostrar_graficos(self.df))
        btn_graficos.pack(side='left', padx=5)

        btn_guardar = ttk.Button(top, text="💾 Guardar limpio", command=self.guardar_csv)
        btn_guardar.pack(side='left', padx=5)

        # Frame para la tabla
        self.frame_tabla = ttk.Frame(root)
        self.frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)

    def cargar_csv(self):
        ruta = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not ruta:
            return
        try:
            df = pd.read_csv(ruta)
            self.df = limpiar_datos(df)
            self.mostrar_tabla(self.df)
            # Poblamos columna de filtros
            cols = list(self.df.columns)
            self.combo_columna['values'] = cols
            self.combo_columna.set("Filtrar por...")
            self.combo_valor.set("")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el CSV:\n{e}")

    def filtrar(self, _):
        col = self.combo_columna.get()
        if not col or self.df is None:
            return
        valores = sorted(self.df[col].dropna().unique())
        self.combo_valor['values'] = valores
        self.combo_valor.set("Seleccione valor...")

    def actualizar_tabla(self, _):
        col = self.combo_columna.get()
        val = self.combo_valor.get()
        if col and val and self.df is not None:
            filtered = self.df[self.df[col] == val]
            self.mostrar_tabla(filtered)

    def mostrar_tabla(self, df):
        for w in self.frame_tabla.winfo_children():
            w.destroy()
        tabla = Table(self.frame_tabla, dataframe=df, showtoolbar=True, showstatusbar=True)
        tabla.show()

    def guardar_csv(self):
        if self.df is None:
            return
        ruta = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")])
        if ruta:
            try:
                self.df.to_csv(ruta, index=False, encoding="utf-8-sig")
                messagebox.showinfo("✅ Guardado", "Archivo limpio guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error al guardar", str(e))

# -------------------------------
# Arrancar la aplicación
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
