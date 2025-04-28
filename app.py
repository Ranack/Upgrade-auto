import streamlit as st
import os
from PIL import Image, ImageEnhance, ImageOps

# Chemins vers les dossiers contenant les images, les masques et les prédictions baseline, relatifs à l'emplacement de app.py
image_folder = 'Image/Photos'
mask_folder = 'Image/Verif'
baseline_folder = 'Image/Prédictions/Baseline'
c1_folder = 'Image/Prédictions/C1'
c2_folder = 'Image/Prédictions/C2'
mc1_folder = 'Image/Prédictions/MC1'
mc2_folder = 'Image/Prédictions/MC2'

# Lister les fichiers dans le dossier des images
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

# Filtrer les images pour n'inclure que celles pour lesquelles une prédiction baseline est disponible
filtered_image_files = []
for image_file in image_files:
    parts = image_file.split('_')
    city = parts[0]
    first_number = parts[1]
    second_number = parts[2]

    # Construire le nom de l'image de prédiction baseline
    baseline_image_name = f"{city}_{first_number}_{second_number}.png"
    baseline_image_path = os.path.join(baseline_folder, baseline_image_name)

    # Vérifier si l'image de prédiction baseline existe
    if os.path.exists(baseline_image_path):
        filtered_image_files.append(image_file)

# Vérifier si des images filtrées sont présentes
if not filtered_image_files:
    st.sidebar.write("Aucune image avec prédiction baseline trouvée dans le dossier spécifié.")
else:
    # Créer un menu déroulant dans la barre latérale avec les noms des images filtrées
    selected_image = st.sidebar.selectbox("Sélectionnez une image à afficher", filtered_image_files)

# Options d'accessibilité dans la barre latérale
st.sidebar.title("Options d'accessibilité")
zoom_level = st.sidebar.slider("Zoom", 50, 200, 100, 10)  # Utiliser des pourcentages pour le zoom
contrast_level = st.sidebar.slider("Contraste", 0.1, 2.0, 1.0)  # Ajouter le contrôle du contraste
light_theme = st.sidebar.checkbox("Thème clair")
monochrome = st.sidebar.checkbox("Monochrome")
invert_colors = st.sidebar.checkbox("Inverser les couleurs")
large_text = st.sidebar.checkbox("Augmenter la taille du texte")

# Ajouter des informations sur la navigation au clavier
st.sidebar.markdown("""
### Navigation au clavier
- **Tab** : Naviguer vers l'élément interactif suivant.
- **Shift + Tab** : Naviguer vers l'élément interactif précédent.
- **Enter** ou **Espace** : Activer l'élément interactif sélectionné.
""")

# Appliquer le thème clair ou sombre
if light_theme:
    bg_color = "#FFFFFF"
    text_color = "#000000"
else:
    bg_color = "#1E1E1E"
    text_color = "#FFFFFF"

# Appliquer les styles CSS pour le thème et la taille du texte
st.markdown(
    f"""
    <style>
    body {{
        background-color: {bg_color};
        color: {text_color};
        font-size: {'18px' if large_text else '14px'};
    }}
    .sidebar .sidebar-content {{
        background-color: {bg_color};
    }}
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
        color: {text_color};
    }}
    .stMarkdown p, .stMarkdown ul, .stMarkdown ol, .stMarkdown blockquote {{
        color: {text_color};
    }}
    .stButton>button {{
        background-color: {text_color};
        color: {bg_color};
    }}
    .stTextInput>div>input, .stSelectbox>div>select {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .stSlider>div>div>div>div {{
        background-color: {text_color};
    }}
    .stSlider>div>div>div>div>div {{
        background-color: {bg_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Fonction pour appliquer les options d'accessibilité à une image
def apply_accessibility_options(image, contrast_level, zoom_level, monochrome, invert_colors):
    if monochrome:
        image = ImageOps.grayscale(image)
    if invert_colors:
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        image = ImageOps.invert(image)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast_level)
    width, height = image.size
    image = image.resize((int(width * zoom_level / 100), int(height * zoom_level / 100)), Image.Resampling.LANCZOS)
    return image

# Créer deux colonnes pour afficher l'image d'origine et le masque côte à côte
col1, col2 = st.columns(2)

# Afficher l'image d'origine dans la première colonne
with col1:
    st.write("### Image d'origine")
    image_path = os.path.join(image_folder, selected_image)
    image = Image.open(image_path)
    image = apply_accessibility_options(image, contrast_level, zoom_level, monochrome, invert_colors)
    st.image(image, caption=selected_image, use_container_width=True)

# Construire le nom du masque correspondant
mask_image_name = selected_image.replace('_leftImg8bit.png', '_gtFine_color.png')
mask_image_path = os.path.join(mask_folder, mask_image_name)

# Afficher le masque dans la deuxième colonne si le fichier existe
with col2:
    if os.path.exists(mask_image_path):
        st.write("### Masque")
        mask_image = Image.open(mask_image_path)
        mask_image = apply_accessibility_options(mask_image, contrast_level, zoom_level, monochrome, invert_colors)
        st.image(mask_image, caption=mask_image_name, use_container_width=True)
    else:
        st.write("Masque non trouvé pour cette image.")

# Extraire les parties nécessaires du nom de l'image d'origine
parts = selected_image.split('_')
city = parts[0]
first_number = parts[1]
second_number = parts[2]

# Construire le nom de l'image de prédiction baseline
baseline_image_name = f"{city}_{first_number}_{second_number}.png"
baseline_image_path = os.path.join(baseline_folder, baseline_image_name)

# Afficher l'image de prédiction baseline centrée sur une seule colonne
st.write("### Prédiction baseline")
baseline_image = Image.open(baseline_image_path)
baseline_image = apply_accessibility_options(baseline_image, contrast_level, zoom_level, monochrome, invert_colors)
st.image(baseline_image, caption=baseline_image_name, use_container_width=True)

# Créer deux nouvelles colonnes pour afficher les images Modèle C1 et Modèle C2
col3, col4 = st.columns(2)

# Construire le nom de l'image Modèle C1
c1_image_name = f"{city}_{first_number}_{second_number}_leftImg8bit_vltseg.png"
c1_image_path = os.path.join(c1_folder, c1_image_name)

# Afficher l'image Modèle C1 dans la première colonne si le fichier existe
with col3:
    if os.path.exists(c1_image_path):
        st.write("### Modèle C1")
        c1_image = Image.open(c1_image_path)
        c1_image = apply_accessibility_options(c1_image, contrast_level, zoom_level, monochrome, invert_colors)
        st.image(c1_image, caption=c1_image_name, use_container_width=True)
    else:
        st.write("Modèle C1 non trouvé pour cette image.")

# Construire le nom de l'image Modèle C2
c2_image_name = f"{city}_{first_number}_{second_number}_leftImg8bit_vltseg.png"
c2_image_path = os.path.join(c2_folder, c2_image_name)

# Afficher l'image Modèle C2 dans la deuxième colonne si le fichier existe
with col4:
    if os.path.exists(c2_image_path):
        st.write("### Modèle C2")
        c2_image = Image.open(c2_image_path)
        c2_image = apply_accessibility_options(c2_image, contrast_level, zoom_level, monochrome, invert_colors)
        st.image(c2_image, caption=c2_image_name, use_container_width=True)
    else:
        st.write("Modèle C2 non trouvé pour cette image.")

# Créer deux nouvelles colonnes pour afficher les images Modèle MC1 et Modèle MC2
col5, col6 = st.columns(2)

# Construire le nom de l'image Modèle MC1
mc1_image_name = f"{city}_{first_number}_{second_number}_leftImg8bit_vltseg.png"
mc1_image_path = os.path.join(mc1_folder, mc1_image_name)

# Afficher l'image Modèle MC1 dans la première colonne si le fichier existe
with col5:
    if os.path.exists(mc1_image_path):
        st.write("### Modèle MC1")
        mc1_image = Image.open(mc1_image_path)
        mc1_image = apply_accessibility_options(mc1_image, contrast_level, zoom_level, monochrome, invert_colors)
        st.image(mc1_image, caption=mc1_image_name, use_container_width=True)
    else:
        st.write("Modèle MC1 non trouvé pour cette image.")

# Construire le nom de l'image Modèle MC2
mc2_image_name = f"{city}_{first_number}_{second_number}_leftImg8bit_vltseg.png"
mc2_image_path = os.path.join(mc2_folder, mc2_image_name)

# Afficher l'image Modèle MC2 dans la deuxième colonne si le fichier existe
with col6:
    if os.path.exists(mc2_image_path):
        st.write("### Modèle MC2")
        mc2_image = Image.open(mc2_image_path)
        mc2_image = apply_accessibility_options(mc2_image, contrast_level, zoom_level, monochrome, invert_colors)
        st.image(mc2_image, caption=mc2_image_name, use_container_width=True)
    else:
        st.write("Modèle MC2 non trouvé pour cette image.")
