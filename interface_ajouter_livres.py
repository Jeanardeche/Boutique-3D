import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sqlite3
import json
import shutil

# --- Configuration de la base de données ---
DB_PATH = "data/boutique.db"

def init_db():
    """Crée la base de données et la table si elles n'existent pas."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prix TEXT,
        image TEXT,
        description TEXT,
        couleurs_disponibles TEXT
        parties_perso TEXT
    )
    """)
    # Essaye d'ajouter la colonne pour les anciennes bases de données, ignore si elle existe déjà
    try:
        cursor.execute("ALTER TABLE produits ADD COLUMN couleurs_disponibles TEXT")
    except sqlite3.OperationalError:
        pass # La colonne existe déjà
    try:
        cursor.execute("ALTER TABLE produits ADD COLUMN parties_perso TEXT")
    except sqlite3.OperationalError:
        pass 

    # Création de la table de référence des couleurs
    cursor.execute("CREATE TABLE IF NOT EXISTS couleurs_ref (nom TEXT PRIMARY KEY, code_hex TEXT)")
    
    # On remplace la liste existante par la liste exacte demandée
    cursor.execute("DELETE FROM couleurs_ref")
    defaults = [
        ("Blanc", "#FFFFFF"), ("Vert simple", "#28CC00"), ("Vert Opale", "#00783C"),
        ("Vert clair", "#66FF00"), ("Rouge", "#FF0000"), ("Orange", "#FF5A00"),
        ("Violet", "#560079"), ("Noir", "#000000"), ("Jaune", "#EBFF00"),
        ("Bleu clair", "#0096E6"), ("Bronze", "#D6B31A")
    ]
    cursor.executemany("INSERT INTO couleurs_ref VALUES (?, ?)", defaults)

    conn.commit()
    conn.close()


def export_json():
    """Exporte la base de données en fichier JSON pour le site web."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produits")
    rows = cursor.fetchall()
    conn.close()
    
    products_list = [dict(row) for row in rows]
    try:
        with open("data/produits.json", "w", encoding="utf-8") as f:
            json.dump(products_list, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Erreur Export", f"Erreur lors de l'export JSON : {e}")

# --- Fonctions de gestion des livres ---

def load_products():
    """Charge les livres depuis la base de données SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par leur nom
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produits ORDER BY nom")
    rows = cursor.fetchall()
    conn.close()
    
    # Convertit les lignes de la base de données en une liste de dictionnaires
    return [dict(row) for row in rows]

def refresh_listbox():
    listbox_products.delete(0, tk.END)
    for product in products:
        listbox_products.insert(tk.END, f"{product['nom']} - {product['prix']}")

def add_product():
    nom = entry_nom.get()
    prix = entry_prix.get().replace("€", "").strip() + "€"
    
    # Gestion des images multiples
    main_img = entry_image_main.get()
    extra_imgs = entry_image_extras.get()
    image = main_img + ("," + extra_imgs if extra_imgs else "")
    
    description = entry_description.get("1.0", tk.END).strip()
    # Récupère les couleurs cochées
    couleurs = ",".join([color for color, var in color_vars.items() if var.get()])
    parties = entry_parties.get().strip()

    if not nom or not prix:
        messagebox.showwarning("Attention", "Le nom et le prix sont obligatoires.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produits (nom, prix, image, description, couleurs_disponibles, parties_perso)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nom, prix, image, description, couleurs, parties))
    conn.commit()
    conn.close()

    export_json()
    messagebox.showinfo("Succès", "L'objet 3D a été ajouté.")
    clear_fields()
    global products
    products = load_products()
    refresh_listbox()


def edit_product():
    selected_indices = listbox_products.curselection()
    if not selected_indices:
        messagebox.showwarning("Sélection requise", "Veuillez sélectionner un objet à modifier.")
        return

    # On utilise l'index de la sélection, c'est plus fiable que de parser le texte.
    selected_index = selected_indices[0]
    selected_product = products[selected_index]

    entry_nom.delete(0, tk.END)
    entry_nom.insert(0, selected_product["nom"])
    entry_prix.delete(0, tk.END)
    entry_prix.insert(0, selected_product["prix"].replace("€", ""))
    
    # Séparation image principale / images supplémentaires
    all_images = selected_product["image"].split(',')
    entry_image_main.delete(0, tk.END)
    entry_image_main.insert(0, all_images[0] if all_images else "")
    entry_image_extras.delete(0, tk.END)
    entry_image_extras.insert(0, ",".join(all_images[1:]) if len(all_images) > 1 else "")

    entry_description.delete("1.0", tk.END)
    entry_description.insert("1.0", selected_product["description"])
    
    # Cocher les couleurs existantes
    saved_colors = selected_product.get("couleurs_disponibles", "")
    # Charger les parties personnalisables
    entry_parties.delete(0, tk.END)
    entry_parties.insert(0, selected_product.get("parties_perso") or "")

    if saved_colors:
        saved_colors_list = [c.strip() for c in saved_colors.split(",")]
    else:
        saved_colors_list = []

    for color, var in color_vars.items():
        var.set(color in saved_colors_list)
    
    btn_save.config(state="normal", command=lambda: save_changes(selected_product['id']))

def save_changes(product_id):
    nom = entry_nom.get()
    prix = entry_prix.get().replace("€", "").strip() + "€"
    
    # Gestion des images multiples
    main_img = entry_image_main.get()
    extra_imgs = entry_image_extras.get()
    image = main_img + ("," + extra_imgs if extra_imgs else "")
    
    description = entry_description.get("1.0", tk.END).strip()
    # Récupère les couleurs cochées
    couleurs = ",".join([color for color, var in color_vars.items() if var.get()])
    parties = entry_parties.get().strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE produits 
        SET nom=?, prix=?, image=?, description=?, couleurs_disponibles=?, parties_perso=?
        WHERE id=?
    """, (nom, prix, image, description, couleurs, parties, product_id))
    conn.commit()
    conn.close()

    export_json()
    messagebox.showinfo("Succès", "Produit mis à jour.")
    clear_fields()
    btn_save.config(state="disabled")
    global products
    products = load_products()
    refresh_listbox()


def delete_product():
    global products
    selected_indices = listbox_products.curselection()
    if not selected_indices:
        messagebox.showwarning("Sélection requise", "Veuillez sélectionner un objet à supprimer.")
        return

    # On utilise l'index de la sélection pour plus de fiabilité.
    selected_index = selected_indices[0]
    selected_product = products[selected_index]
    response = messagebox.askyesno("Confirmer", f"Supprimer '{selected_product['nom']}' ?")
    if response:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produits WHERE id=?", (selected_product['id'],))
        conn.commit()
        conn.close()
        export_json()
        messagebox.showinfo("Succès", "Objet supprimé.")
        products = load_products()
        refresh_listbox()

def clear_fields():
    entry_nom.delete(0, tk.END)
    entry_prix.delete(0, tk.END)
    entry_image_main.delete(0, tk.END)
    entry_image_extras.delete(0, tk.END)
    entry_description.delete("1.0", tk.END)
    entry_parties.delete(0, tk.END)
    for var in color_vars.values():
        var.set(False)

def select_main_image():
    file_path = filedialog.askopenfilename(
        initialdir="images", title="Choisir l'image principale",
        filetypes=(("Images", "*.jpg;*.jpeg;*.png"), ("Tous", "*.*"))
    )
    if file_path:
        dest_dir = os.path.join(os.path.dirname(__file__), "images")
        os.makedirs(dest_dir, exist_ok=True)
        
        filename = os.path.basename(file_path).replace(",", "_")
        dest_path = os.path.join(dest_dir, filename)
        try:
            shutil.copy(file_path, dest_path)
        except shutil.SameFileError:
            pass
        
        entry_image_main.delete(0, tk.END)
        entry_image_main.insert(0, "images/" + filename)

def select_extra_images():
    file_paths = filedialog.askopenfilenames(
        initialdir="images", title="Choisir les images supplémentaires",
        filetypes=(("Images", "*.jpg;*.jpeg;*.png"), ("Tous", "*.*"))
    )
    if file_paths:
        # Créer le dossier images s'il n'existe pas
        dest_dir = os.path.join(os.path.dirname(__file__), "images")
        os.makedirs(dest_dir, exist_ok=True)

        saved_images = []
        for file_path in file_paths:
            # Copier l'image dans le dossier du projet
            filename = os.path.basename(file_path).replace(",", "_") # Sécurité anti-virgule
            dest_path = os.path.join(dest_dir, filename)
            try:
                shutil.copy(file_path, dest_path)
            except shutil.SameFileError:
                pass
            saved_images.append("images/" + filename)
        
        # On joint les chemins par une virgule pour les stocker dans le champ texte
        image_string = ",".join(saved_images)
        
        # Si des images sont déjà présentes, on ajoute à la suite, sinon on remplace
        current_extras = entry_image_extras.get()
        if current_extras:
             entry_image_extras.insert(tk.END, "," + image_string)
        else:
             entry_image_extras.insert(0, image_string)

def on_mouse_wheel(event):
    if event.delta > 0:
        canvas.yview_scroll(-1, "units")
    else:
        canvas.yview_scroll(1, "units")

def select_all_colors():
    for var in color_vars.values():
        var.set(True)

# --- Création de l'interface ---

root = tk.Tk()
root.title("Gestion Boutique 3D")
root.geometry("800x600")
root.resizable(True, True)

init_db()
products = load_products()

# --- Partie haute : Recherche et liste des livres ---

top_frame = tk.Frame(root)
top_frame.pack(fill="both", expand=True, padx=10, pady=5)

listbox_products = tk.Listbox(top_frame, font=("Arial", 12))
listbox_products.pack(fill="both", expand=True, pady=5)
refresh_listbox()

btn_edit = tk.Button(top_frame, text="Éditer sélection", command=edit_product, font=("Arial", 12))
btn_edit.pack(pady=5)

btn_delete = tk.Button(top_frame, text="Supprimer sélection", command=delete_product, font=("Arial", 12))
btn_delete.pack(pady=5)

# --- Partie basse : Formulaire dans une zone défilable ---

bottom_frame = tk.Frame(root)
bottom_frame.pack(fill="both", expand=True, padx=10, pady=5)

canvas = tk.Canvas(bottom_frame)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(bottom_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)

scrollable_frame = tk.Frame(canvas)
window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def on_configure(event):
    canvas.itemconfig(window_id, width=canvas.winfo_width())
    canvas.config(scrollregion=canvas.bbox("all"))
canvas.bind("<Configure>", on_configure)
canvas.bind_all("<MouseWheel>", on_mouse_wheel)

# Les autres composants du formulaire...
label_nom = tk.Label(scrollable_frame, text="Nom de l'objet", font=("Arial", 12))
label_nom.pack(fill='x', pady=5)
entry_nom = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_nom.pack(fill='x', pady=5)

label_prix = tk.Label(scrollable_frame, text="Prix (saisir le chiffre uniquement)", font=("Arial", 12))
label_prix.pack(fill='x', pady=5)
entry_prix = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_prix.pack(fill='x', pady=5)

# --- Section Image Principale ---
label_image_main = tk.Label(scrollable_frame, text="Image Principale (Image 1)", font=("Arial", 12))
label_image_main.pack(fill='x', pady=(10, 0))
entry_image_main = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_image_main.pack(fill='x', pady=5)
btn_select_main = tk.Button(scrollable_frame, text="Sélectionner Image 1", command=select_main_image, font=("Arial", 10))
btn_select_main.pack(pady=2)

# --- Section Images Supplémentaires ---
label_image_extras = tk.Label(scrollable_frame, text="Images Supplémentaires (Optionnel)", font=("Arial", 12))
label_image_extras.pack(fill='x', pady=(10, 0))
entry_image_extras = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_image_extras.pack(fill='x', pady=5)
btn_select_extras = tk.Button(scrollable_frame, text="Ajouter des images en plus", command=select_extra_images, font=("Arial", 10))
btn_select_extras.pack(pady=2)

label_description = tk.Label(scrollable_frame, text="Description", font=("Arial", 12))
label_description.pack(fill='x', pady=5)
entry_description = tk.Text(scrollable_frame, height=5, font=("Arial", 12))
entry_description.pack(fill='x', pady=5)

btn_add = tk.Button(scrollable_frame, text="Ajouter l'objet", command=add_product, font=("Arial", 12))
btn_add.pack(pady=5)

# --- Section Couleurs ---
label_couleurs_titre = tk.Label(scrollable_frame, text="--- Personnalisation ---", font=("Arial", 12, "bold"))
label_couleurs_titre.pack(fill='x', pady=(20, 5))

# 1. Liste des couleurs dispo
label_couleurs = tk.Label(scrollable_frame, text="Couleurs disponibles", font=("Arial", 12, "bold"))
label_couleurs.pack(fill='x', pady=(10, 5))

frame_couleurs_container = tk.Frame(scrollable_frame)
frame_couleurs_container.pack(fill='x', pady=5)

color_vars = {} # Dictionnaire pour stocker les variables des checkboxes

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT nom FROM couleurs_ref")
couleurs_db = [r[0] for r in cursor.fetchall()]
conn.close()

for i, color in enumerate(couleurs_db):
    var = tk.BooleanVar()
    color_vars[color] = var
    cb = tk.Checkbutton(frame_couleurs_container, text=color, variable=var, font=("Arial", 10))
    cb.grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)

btn_select_all = tk.Button(scrollable_frame, text="Tout sélectionner", command=select_all_colors, font=("Arial", 9))
btn_select_all.pack(pady=2)

# 2. Définition des parties (Multi-couleurs)
label_parties = tk.Label(scrollable_frame, text="Parties personnalisables (séparées par des virgules)", font=("Arial", 11, "bold"))
label_parties.pack(fill='x', pady=(15, 0))
label_parties_info = tk.Label(scrollable_frame, text="Ex: Tête, Corps, Ailes (Laisser vide si couleur unique)", font=("Arial", 9), fg="gray")
label_parties_info.pack(fill='x')
entry_parties = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_parties.pack(fill='x', pady=5)

btn_save = tk.Button(scrollable_frame, text="Sauvegarder les modifications", state="disabled", font=("Arial", 12))
btn_save.pack(pady=5)

root.mainloop()
