# 🏥 ChatBot Médical Malagasy

Chatbot médical conversationnel en langue malagasy, basé sur un modèle NLP (TF-IDF + SVM) entraîné sur un dataset de symptômes et traitements malgaches.

## ⚙️ Prérequis

Outil : Python 3.10+ https://python.org,  Node.js 18+  https://nodejs.org, MongoDB 6+ https://www.mongodb.com, Google Colab https://colab.research.google.com 

## 🤖 Étape 1 — Entraîner le modèle NLP (Google Colab)

> À faire **une seule fois**. Si quelqu'un te transmet déjà le dossier `ml_models/`, passe directement à l'étape 2.

1. Ouvre le fichier `Chatbot_Medical_Malagasy.ipynb` dans Google Colab
2. Upload le fichier `dataset_sante.csv` dans Colab quand demandé
3. Exécute toutes les cellules dans l'ordre (Cellule 1 → Cellule 14)
4. À la fin, la **Cellule 14** génère un fichier `chatbot_intelligent_NLP.zip`
5. Télécharge ce ZIP depuis le panneau **Fichiers** de Colab (icône dossier à gauche)
6. Dézippe-le et copie les 4 fichiers dans `flask/ml_models/` :

```
flask/utils/
├── pipeline.pkl            ← modèle SVM entraîné
├── encoder.pkl             ← encodeur des 16 catégories
├── retriever_tfidf.pkl     ← vectoriseur TF-IDF pour BM25
└── dataset_clean.csv       ← dataset nettoyé (reconstruit BM25)
```

---

## 🐍 Étape 2 — Backend Flask

### Installation

```bash
cd flask

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows :
.\venv\Scripts\activate
# macOS / Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration

Crée un fichier `.env` dans le dossier `flask/` :

```env
MONGO_URI=mongodb://localhost:27017/chatbot_medical
JWT_SECRET=une_cle_secrete_longue_de_32_caracteres_minimum
JWT_EXPIRATION=604800
CHATBOT_MODEL_DIR=ml_models
```

> ⚠️ `JWT_SECRET` doit faire **au moins 32 caractères** pour éviter l'avertissement de sécurité JWT.

### Lancement

```bash
# Depuis le dossier flask/ avec le venv activé
flask run --host=0.0.0.0 --port=5000
```

Tu dois voir :

```
✅ Index email créé
✅ Index conversations/messages créés
✅ ChatService prêt — 4598 docs, 16 classes
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

### Documentation API (Swagger)

```
http://127.0.0.1:5000/apidocs
```

---

## ⚛️ Étape 3 — Frontend React

### Installation

```bash
cd react

# Installer les dépendances Node
pnpm install
```

### Configuration

Vérifie que l'URL de l'API dans le frontend pointe vers le backend Flask.
Dans `src/utils/api.ts` (ou équivalent) :

```ts
const BASE_URL = "http://localhost:5000/api"
```

### Lancement

```bash
pnpm dev
```

L'application est accessible sur :

```
http://localhost:5173
```

---

## 🚀 Lancer le projet complet

Ouvre **deux terminaux** :

**Terminal 1 — Backend**
```bash
cd flask
.\venv\Scripts\activate      # Windows
flask run --host=0.0.0.0 --port=5000
```

**Terminal 2 — Frontend**
```bash
cd react
npm run dev
```

Puis ouvre `http://localhost:5173` dans ton navigateur.



## 🗄️ Base de données MongoDB

Trois collections sont créées automatiquement au démarrage :

**`users`**
```json
{
  "_id": "ObjectId",
  "name": "Heritiana",
  "email": "heritiana@gmail.com",
  "password": "hash bcrypt",
  "role": "user",
  "created_at": "datetime UTC+3",
  "updated_at": "datetime UTC+3"
}
```

**`conversations`**
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "nom_conversation": "Marary ny lohako",
  "created_at": "datetime UTC+3",
  "updated_at": "datetime UTC+3"
}
```

**`messages`**
```json
{
  "_id": "ObjectId",
  "conversation_id": "string",
  "texte": "marary ny lohako",
  "categorie": "aretin-doha",
  "label_fr": "aretin-doha",
  "icon": "🧠",
  "confidence": 97.4,
  "indicator": "green",
  "medicament1": "Aspirine 500mg : 2x/andro",
  "medicament2": "Ibuprofène 400mg",
  "astuce": "Aza mijery solosaina ela loatra",
  "generated": "Raha aretin-doha no mahazo anao...",
  "top3": [...],
  "alerte": null,
  "ood": false,
  "created_at": "datetime UTC+3"
}
```

---

## 🔐 Authentification

L'API utilise **JWT Bearer Token** :

```
Authorization: Bearer <token>
```

Le token est retourné lors du login et doit être inclus dans toutes les requêtes protégées.
Durée de validité : configurable via `JWT_EXPIRATION` dans `.env` (défaut : 604800 secondes = 7 jours).

---

## 🧪 Tester l'orchestration backend

```bash
cd flask
.\venv\Scripts\activate
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from services.conversation_services import ConversationService
    db = app.db
    user = db.users.find_one({})
    user_id = str(user['_id'])
    conv = ConversationService.create(db, user_id, 'Test')
    conv_id = conv['id']
    res = ConversationService.send(db, conv_id, user_id, 'marary ny lohako')
    print('SEND ->', res['type'], res.get('categorie'))
    ConversationService.delete(db, conv_id, user_id)
    print('OK tout fonctionne')
"
```

Résultat attendu :
```
✅ ChatService prêt — 4598 docs, 16 classes
SEND -> medical aretin-doha
OK tout fonctionne
```

---

## ❓ Problèmes fréquents

**`ChatService` en mode fallback**
→ Vérifie que `CHATBOT_MODEL_DIR` dans `.env` pointe vers le bon dossier contenant les 4 fichiers `.pkl` et `.csv`

**Erreur JWT `Signature has expired`**
→ Reconnecte-toi, le token a expiré. Augmente `JWT_EXPIRATION` dans `.env`

**Erreur JWT `InsecureKeyLengthWarning`**
→ `JWT_SECRET` trop court, mets au moins 32 caractères

**MongoDB ne démarre pas**
→ Lance MongoDB avant Flask : `mongod` dans un terminal séparé

**Frontend ne contacte pas le backend**
→ Vérifie que Flask tourne sur le port 5000 et que l'URL dans `api.ts` est correcte

---

## 👨💻 Auteur

Projet développé avec Flask, React, MongoDB et scikit-learn.
Modèle NLP entraîné sur Google Colab avec un dataset médical malagasy de 4598 exemples.

