import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

# --- Fonctions de gestion des livres ---

def load_books():
    try:
        with open("data/livres.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_books(books):
    with open("data/livres.json", "w", encoding="utf-8") as file:
        json.dump(books, file, ensure_ascii=False, indent=4)

def refresh_listbox():
    listbox_books.delete(0, tk.END)
    for book in books:
        listbox_books.insert(tk.END, book["titre"])

def add_book():
    new_book = {
        "id": len(books) + 1,
        "titre": entry_title.get(),
        "auteur": entry_author.get(),
        "emplacement": entry_location.get(),
        "image": entry_image.get(),
        "mots_cles": [kw.strip() for kw in entry_keywords.get().split(",") if kw.strip()],
        "mention_speciale": var_special.get(),
        # Modifié ici pour éviter d'ajouter des avis vides
        "avis": [line.strip() for line in entry_reviews.get("1.0", tk.END).strip().split("\n") if line.strip()],
        "resume": entry_summary.get("1.0", tk.END).strip()
    }
    books.append(new_book)
    save_books(books)
    messagebox.showinfo("Succès", "Le livre a été ajouté avec succès.")
    clear_fields()
    refresh_listbox()


def search_book(event=None):
    search_term = entry_search.get().lower()
    results = [book for book in books if search_term in book["titre"].lower() 
               or any(search_term in kw.lower() for kw in book["mots_cles"])]
    listbox_books.delete(0, tk.END)
    if results:
        for book in results:
            listbox_books.insert(tk.END, book["titre"])
    else:
        messagebox.showwarning("Aucun résultat", "Aucun livre trouvé avec ce titre ou mot clé.")
def trouver_index(liste,element): #fonction de Mathurine
    for i in range(len(liste)):
        if liste[i]==element:
            return i
    return -1


def edit_book():
    selected_indices = listbox_books.curselection()
    if selected_indices :
        selected_index = selected_indices[0]
        selected_item = listbox_books.get(selected_index)
    if not selected_indices:
        messagebox.showwarning("Sélection requise", "Veuillez sélectionner un livre à modifier.")
        return 
    liste_titres=[books[i]["titre"] for i in range(len(books))]
    selected_index = trouver_index(liste_titres,selected_item)
    # Charge les infos du livre sélectionné dans le formulaire
    selected_book = books[selected_index]
    entry_title.delete(0, tk.END)
    entry_title.insert(0, selected_book["titre"])
    entry_author.delete(0, tk.END)
    entry_author.insert(0, selected_book["auteur"])
    entry_location.delete(0, tk.END)
    entry_location.insert(0, selected_book["emplacement"])
    entry_image.delete(0, tk.END)
    entry_image.insert(0, selected_book["image"])
    entry_keywords.delete(0, tk.END)
    entry_keywords.insert(0, ", ".join(selected_book["mots_cles"]))
    var_special.set(selected_book["mention_speciale"])
    entry_reviews.delete("1.0", tk.END)
    entry_reviews.insert("1.0", "\n".join(selected_book["avis"]))
    entry_summary.delete("1.0", tk.END)
    entry_summary.insert("1.0", selected_book["resume"])
    # Active le bouton de sauvegarde en liant la fonction de sauvegarde au livre sélectionné
    btn_save.config(state="normal", command=lambda: save_changes(selected_index))

def save_changes(index):
    books[index]["titre"] = entry_title.get()
    books[index]["auteur"] = entry_author.get()
    books[index]["emplacement"] = entry_location.get()
    books[index]["image"] = entry_image.get()
    books[index]["mots_cles"] = [kw.strip() for kw in entry_keywords.get().split(",") if kw.strip()]
    books[index]["mention_speciale"] = var_special.get()
    # Modifié ici pour éviter d'ajouter des avis vides
    books[index]["avis"] = [line.strip() for line in entry_reviews.get("1.0", tk.END).strip().split("\n") if line.strip()]
    books[index]["resume"] = entry_summary.get("1.0", tk.END).strip()
    save_books(books)
    messagebox.showinfo("Succès", "Les informations du livre ont été mises à jour.")
    clear_fields()
    btn_save.config(state="disabled")
    refresh_listbox()


def delete_book():
    selected_indices = listbox_books.curselection()
    if not selected_indices:
        messagebox.showwarning("Sélection requise", "Veuillez sélectionner un livre à supprimer.")
        return
    selected_index = selected_indices[0]
    selected_book = books[selected_index]
    response = messagebox.askyesno("Confirmer la suppression", f"Voulez-vous vraiment supprimer le livre '{selected_book['titre']}' ?")
    if response:
        del books[selected_index]
        save_books(books)
        messagebox.showinfo("Succès", "Le livre a été supprimé.")
        refresh_listbox()

def clear_fields():
    entry_title.delete(0, tk.END)
    entry_author.delete(0, tk.END)
    entry_location.delete(0, tk.END)
    entry_image.delete(0, tk.END)
    entry_keywords.delete(0, tk.END)
    entry_reviews.delete("1.0", tk.END)
    entry_summary.delete("1.0", tk.END)

def select_image():
    file_path = filedialog.askopenfilename(
        initialdir="images", title="Choisir une image",
        filetypes=(("Images", "*.jpg;*.jpeg;*.png"), ("Tous", "*.*"))
    )
    if file_path:
        # Ajouter le préfixe "images/" et récupérer le nom du fichier
        image_filename = "images/" + os.path.basename(file_path)
        entry_image.delete(0, tk.END)
        entry_image.insert(0, image_filename)

def on_mouse_wheel(event):
    if event.delta > 0:
        canvas.yview_scroll(-1, "units")
    else:
        canvas.yview_scroll(1, "units")

# --- Création de l'interface ---

root = tk.Tk()
root.title("Bibliothèque")
root.geometry("800x600")
root.resizable(True, True)

books = load_books()
search_results = []

# --- Partie haute : Recherche et liste des livres ---

top_frame = tk.Frame(root)
top_frame.pack(fill="both", expand=True, padx=10, pady=5)

label_search = tk.Label(top_frame, text="Rechercher un livre (titre ou mots clés)", font=("Arial", 12))
label_search.pack(fill='x', pady=5)
entry_search = tk.Entry(top_frame, font=("Arial", 12))
entry_search.pack(fill='x', pady=5)
entry_search.bind("<Return>", search_book)

btn_search = tk.Button(top_frame, text="Rechercher", command=search_book, font=("Arial", 12))
btn_search.pack(pady=5)

listbox_books = tk.Listbox(top_frame, font=("Arial", 12))
listbox_books.pack(fill="both", expand=True, pady=5)
refresh_listbox()

btn_edit = tk.Button(top_frame, text="Éditer le livre sélectionné", command=edit_book, font=("Arial", 12))
btn_edit.pack(pady=5)

btn_delete = tk.Button(top_frame, text="Supprimer le livre sélectionné", command=delete_book, font=("Arial", 12))
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
label_title = tk.Label(scrollable_frame, text="Titre", font=("Arial", 12))
label_title.pack(fill='x', pady=5)
entry_title = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_title.pack(fill='x', pady=5)

label_author = tk.Label(scrollable_frame, text="Auteur", font=("Arial", 12))
label_author.pack(fill='x', pady=5)
entry_author = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_author.pack(fill='x', pady=5)

label_location = tk.Label(scrollable_frame, text="Emplacement", font=("Arial", 12))
label_location.pack(fill='x', pady=5)
entry_location = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_location.pack(fill='x', pady=5)

label_image = tk.Label(scrollable_frame, text="Image", font=("Arial", 12))
label_image.pack(fill='x', pady=5)
entry_image = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_image.pack(fill='x', pady=5)
btn_select_image = tk.Button(scrollable_frame, text="Sélectionner une image", command=select_image, font=("Arial", 12))
btn_select_image.pack(pady=5)

label_keywords = tk.Label(scrollable_frame, text="Mots clés (séparés par des virgules)", font=("Arial", 12))
label_keywords.pack(fill='x', pady=5)
entry_keywords = tk.Entry(scrollable_frame, font=("Arial", 12))
entry_keywords.pack(fill='x', pady=5)

var_special = tk.BooleanVar()
checkbox_special = tk.Checkbutton(scrollable_frame, text="Mention spéciale", variable=var_special, font=("Arial", 12))
checkbox_special.pack(pady=5)

label_reviews = tk.Label(scrollable_frame, text="Avis (séparés par des retours à la ligne)", font=("Arial", 12))
label_reviews.pack(fill='x', pady=5)
entry_reviews = tk.Text(scrollable_frame, height=5, font=("Arial", 12))
entry_reviews.pack(fill='x', pady=5)

label_summary = tk.Label(scrollable_frame, text="Résumé", font=("Arial", 12))
label_summary.pack(fill='x', pady=5)
entry_summary = tk.Text(scrollable_frame, height=5, font=("Arial", 12))
entry_summary.pack(fill='x', pady=5)

btn_add = tk.Button(scrollable_frame, text="Ajouter un livre", command=add_book, font=("Arial", 12))
btn_add.pack(pady=5)
btn_save = tk.Button(scrollable_frame, text="Sauvegarder les modifications", state="disabled", font=("Arial", 12))
btn_save.pack(pady=5)

root.mainloop()
