// Fonction pour sélectionner une couleur
window.selectColor = (element) => {
    // Trouve le conteneur parent des pastilles
    const container = element.parentElement;
    // Retire la classe 'selected' de toutes les pastilles de ce produit
    container.querySelectorAll('.color-swatch').forEach(swatch => swatch.classList.remove('selected'));
    // Ajoute la classe 'selected' à la pastille cliquée
    element.classList.add('selected');
};

// Fonction pour gérer le clic sur "Commander"
window.passerCommande = (button) => {
    const card = button.closest('.produit');
    const nom = card.querySelector('h3').innerText;
    const prix = card.querySelector('.prix').innerText;
    
    const selectedSwatch = card.querySelector('.color-swatch.selected');
    let couleurChoisie = "Non spécifiée";

    // S'il y a des pastilles de couleur et qu'une est sélectionnée
    if (selectedSwatch) {
        couleurChoisie = selectedSwatch.dataset.color;
    } else if (card.querySelector('.color-swatches-container')) {
        // S'il y a des couleurs mais aucune n'est sélectionnée
        alert("Veuillez sélectionner une couleur avant de commander.");
        return; // On arrête la fonction ici
    }

    const subject = encodeURIComponent(`Commande : ${nom} (${couleurChoisie})`);
    const body = encodeURIComponent(`Bonjour,\n\nJe souhaite commander l'objet suivant :\n- Nom : ${nom}\n- Couleur : ${couleurChoisie}\n- Prix : ${prix}\n\nMerci de me contacter pour le paiement et la livraison.`);
    
    // Ouvre le client mail dans un nouvel onglet
    window.open(`mailto:leon.alleaumevoyard@gmail.com?subject=${subject}&body=${body}`, '_blank');
};


document.addEventListener('DOMContentLoaded', () => {
    const dataUrl = 'data/produits.json';
    const resultsContainer = document.getElementById('resultats');
    const searchInput = document.getElementById('searchBar');
    let allProducts = []; // Pour stocker les produits en mémoire

    // Affiche un message de chargement
    resultsContainer.innerHTML = '<p>Chargement des créations...</p>';
    
    // Fonction pour afficher une liste de produits donnée
    const displayProducts = (productsToDisplay) => {
        resultsContainer.innerHTML = '';

        if (productsToDisplay.length === 0) {
            resultsContainer.innerHTML = '<p>Aucune création trouvée.</p>';
            return;
        }

        // Ce dictionnaire fait le lien entre le nom de la couleur et son code CSS
        const colorMap = {
            "Blanc": "white", "Noir": "black", "Gris": "#808080", "Bleu": "#007bff",
            "Rouge": "#dc3545", "Vert": "#28a745", "Jaune": "#ffc107", "Violet": "#6f42c1",
            "Orange": "#fd7e14", "Rose": "#e83e8c", "Or": "#FFD700", "Argent": "#C0C0C0"
        };

        productsToDisplay.forEach(product => {
            let colorsHtml = '';
            // Vérifie si le produit a des couleurs définies
            if (product.couleurs_disponibles && product.couleurs_disponibles.length > 0) {
                const couleurs = product.couleurs_disponibles.split(',').map(c => c.trim());
                const swatches = couleurs.map((colorName, index) => {
                    const colorValue = colorMap[colorName] || colorName; // Utilise le nom si non trouvé
                    const isSelected = index === 0 ? 'selected' : ''; // Sélectionne la première par défaut
                    return `<div class="color-swatch ${isSelected}" 
                                 style="background-color: ${colorValue};" 
                                 data-color="${colorName}"
                                 onclick="selectColor(this)"></div>`;
                }).join('');

                colorsHtml = `
                    <div class="options-container">
                        <label>Couleur :</label>
                        <div class="color-swatches-container">${swatches}</div>
                    </div>
                `;
            }
            
            const productHtml = `
                <div class="produit">
                    ${product.image ? `<img src="${product.image}" alt="Image de ${product.nom}" class="produit-image">` : ''}
                    <div class="produit-contenu">
                        <h3>${product.nom}</h3>
                        <p class="description">${product.description}</p>
                        ${colorsHtml}

                        <div class="footer-details">
                            <span class="prix">${product.prix}</span>
                            <button onclick="window.passerCommande(this)" class="btn-commander">Commander</button>
                        </div>
                    </div>
                </div>
            `;
            resultsContainer.innerHTML += productHtml;
        });
    };

    fetch(dataUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur HTTP! Statut: ${response.status}`);
            }
            return response.json();
        })
        .then(products => {
            allProducts = products; // On sauvegarde la liste complète
            displayProducts(allProducts); // On affiche tout au début
        })
        .catch(error => {
            console.error('Erreur lors du chargement des produits:', error);
            resultsContainer.innerHTML = '<p style="color: red;">Impossible de charger les produits. Vérifiez la console pour les détails.</p>';
        });

    // Écouteur pour la barre de recherche
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const filteredProducts = allProducts.filter(product => 
            product.nom.toLowerCase().includes(searchTerm)
        );
        displayProducts(filteredProducts);
    });
});