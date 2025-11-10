"""
==============================================================
🎯 Script : predict.py — Prédiction simple avec modèle XGBoost
==============================================================

🧠 Description :
----------------
Ce script charge le modèle XGBoost et l’encodeur entraînés
puis effectue une prédiction sur une ligne aléatoire du jeu
de validation (data/processed/X_val.npz).

📦 Entrées :
------------
- data/processed/X_val.npz             → Données sparse de validation
- data/models/xgb_fusion.json          → Modèle XGBoost entraîné
- data/models/label_encoder.joblib     → Encodeur des labels

📊 Sorties :
------------
Affiche dans la console :
  • l’index de la ligne choisie
  • le code produit prédit
  • le libellé de catégorie correspondant

🔁 Exemple d’exécution :
------------------------
$ python src/api/predict.py

🚀 Utilisation typique :
------------------------
Ce script peut être utilisé :
  • pour tester rapidement un modèle entraîné
  • ou comme fonction d’inférence dans une future API FastAPI
==============================================================
"""


import os
import numpy as np
import joblib
import xgboost as xgb
from scipy import sparse

# === Dictionnaire des catégories ===
cat_map = {
    10:  "Livres et ouvrages culturels",
    40:  "Jeux vidéo et accessoires",
    50:  "Accessoires gaming",
    60:  "Consoles rétro",
    1140:"Figurines Pop & licences geek",
    1160:"Cartes à collectionner",
    1180:"Jeux de figurines & wargames",
    1280:"Jouets enfants & bébés",
    1281:"Jeux et loisirs enfants",
    1300:"Drones et modèles réduits",
    1301:"Chaussettes & accessoires enfants",
    1302:"Jouets divers & loisirs créatifs",
    1320:"Puériculture & équipement bébé",
    1560:"Mobilier & articles de maison",
    1920:"Linge de maison & décoration textile",
    1940:"Alimentation & boissons",
    2060:"Décoration & accessoires saisonniers",
    2220:"Accessoires pour animaux",
    2280:"Magazines & journaux anciens",
    2403:"Livres, mangas & partitions",
    2462:"Lots jeux vidéo et consoles",
    2522:"Fournitures de papeterie",
    2582:"Mobilier et accessoires de jardin",
    2583:"Accessoires pour piscines et spas",
    2585:"Outils et équipements de jardinage",
    2705:"Essais & livres d’histoire",
    2905:"Jeux PC à télécharger & éditions spéciales",
}


def predict_one():
    """Prédit une seule ligne aléatoire de X_val.npz"""
    print("📦 Chargement des artefacts...")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    X_path = os.path.join(base_dir, "data/processed/X_val.npz")
    model_path = os.path.join(base_dir, "data/models/xgb_fusion.json")
    encoder_path = os.path.join(base_dir, "data/models/label_encoder.joblib")

    # Chargement du modèle et des données
    X = sparse.load_npz(X_path)
    bst = xgb.Booster()
    bst.load_model(model_path)
    encoder = joblib.load(encoder_path)
    print("✅ Modèles et données chargés.")

    # Sélection aléatoire d'une ligne
    row_index = np.random.randint(0, X.shape[0])
    x_row = X.getrow(row_index)
    dtest = xgb.DMatrix(x_row)

    # Prédiction
    proba = bst.predict(dtest)[0]
    pred_id = np.argmax(proba)
    prdtypecode = encoder.inverse_transform([pred_id])[0]

    category = cat_map.get(int(prdtypecode), "Non défini")
    print(f"\n🎯 Ligne {row_index} — Code produit prédit : {prdtypecode}")
    print(f"🪄 Catégorie : {category}\n")

    return {
        "row_index": int(row_index),
        "predicted_code": int(prdtypecode),
        "category": category,
    }


if __name__ == "__main__":
    result = predict_one()
    print(result)
