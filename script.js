// Fonction pour sélectionner une couleur
window.selectColor = (element) => {
    // Trouve le conteneur parent des pastilles
    const container = element.parentElement;
    // Retire la classe 'selected' de toutes les pastilles de ce produit
    container.querySelectorAll('.color-swatch').forEach(swatch => swatch.classList.remove('selected'));
    // Ajoute la classe 'selected' à la pastille cliquée
    element.classList.add('selected');

    // Met à jour le texte de la couleur sélectionnée
    const colorName = element.dataset.color;
    const labelSpan = container.parentElement.querySelector('.selected-color-name');
    if (labelSpan) {
        labelSpan.textContent = colorName;
    }
};

// Fonction pour changer d'image (Carrousel)
window.changeImage = (button, direction) => {
    const container = button.parentElement;
    const track = container.querySelector('.slider-track');
    const count = parseInt(track.dataset.count);
    let currentIndex = parseInt(track.dataset.index);

    currentIndex += direction;
    if (currentIndex < 0) currentIndex = count - 1; 
    if (currentIndex >= count) currentIndex = 0; 

    // On déplace la piste vers la gauche (index * 100%)
    track.style.transform = `translateX(-${currentIndex * 100}%)`;
    track.dataset.index = currentIndex;
};

// Fonction pour déplier/replier les détails du produit
window.toggleDetails = (button) => {
    const wrapper = button.previousElementSibling; // La div .options-wrapper juste avant
    wrapper.classList.toggle('collapsed');
    
    if (wrapper.classList.contains('collapsed')) {
        button.innerText = "Voir plus +";
    } else {
        button.innerText = "Voir moins -";
    }
};

// Fonction pour gérer le clic sur "Commander"
window.passerCommande = (button) => {
    const card = button.closest('.produit');
    const nom = card.querySelector('h3').innerText;
    const prix = card.querySelector('.prix').innerText;
    
    // Récupération des choix de couleurs
    let detailsCouleurs = "";
    const optionGroups = card.querySelectorAll('.options-group');

    if (optionGroups.length > 0) {
        let missingSelection = false;
        const choices = [];

        optionGroups.forEach(group => {
            const partName = group.dataset.part; // "Général" ou "Tête", "Corps"...
            const selected = group.querySelector('.color-swatch.selected');
            if (selected) {
                choices.push(`${partName}: ${selected.dataset.color}`);
            } else {
                missingSelection = true;
            }
        });

        if (missingSelection) {
            alert("Veuillez sélectionner une couleur pour chaque partie.");
            return;
        }
        detailsCouleurs = choices.join(", ");
    }

    const subject = encodeURIComponent(`Commande : ${nom}`);
    const body = encodeURIComponent(`Bonjour,\n\nJe souhaite commander l'objet suivant :\n- Nom : ${nom}\n- Détails couleurs : ${detailsCouleurs}\n- Prix : ${prix}\n\nMerci de me contacter pour le paiement et la livraison.`);
    
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
            "Blanc": "#FFFFFF", "Vert simple": "#28CC00", "Vert Opale": "#00783C",
            "Vert clair": "#66FF00", "Rouge": "#FF0000", "Orange": "#FF5A00",
            "Violet": "#560079", "Noir": "#000000", "Jaune": "#EBFF00",
            "Bleu clair": "#0096E6", "Bronze": "#D6B31A", "Orange clair":"#eea411",
            "Vert bis":"#13bf57","Violet clair":"#a46ee5","Rouge bis":"#f84443", "Bleu clair bis":"#39aafd"
        };

        productsToDisplay.forEach(product => {
            let colorsHtml = '';
            // Vérifie si le produit a des couleurs définies
            if (product.couleurs_disponibles && product.couleurs_disponibles.length > 0) {
                const availableColors = product.couleurs_disponibles.split(',').map(c => c.trim());
                
                // Détermine les parties à colorier (soit défini dans parties_perso, soit "Couleur principale")
                let parts = ["Couleur"];
                if (product.parties_perso && product.parties_perso.trim() !== "") {
                    parts = product.parties_perso.split(',').map(p => p.trim());
                }

                // Génère le HTML pour chaque partie
                const selectorsHtml = parts.map(partName => {
                    const swatches = availableColors.map((colorName, index) => {
                        const colorValue = colorMap[colorName] || colorName;
                        const isSelected = index === 0 ? 'selected' : ''; // Par défaut le 1er est sélectionné
                        return `<div class="color-swatch ${isSelected}" 
                                     style="background-color: ${colorValue};" 
                                     data-color="${colorName}"
                                     onclick="selectColor(this)"></div>`;
                    }).join('');

                    return `
                        <div class="options-group" data-part="${partName}">
                            <label>${partName} : <span class="selected-color-name" style="color: #fff; font-weight: 600;">${availableColors[0]}</span></label>
                            <div class="color-swatches-container">${swatches}</div>
                        </div>
                    `;
                }).join('');

                colorsHtml = `<div class="options-container">${selectorsHtml}</div>`;
            }
            
            // Gestion de l'image ou du carrousel
            let imageHtml = '';
            if (product.image) {
                const imagesList = product.image.split(',').map(i => i.trim());
                if (imagesList.length > 1) {
                    // Création de toutes les balises images
                    const imagesTags = imagesList.map(src => `<img src="${src}" alt="Image de ${product.nom}" class="produit-image">`).join('');
                    imageHtml = `
                        <div class="produit-image-container">
                            <button class="nav-arrow left" onclick="changeImage(this, -1)">&#10094;</button>
                            <div class="slider-track" data-index="0" data-count="${imagesList.length}">
                                ${imagesTags}
                            </div>
                            <button class="nav-arrow right" onclick="changeImage(this, 1)">&#10095;</button>
                        </div>`;
                } else {
                    // On place aussi l'image unique dans le conteneur pour qu'elle respecte la hauteur de 220px
                    imageHtml = `
                        <div class="produit-image-container">
                            <img src="${imagesList[0]}" alt="Image de ${product.nom}" class="produit-image">
                        </div>`;
                }
            }

            const productHtml = `
                <div class="produit">
                    ${imageHtml}
                    <div class="produit-contenu">
                        <h3>${product.nom}</h3>
                        
                        <div class="produit-infos-completes collapsed">
                            <p class="description">${product.description}</p>
                            ${colorsHtml}
                        </div>
                        <button class="btn-toggle-details" onclick="toggleDetails(this)">Voir plus +</button>

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