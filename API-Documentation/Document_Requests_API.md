# Documentation API - Module Demandes de Document

Ce module permet la gestion des demandes de documents étudiants, offrant aux étudiants la possibilité de créer des demandes et aux administrateurs de les lister, visualiser et mettre à jour.

## Base URL
`/api/documents/`

## Authentification
Toutes les routes nécessitent un jeton d'authentification (Bearer Token).

---

## Endpoints

### 1. Créer une demande de document (Étudiant)
**POST** `/api/documents/demande`

Permet à un étudiant de soumettre une nouvelle demande de document.

**Corps de la requête (JSON) :**
```json
{
    "document_type": "<document_type>",
    "language": "<language>",
    "reception_type": "<reception_type>"
}
```
  - `document_type`: Type de document demandé (ex: "TRANSCRIPT", "CERTIFICATE_PRESENCE"). Se référer aux choix `DocumentType` dans `backend/document_requests/models.py`.
  - `language`: Langue souhaitée du document (ex: "ar" pour Arabe, "fr" pour Français).
  - `reception_type`: Mode de réception du document (ex: "ONLINE", "PERSONAL", "BOTH").

**Réponse (201 Created) :**
```json
{
    "id": "<uuid>",
    "student": <student_details>,
    "document_type": "<document_type>",
    "status": "NEW",
    "additional_info": null,
    "created_at": "<datetime>",
    "updated_at": "<datetime>",
    "history": [],
    "language": "<language>",
    "reception_type": "<reception_type>"
}
```

### 2. Lister les demandes de document (Étudiant)
**GET** `/api/documents/demandes`

Retourne une liste des demandes de documents effectuées par l'étudiant authentifié.

**Filtres disponibles (Query Params) :**
  - `document_type`: Filtrer par type de document.
  - `status`: Filtrer par statut (ex: "NEW", "IN_PROGRESS", "READY", "REJECTED").
  - `ordering`: Trier les résultats par des champs comme `created_at` ou `status`.

**Réponse (200 OK) :** Une liste d'objets de demande de document.

### 3. Lister les demandes de document (Admin)
**GET** `/api/documents/demandes/admin`

Retourne une liste de toutes les demandes de documents. Accessible uniquement par les administrateurs et le personnel.

**Filtres disponibles (Query Params) :** (Identique à la liste étudiant)

**Réponse (200 OK) :** Une liste de tous les objets de demande de document.

### 4. Détails de la demande de document (Consulter, Mettre à jour, Supprimer)
**GET**, **PUT**, **PATCH**, **DELETE** `/api/documents/demandes/{id}`

**Description :** 
    - `GET`: Récupère les détails d'une demande de document spécifique.
    - `PUT`/`PATCH`: Met à jour le statut ou ajoute un commentaire à une demande de document. Accessible uniquement par les administrateurs et le personnel.
    - `DELETE`: Supprime une demande de document. Accessible par l'étudiant qui l'a créée ou par les administrateurs/personnel.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Corps de la requête pour PUT/PATCH (Admin/Personnel uniquement) :**
```json
{
    "status": "<new_status>",
    "comment": "<optional_comment>"
}
```
  - `status`: Le nouveau statut de la demande de document (ex: "IN_PROGRESS", "READY", "REJECTED").
  - `comment`: Un commentaire facultatif à ajouter à l'historique de la demande de document.

**Réponse (200 OK pour GET/PUT/PATCH, 204 No Content pour DELETE) :**
  - `GET`: Un seul objet de demande de document.
  - `PUT`/`PATCH`: L'objet de demande de document mis à jour.

### 5. Valider une demande de document (Admin/Personnel uniquement)
**PUT** `/api/documents/demandes/{id}/terminer`

Met à jour le statut d'une demande de document à `READY` (Prêt). Seuls les administrateurs et le personnel peuvent effectuer cette action.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Réponse (200 OK) :** L'objet de demande de document mis à jour.

### 6. Rejeter une demande de document (Admin/Personnel uniquement)
**PUT** `/api/documents/demandes/{id}/rejeter`

Met à jour le statut d'une demande de document à `REJECTED` (Rejeté). Seuls les administrateurs et le personnel peuvent effectuer cette action.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Réponse (200 OK) :** L'objet de demande de document mis à jour.

### 7. Passer une demande de document en traitement (Admin/Personnel uniquement)
**PUT** `/api/documents/demandes/{id}/traiter`

Met à jour le statut d'une demande de document à `IN_PROGRESS` (En cours). Seuls les administrateurs et le personnel peuvent effectuer cette action.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Réponse (200 OK) :** L'objet de demande de document mis à jour.

### 8. Télécharger le fichier PDF d'une demande de document (Admin/Personnel uniquement)
**GET** `/api/documents/demandes/{id}/prefile`

Permet aux administrateurs et au personnel de télécharger le fichier PDF associé à une demande de document spécifique.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Réponse (200 OK) :** Le fichier PDF de la demande de document est retourné directement (content-type: `application/pdf`).
En cas d'absence de fichier PDF ou si l'utilisateur n'a pas les permissions, un statut 404 ou 403 sera retourné.

### 9. Télécharger le fichier PDF demandé par l'admin d'une demande de document (Admin/Personnel uniquement)
**PUT/PATCH** `/api/documents/demandes/{id}/file`

Permet aux administrateurs et au personnel de télécharger le fichier PDF demandé dans le champ `pdf_requested_file` pour une demande de document spécifique.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Corps de la requête (multipart/form-data) :**
```
Content-Disposition: form-data; name="pdf_requested_file"; filename="example.pdf"
Content-Type: application/pdf

<binary content of the PDF file>
```

**Réponse (200 OK) :** L'objet de demande de document mis à jour, incluant le chemin du fichier PDF téléversé.
```json
{
    "id": "<uuid>",
    "student": <student_details>,
    "document_type": "<document_type>",
    "status": "<status>",
    "additional_info": "<additional_info>",
    "created_at": "<datetime>",
    "updated_at": "<datetime>",
    "history": [],
    "language": "<language>",
    "reception_type": "<reception_type>",
    "pdf_file": "<path_to_original_pdf>",
    "pdf_requested_file": "<path_to_uploaded_pdf>"
}
```