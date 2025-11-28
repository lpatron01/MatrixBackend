# Documentation API - Module Réclamations

Ce module permet la gestion des réclamations étudiantes de manière sécurisée et optionnellement anonyme.

## Base URL
`/api/reclamations/`

## Authentification
Toutes les routes nécessitent un jeton d'authentification (Bearer Token).

## Modèles de Données

### Catégories
- `ADMINISTRATION`
- `ENSEIGNEMENT`
- `INFRASTRUCTURE`
- `HARCELEMENT`
- `AUTRES`

### Statuts
- `NOUVEAU` (Défaut)
- `EN_COURS`
- `RESOLU`
- `REJETE`

---

## Endpoints

### 1. Créer une réclamation
**POST** `/api/reclamations/`

Permet à un étudiant de soumettre une nouvelle réclamation.

**Corps de la requête (Multipart/Form-data si fichier inclus) :**
```json
{
  "category": "INFRASTRUCTURE",
  "description": "Le projecteur de la salle 101 ne fonctionne pas.",
  "is_anonymous": false,
  "file": (Fichier binaire optionnel)
}
```

### 2. Lister les réclamations
**GET** `/api/reclamations/`

- **Étudiants** : Retourne uniquement leurs propres réclamations.
- **Administrateurs** : Retourne toutes les réclamations.

**Filtres disponibles (Query Params) :**
- `?category=ADMINISTRATION`
- `?status=NOUVEAU`
- `?is_anonymous=true`

### 3. Obtenir les détails
**GET** `/api/reclamations/{uuid}/`

Retourne les détails complets d'une réclamation, y compris l'historique des modifications (visible pour l'étudiant et l'admin).

**Note** : L'ID utilisé dans l'URL est le `public_id` (UUID), pas l'ID interne.

### 4. Mettre à jour le statut (Admin uniquement)
**PATCH** `/api/reclamations/{uuid}/`

Permet à un administrateur de changer le statut ou d'ajouter un commentaire.

**Corps de la requête :**
```json
{
  "status": "EN_COURS",
  "comment": "Prise en charge par le service technique."
}
```
*L'ajout d'un commentaire ou le changement de statut crée automatiquement une entrée dans l'historique.*

### 5. Supprimer une réclamation
**DELETE** `/api/reclamations/{uuid}/`

- **Étudiants** : Peuvent supprimer leurs propres réclamations.
- **Administrateurs** : Peuvent supprimer n'importe quelle réclamation.

---

## Sécurité et Anonymat
- Si `is_anonymous` est `true`, le champ `student` sera retourné comme `null` dans les réponses API pour préserver l'anonymat visuel.
- Les IDs exposés sont des UUIDs aléatoires (`public_id`) pour empêcher l'énumération des réclamations.
