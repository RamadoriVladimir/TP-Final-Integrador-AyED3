
import os
import ctypes
from ctypes import c_int, c_char_p, c_char, create_string_buffer
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DLL_PATH = os.path.join(SCRIPT_DIR, "DijkstraDLL.dll")

try:
    d = ctypes.CDLL(DLL_PATH)
except OSError as e:
    print(f"Error al cargar la DLL: {e}")
    print(f"Ruta esperada: {DLL_PATH}")
    exit(1)

# Declarar firmas de funciones exportadas por la DLL
d.create_graph.argtypes = [c_int]
d.create_graph.restype = None

d.add_edge.argtypes = [c_int, c_int, c_int]
d.add_edge.restype = None

d.run_dijkstra.argtypes = [c_int]
d.run_dijkstra.restype = None

d.get_distance.argtypes = [c_int]
d.get_distance.restype = c_int

d.get_path_csv.argtypes = [c_int, ctypes.c_char_p, c_int]
d.get_path_csv.restype = c_int

d.clear_graph.argtypes = []
d.clear_graph.restype = None

# Crear ventana principal
root = tk.Tk()
root.title("Dijkstra - GUI (ctypes DLL)")
root.geometry("800x600")

frm = ttk.Frame(root, padding=10)
frm.pack(fill=tk.BOTH, expand=True)

# Campo: Número de vértices
ttk.Label(frm, text="Número de vértices (V):").grid(row=0, column=0, sticky="w")
entry_V = ttk.Entry(frm, width=10)
entry_V.grid(row=0, column=1, sticky="w")
entry_V.insert(0, "5")

# Campo: Aristas (multilinea)
ttk.Label(frm, text="Aristas (una por línea: u v peso):").grid(row=1, column=0, columnspan=2, sticky="w")
text_edges = scrolledtext.ScrolledText(frm, width=40, height=12)
text_edges.grid(row=2, column=0, columnspan=2, sticky="nsew")
# Ejemplo por defecto (mismo que en el código original C++)
text_edges.insert("1.0", 
    "1 2 7\n"
    "1 4 2\n"
    "2 3 1\n"
    "2 4 2\n"
    "3 5 4\n"
    "4 2 3\n"
    "4 3 8\n"
    "4 5 5\n"
    "5 3 5\n"
)

# Campo: Vértice inicial
ttk.Label(frm, text="Vértice inicial:").grid(row=0, column=2, sticky="w")
entry_ini = ttk.Entry(frm, width=10)
entry_ini.grid(row=0, column=3, sticky="w")
entry_ini.insert(0, "1")

# Campo: Vértice destino
ttk.Label(frm, text="Vértice destino (para camino):").grid(row=1, column=2, sticky="w")
entry_dest = ttk.Entry(frm, width=10)
entry_dest.grid(row=1, column=3, sticky="w")
entry_dest.insert(0, "5")

# Área de salida
ttk.Label(frm, text="Salida:").grid(row=3, column=0, sticky="w")
text_out = scrolledtext.ScrolledText(frm, width=80, height=16)
text_out.grid(row=4, column=0, columnspan=4, sticky="nsew")

def run():
    text_out.delete("1.0", tk.END)
    
    try:
        V = int(entry_V.get())
        inicial = int(entry_ini.get())
        destino = int(entry_dest.get())
    except ValueError:
        messagebox.showerror("Error", "V, inicial y destino deben ser enteros.")
        return
    
    if V < 1 or V >= 10005:
        messagebox.showerror("Error", f"V debe estar entre 1 y 10004. Valor ingresado: {V}")
        return
    
    if inicial < 1 or inicial > V:
        messagebox.showerror("Error", f"Vértice inicial debe estar entre 1 y {V}")
        return
    
    if destino < 1 or destino > V:
        messagebox.showerror("Error", f"Vértice destino debe estar entre 1 y {V}")
        return

    d.clear_graph()
    d.create_graph(V)

    raw = text_edges.get("1.0", "end").strip()
    if raw == "":
        messagebox.showwarning("Aviso", "No hay aristas definidas.")
        return
    
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    edge_count = 0
    for ln in lines:
        parts = ln.split()
        if len(parts) < 3:
            messagebox.showerror("Error", f"Línea inválida: '{ln}'. Debe ser: u v peso")
            return
        try:
            u = int(parts[0])
            v = int(parts[1])
            w = int(parts[2])
        except ValueError:
            messagebox.showerror("Error", f"Línea inválida: '{ln}'. Valores no enteros.")
            return
        
        if u < 1 or u > V or v < 1 or v > V:
            messagebox.showerror("Error", f"Arista inválida: {u} {v} {w}. Vértices deben estar entre 1 y {V}")
            return
        
        d.add_edge(u, v, w)
        edge_count += 1

    d.run_dijkstra(inicial)

    text_out.insert(tk.END, f"═══════════════════════════════════════════════════\n")
    text_out.insert(tk.END, f"Grafo: {V} vértices, {edge_count} aristas\n")
    text_out.insert(tk.END, f"═══════════════════════════════════════════════════\n\n")
    text_out.insert(tk.END, f"Distancias más cortas desde vértice {inicial}:\n")
    text_out.insert(tk.END, f"───────────────────────────────────────────────────\n")
    
    for node in range(1, V+1):
        dist = d.get_distance(node)
        if dist < 0:
            text_out.insert(tk.END, f"  Vértice {node:3d} → INALCANZABLE\n")
        else:
            text_out.insert(tk.END, f"  Vértice {node:3d} → distancia = {dist}\n")

    # Obtener e imprimir camino al destino
    text_out.insert(tk.END, f"\n───────────────────────────────────────────────────\n")
    BUF_SIZE = 1024
    buf = create_string_buffer(BUF_SIZE)
    res = d.get_path_csv(destino, buf, BUF_SIZE)
    
    if res != 0:
        text_out.insert(tk.END, f"No se pudo obtener el camino para vértice {destino}\n")
        text_out.insert(tk.END, f"(Buffer pequeño o destino inválido)\n")
    else:
        path_str = buf.value.decode('utf-8')
        if path_str == "UNREACHABLE":
            text_out.insert(tk.END, f"Camino al vértice {destino}: INALCANZABLE\n")
        else:
            text_out.insert(tk.END, f"Camino más corto al vértice {destino}:\n")
            text_out.insert(tk.END, f"  {path_str}\n")
    
    text_out.insert(tk.END, f"═══════════════════════════════════════════════════\n")

btn_run = ttk.Button(frm, text="Ejecutar Dijkstra", command=run)
btn_run.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=5, pady=5)

# Configurar expansión de grid
frm.columnconfigure(0, weight=1)
frm.columnconfigure(1, weight=0)
frm.columnconfigure(2, weight=1)
frm.columnconfigure(3, weight=0)
frm.rowconfigure(4, weight=1)

root.mainloop()