import customtkinter as ctk
from logic import obtener_datos_remotos  # Asumimos que tienes tu lógica de red aquí
import time
import pyttsx3
import threading
from plyer import notification

# --- CONFIGURACIÓN DE VOZ (Opcional, pero profesional) ---
engine = pyttsx3.init()
engine.setProperty('rate', 180) # Velocidad de voz natural

def hablar(texto):
    def run():
        engine.say(texto)
        engine.runAndWait()
    threading.Thread(target=run, daemon=True).start()

class FocusMindOS(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- DATOS DEL SISTEMA ---
        self.xp = 850
        self.nivel = 2
        self.porcentaje = 0
        self.corriendo = False
        self.segundos = 25 * 60
        self.tarea_actual = "Standby"
        self.lista_tareas = []
        
        # --- CONFIGURACIÓN DE VENTANA (CALCADA DE LA IMAGEN) ---
        self.title("FocusMind OS Professional")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        
        # Paleta de Colores de Neón (Cian Neón, Negro Profundo)
        self.c_neon = "#00ffff" # Cian de la imagen (más brillante)
        self.c_bg = "#000000"   # Negro puro para contraste
        self.c_card = "#141414" # Negro sutil para paneles

        # --- DISEÑO DE INTERFAZ (GRID PRINCIPAL) ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Fila de tabla expandible

        # 1. HEADER (Delgado y Negro)
        self.header = ctk.CTkFrame(self, fg_color=self.c_bg, height=60, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        self.label_reloj = ctk.CTkLabel(self.header, text="22:03:54", font=("Arial", 28, "bold"), text_color="#fcc419")
        self.label_reloj.pack(side="left", padx=20)
        self.label_xp = ctk.CTkLabel(self.header, text=f"LVL {self.nivel} | XP {self.xp}", font=("Arial", 14, "bold"), text_color="white")
        self.label_xp.pack(side="right", padx=20)

        # 2. PANEL DE CONTROL (ENFOQUE, TIENDA Y GRÁFICA)
        self.dash_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dash_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        
        # Panel Enfoque (RECICLADO CON GLOW ROJO)
        self.card_enfoque = ctk.CTkFrame(self.dash_frame, fg_color=self.c_card, border_width=1, border_color="#ff4444", corner_radius=15)
        self.card_enfoque.pack(side="left", padx=10)
        ctk.CTkLabel(self.card_enfoque, text="ENFOQUE", text_color="#ff4444", font=("Arial", 9, "bold")).pack(pady=(10,0))
        self.label_crono = ctk.CTkLabel(self.card_enfoque, text="25:00", font=("Arial", 50, "bold"), text_color="#ff4444")
        self.label_crono.pack(padx=30, pady=5)
        self.btn_play = ctk.CTkButton(self.card_enfoque, text="▶", fg_color="#28a745", hover_color="#248f24", width=50, height=30, corner_radius=5, command=self.toggle_crono)
        self.btn_play.pack(pady=10)

        # Panel Tienda / Acciones
        self.card_tienda = ctk.CTkFrame(self.dash_frame, fg_color="#2b2e3b", corner_radius=15)
        self.card_tienda.pack(side="left", padx=10, fill="y")
        self.btn_up = ctk.CTkButton(self.card_tienda, text="UPGRADE LVL", fg_color="#3d4455", hover_color="#4d5565", height=35).pack(pady=(15, 10), padx=15)
        # NUEVO BOTÓN: LIMPIAR completados (con Glow sutil)
        self.btn_clear = ctk.CTkButton(self.card_tienda, text="🧹 LIMPIAR HECHOS", fg_color="#c62828", hover_color="#dc3545", border_width=1, border_color="#ff6666", height=35, command=self.limpiar)
        self.btn_clear.pack(pady=10, padx=15)

        # Panel Gráfica Eficiencia (Círculo de la imagen)
        self.card_graph = ctk.CTkFrame(self.dash_frame, fg_color=self.c_bg, corner_radius=15)
        self.card_graph.pack(side="left", padx=10, fill="y")
        self.canvas_circular = ctk.CTkCanvas(self.card_graph, width=100, height=100, bg=self.c_bg, highlightthickness=0)
        self.canvas_circular.pack(pady=10, padx=20)
        ctk.CTkLabel(self.card_graph, text="EFICIENCIA", font=("Arial", 8), text_color="gray").pack()

        # 3. TABLA DE TAREAS (CALCADA DE LA IMAGEN - FONDO BLANCO)
        self.tabla_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.tabla_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Encabezados sutiles
        self.head_box = ctk.CTkFrame(self.tabla_frame, fg_color="transparent")
        self.head_box.pack(fill="x", pady=10)
        headers = [("ID", 80), ("TAREA", 350), ("MINS", 120), ("ESTADO", 120)]
        for h, w in headers:
            ctk.CTkLabel(self.head_box, text=h, text_color="black", font=("Arial", 12, "bold"), width=w).pack(side="left")

        # Línea de división de ingeniería
        ctk.CTkFrame(self.tabla_frame, fg_color="black", height=2).pack(fill="x")

        self.scroll = ctk.CTkScrollableFrame(self.tabla_frame, fg_color="white", corner_radius=0)
        self.scroll.pack(fill="both", expand=True)

        # --- BOTÓN INFERIOR: FINALIZAR TAREA (¡GLOW CIAN ACTIVADO!) ---
        self.btn_finalizar = ctk.CTkButton(self, text="✔ FINALIZAR TAREA", font=("Arial", 22, "bold"), 
                                          fg_color=self.c_neon, text_color="black", height=80, corner_radius=0,
                                          # El hover_color crea el efecto de que el botón se "enciende" al pasar el mouse
                                          hover_color="#33ffff", border_width=2, border_color="white",
                                          command=self.completar_tarea)
        self.btn_finalizar.pack(fill="x", side="bottom")

        # INICIALIZACIÓN
        self.actualizar_tabla()
        self.actualizar_grafica()
        self.hilos_activos()
        
        # VOZ DE BIENVENIDA
        hablar("Panel de control Focus Mind activado.")

    def actualizar_grafica(self):
        # Dibuja el círculo cian neón calcado de la imagen
        self.canvas_circular.delete("all")
        self.canvas_circular.create_oval(10, 10, 90, 90, outline="#333", width=7) # Fondo oscuro
        
        total = len(self.lista_tareas)
        hechas = sum(1 for t in self.lista_tareas if t["estado"] == "HECHO")
        pct = (hechas / total) if total > 0 else 0
        extent = pct * -359.9
        self.canvas_circular.create_arc(10, 10, 90, 90, start=90, extent=extent, outline=self.c_neon, width=7, style="arc") # Neón

    def actualizar_tabla(self):
        # Datos calcados de la imagen para la primera carga
        if not self.lista_tareas:
            self.lista_tareas = [
                {"id": 1, "tarea": "Sistema Iniciado", "mins": "20:51", "estado": "HECHO"},
                {"id": 2, "tarea": "Ajuste de Gráfica", "mins": "22:10", "estado": "PENDIENTE"}
            ]

        for w in self.scroll.winfo_children(): w.destroy()
        
        for t in self.lista_tareas:
            fila = ctk.CTkFrame(self.scroll, fg_color="white")
            fila.pack(fill="x", pady=2)
            
            ctk.CTkLabel(fila, text=t["id"], text_color="#333", width=80).pack(side="left")
            ctk.CTkLabel(fila, text=t["tarea"], text_color="black", width=350, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(fila, text=t["mins"], text_color="#333", width=120).pack(side="left")
            
            color_st = "#28a745" if t["estado"] == "HECHO" else "#dc3545"
            ctk.CTkLabel(fila, text=t["estado"], text_color=color_st, font=("Arial", 11, "bold"), width=120).pack(side="left")

    def completar_tarea(self):
        # Lógica para finalizar la primera tarea pendiente
        for t in self.lista_tareas:
            if t["estado"] == "PENDIENTE":
                t["estado"] = "HECHO"
                self.xp += 50
                self.label_xp.configure(text=f"LVL {self.nivel} | XP {self.xp}")
                
                # VOZ AL FINALIZAR
                hablar("Protocolo finalizado.")
                
                self.actualizar_tabla()
                self.actualizar_grafica()
                break

    def limpiar(self):
        # Elimina tareas HECHAS
        self.lista_tareas = [t for t in self.lista_tareas if t["estado"] != "HECHO"]
        self.actualizar_tabla()
        self.actualizar_grafica()
        hablar("Limpieza de registros.")

    def toggle_crono(self):
        self.corriendo = not self.corriendo
        self.btn_play.configure(text="⏸" if self.corriendo else "▶")

    def hilos_activos(self):
        def loop():
            while True:
                # Tiempo real del header (se puede sincronizar con Render después)
                hora_actual = time.strftime("%H:%M:%S")
                self.label_reloj.configure(text=hora_actual)
                
                if self.corriendo and self.segundos > 0:
                    self.segundos -= 1
                    mins, segs = divmod(self.segundos, 60)
                    self.label_crono.configure(text=f"{mins:02d}:{segs:02d}")
                    if self.segundos == 0:
                        # NOTIFICACIÓN NATIVA
                        notification.notify(title="FocusMind OS", message="Tiempo agotado. Protocolo Standby.")
                        self.corriendo = False
                        hablar("Tiempo agotado.")
                time.sleep(1)
        threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app = FocusMindOS()
    app.mainloop()
