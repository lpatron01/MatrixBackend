# Documentation API - Module Demandes de Document

Ce module permet la gestion des demandes de documents étudiants, offrant aux étudiants la possibilité de créer des demandes et aux administrateurs de les lister, visualiser et mettre à jour.

## Base URL
`/api/documents/`

## Authentification
Toutes les routes nécessitent un jeton d'authentification (Bearer Token).

## Types de données

### Statuts de demande
- `NEW`: Nouveau (statut initial)
- `IN_PROGRESS`: En cours de traitement
- `READY`: Prêt (terminé)
- `REJECTED`: Rejeté
- `DELIVERED`: Livré

### Types de documents
- `TRANSCRIPT`: Relevé de notes
- `CERTIFICATE_PRESENCE`: Attestation de présence
- `CERTIFICATE_SUCCESS`: Attestation de réussite
- `CERTIFICATE_INSCRIPTION`: Attestation d'inscription
- `DIPLOMA`: Diplôme
- `OTHER`: Autre

### Langues
- `ar`: Arabe
- `fr`: Français

### Types de réception
- `ONLINE`: En ligne
- `PERSONAL`: En personne
- `BOTH`: Les deux

### Statuts d'approbation (pour les demandes d'attestation de présence)
- `PENDING`: En attente d'approbation
- `APPROVED`: Approuvé par l'enseignant
- `REJECTED`: Rejeté par l'enseignant

## Historique des changements

Toutes les modifications de statut sont automatiquement tracées dans le champ `history`. Chaque entrée contient :
- `changed_by`: Utilisateur qui a effectué le changement
- `old_status`: Statut précédent
- `new_status`: Nouveau statut
- `comment`: Commentaire optionnel
- `date`: Date et heure du changement

---

## Endpoints

### 1. Créer une demande de document (Étudiant)
**POST** `/api/documents/demandes/`

Permet à un étudiant de soumettre une nouvelle demande de document.

**Corps de la requête (JSON) :**
```json
{
    "document_type": "<document_type>",
    "language": "<language>",
    "reception_type": "<reception_type>",
    "academic_year": "<academic_year>"
}
```
  - `document_type`: Type de document demandé (ex: "TRANSCRIPT", "CERTIFICATE_PRESENCE", "CERTIFICATE_INSCRIPTION", "DIPLOMA", "OTHER"). Se référer aux choix `DocumentType` dans `backend/document_requests/models.py`.
  - `language`: Langue souhaitée du document (ex: "ar" pour Arabe, "fr" pour Français).
  - `reception_type`: Mode de réception du document (ex: "ONLINE", "PERSONAL", "BOTH").
  - `academic_year`: Année académique au format "YYYY-YYYY" (ex: "2023-2024").

**Réponse (201 Created) :**
```json
{
    "id": "<uuid>",
    "student": {
        "id": <user_id>,
        "username": "<username>",
        "email": "<email>",
        "first_name": "<first_name>",
        "last_name": "<last_name>",
        "first_name_arabic": "<first_name_arabic>",
        "last_name_arabic": "<last_name_arabic>"
    },
    "document_type": "<document_type>",
    "status": "NEW",
    "additional_info": null,
    "academic_year": "<academic_year>",
    "created_at": "<datetime>",
    "updated_at": "<datetime>",
    "history": [],
    "language": "<language>",
    "reception_type": "<reception_type>",
    "pdf_file": "<path_to_generated_pdf>",
    "pdf_requested_file": null
}
```

**Notes :**
- Un fichier PDF est automatiquement généré et attaché à la demande lors de sa création.
- Le champ `history` contient l'historique des changements de statut (initialement vide).

### 2. Lister les demandes de document
**GET** `/api/documents/demandes/`

Retourne une liste des demandes de documents.

**Permissions :**
  - **Étudiant** : Voit uniquement ses propres demandes
  - **Admin/Personnel** : Voit toutes les demandes

**Filtres disponibles (Query Params) :**
  - `document_type`: Filtrer par type de document.
  - `status`: Filtrer par statut (ex: "NEW", "IN_PROGRESS", "READY", "REJECTED", "DELIVERED").
  - `ordering`: Trier les résultats par des champs comme `created_at` ou `status`.

**Réponse (200 OK) :** Une liste d'objets de demande de document avec la structure complète.

### 3. Détails de la demande de document (Consulter, Mettre à jour, Supprimer)
**GET**, **PUT**, **PATCH**, **DELETE** `/api/documents/demandes/{id}/`

**Description :**
    - `GET`: Récupère les détails d'une demande de document spécifique.
    - `PUT`/`PATCH`: Met à jour le statut ou ajoute un commentaire à une demande de document. Accessible uniquement par les administrateurs et le personnel.
    - `DELETE`: Supprime une demande de document. Accessible par l'étudiant qui l'a créée ou par les administrateurs/personnel.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Permissions :**
  - **GET** : Étudiant (sa propre demande) ou Admin/Personnel (toutes les demandes)
  - **PUT/PATCH** : Admin/Personnel uniquement
  - **DELETE** : Étudiant (sa propre demande) ou Admin/Personnel

**Corps de la requête pour PUT/PATCH (Admin/Personnel uniquement) :**
```json
{
    "status": "<new_status>",
    "comment": "<optional_comment>"
}
```
  - `status`: Le nouveau statut de la demande de document (ex: "IN_PROGRESS", "READY", "REJECTED", "DELIVERED").
  - `comment`: Un commentaire facultatif à ajouter à l'historique de la demande de document.

**Réponse (200 OK pour GET/PUT/PATCH, 204 No Content pour DELETE) :**
  - `GET`: Un seul objet de demande de document.
  - `PUT`/`PATCH`: L'objet de demande de document mis à jour.

### 4. Valider une demande de document (Admin/Personnel uniquement)
**PUT** `/api/documents/demandes/{id}/terminate/`

Met à jour le statut d'une demande de document à `READY` (Prêt). Seuls les administrateurs et le personnel peuvent effectuer cette action.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Réponse (200 OK) :** L'objet de demande de document mis à jour avec historique automatique.

### 5. Rejeter une demande de document (Admin/Personnel uniquement)
**PUT** `/api/documents/demandes/{id}/reject/`

Met à jour le statut d'une demande de document à `REJECTED` (Rejeté). Seuls les administrateurs et le personnel peuvent effectuer cette action.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Réponse (200 OK) :** L'objet de demande de document mis à jour avec historique automatique.

### 6. Passer une demande de document en traitement (Admin/Personnel uniquement)
**PUT** `/api/documents/demandes/{id}/process/`

Met à jour le statut d'une demande de document à `IN_PROGRESS` (En cours). Seuls les administrateurs et le personnel peuvent effectuer cette action.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Réponse (200 OK) :** L'objet de demande de document mis à jour avec historique automatique.

### 7. Télécharger le fichier PDF d'une demande de document (Admin/Personnel uniquement)
**GET** `/api/documents/demandes/{id}/file/`

Permet aux administrateurs et au personnel de télécharger le fichier PDF généré automatiquement associé à une demande de document spécifique.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Réponse (200 OK) :** Le fichier PDF de la demande de document est retourné directement (content-type: `application/pdf`).
En cas d'absence de fichier PDF ou si l'utilisateur n'a pas les permissions, un statut 404 ou 403 sera retourné.

### 8. Télécharger le fichier PDF demandé par l'admin (Admin/Personnel uniquement)
**PUT/PATCH** `/api/documents/demandes/{id}/upload-file/`

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

### 9. Générer un certificat d'inscription (Étudiant, Admin, Personnel)
**GET** `/api/documents/demandes/{id}/generate-inscription-certificate/`

Permet de générer et télécharger un certificat d'inscription au format PDF pour une demande spécifique.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Paramètres de requête (Query Params) :**
  - `lang` (facultatif): Langue du certificat (ex: `ar` pour Arabe, `fr` pour Français). Par défaut, la langue spécifiée dans la demande de document sera utilisée.

**Permissions :**
  - L'étudiant qui a créé la demande peut générer son propre certificat.
  - Les administrateurs et le personnel peuvent générer le certificat pour n'importe quelle demande.

**Conditions :**
  - La demande de document doit être de type `CERTIFICATE_INSCRIPTION`.
  - L'étudiant doit avoir un historique éducatif pour l'année académique spécifiée.

**Réponse (200 OK) :** Le fichier PDF du certificat d'inscription est retourné directement (content-type: `application/pdf`).
En cas d'absence de fichier PDF, de type de document incorrect, de permissions insuffisantes, ou de données manquantes, un statut 404 ou 403 sera retourné.

### 10. Générer un certificat de présence (Étudiant, Admin, Personnel)
**GET** `/api/documents/demandes/{id}/generate-presence-certificate/`

Permet de générer et télécharger un certificat de présence au format PDF pour une demande spécifique.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Paramètres de requête (Query Params) :**
  - `lang` (facultatif): Langue du certificat (ex: `ar` pour Arabe, `fr` pour Français). Par défaut, la langue spécifiée dans la demande de document sera utilisée.

**Permissions :**
  - L'étudiant qui a créé la demande peut générer son propre certificat.
  - Les administrateurs et le personnel peuvent générer le certificat pour n'importe quelle demande.

**Conditions :**
  - La demande de document doit être de type `CERTIFICATE_PRESENCE`.
  - L'étudiant doit avoir un historique éducatif pour l'année académique spécifiée.

**Réponse (200 OK) :** Le fichier PDF du certificat de présence est retourné directement (content-type: `application/pdf`).
En cas d'absence de fichier PDF, de type de document incorrect, de permissions insuffisantes, ou de données manquantes, un statut 404 ou 403 sera retourné.

### 11. Générer un certificat de réussite (Étudiant, Admin, Personnel)
**GET** `/api/documents/demandes/{id}/generate-success-certificate/`

Permet de générer et télécharger un certificat de réussite au format PDF pour une demande spécifique.

**Paramètres d'URL :**
  - `{id}`: Le `public_id` (UUID) de la demande de document.

**Paramètres de requête (Query Params) :**
  - `lang` (facultatif): Langue du certificat (ex: `ar` pour Arabe, `fr` pour Français). Par défaut, la langue spécifiée dans la demande de document sera utilisée.

**Permissions :**
  - L'étudiant qui a créé la demande peut générer son propre certificat.
  - Les administrateurs et le personnel peuvent générer le certificat pour n'importe quelle demande.

**Conditions :**
  - La demande de document doit être de type `CERTIFICATE_SUCCESS`.
  - L'étudiant doit avoir un historique éducatif pour l'année académique spécifiée.

**Réponse (200 OK) :** Le fichier PDF du certificat de réussite est retourné directement (content-type: `application/pdf`).
En cas d'absence de fichier PDF, de type de document incorrect, de permissions insuffisantes, ou de données manquantes, un statut 404 ou 403 sera retourné.

### 12. Créer une demande d'attestation de présence avec sélection d'enseignants (Étudiant)
**POST** `/api/documents/presence-requests/`

Permet à un étudiant de soumettre une nouvelle demande d'attestation de présence en sélectionnant exactement 2 enseignants pour approbation.

**Corps de la requête (JSON) :**
```json
{
    "language": "<language>",
    "reception_type": "<reception_type>",
    "academic_year": "<academic_year>",
    "teachers": ["<teacher_uuid_1>", "<teacher_uuid_2>"]
}
```
  - `language`: Langue souhaitée du document (ex: "ar" pour Arabe, "fr" pour Français).
  - `reception_type`: Mode de réception du document (ex: "ONLINE", "PERSONAL", "BOTH").
  - `academic_year`: Année académique au format "YYYY-YYYY" (ex: "2023-2024").
  - `teachers`: Tableau contenant exactement 2 UUIDs d'enseignants actifs pour approuver la demande.

**Permissions :**
  - **Étudiant** : Uniquement les étudiants authentifiés peuvent créer des demandes d'attestation de présence.

**Réponse (201 Created) :**
```json
{
    "id": "<uuid>",
    "student": {
        "id": <user_id>,
        "username": "<username>",
        "email": "<email>",
        "first_name": "<first_name>",
        "last_name": "<last_name>",
        "first_name_arabic": "<first_name_arabic>",
        "last_name_arabic": "<last_name_arabic>"
    },
    "document_type": "CERTIFICATE_PRESENCE",
    "status": "NEW",
    "language": "<language>",
    "reception_type": "<reception_type>",
    "academic_year": "<academic_year>",
    "created_at": "<datetime>",
    "updated_at": "<datetime>",
    "pdf_file": "<path_to_generated_pdf>"
}
```

**Notes :**
- Le type de document est automatiquement défini comme `CERTIFICATE_PRESENCE`.
- Un fichier PDF de demande est automatiquement généré.
- Des notifications par email sont automatiquement envoyées aux 2 enseignants sélectionnés.
- Chaque enseignant doit approuver la demande pour qu'elle passe en traitement administratif.
- Si un enseignant rejette la demande, elle est automatiquement rejetée.

### 13. Lister les demandes d'approbation en attente (Enseignant uniquement)
**GET** `/api/documents/teacher/approvals/`

Permet aux enseignants de voir la liste de leurs demandes d'attestation de présence en attente d'approbation.

**Permissions :**
  - **Enseignant** : Uniquement les enseignants authentifiés peuvent voir leurs propres demandes d'approbation.

**Réponse (200 OK) :** Une liste d'objets d'approbation avec la structure suivante :
```json
[
    {
        "id": <approval_id>,
        "document_request": {
            "id": "<request_uuid>",
            "student": {
                "id": <student_id>,
                "first_name": "<first_name>",
                "last_name": "<last_name>",
                "email": "<student_email>"
            },
            "language": "<language>",
            "reception_type": "<reception_type>",
            "academic_year": "<academic_year>",
            "created_at": "<datetime>"
        },
        "teacher": {
            "id": <teacher_id>,
            "first_name": "<first_name>",
            "last_name": "<last_name>",
            "email": "<teacher_email>"
        },
        "status": "PENDING",
        "created_at": "<datetime>",
        "updated_at": "<datetime>"
    }
]
```

### 14. Approuver ou rejeter une demande d'attestation de présence (Enseignant uniquement)
**GET**, **PUT**, **PATCH** `/api/documents/teacher/approvals/{id}/`

Permet aux enseignants de consulter, approuver ou rejeter une demande d'attestation de présence qui leur a été assignée.

**Paramètres d'URL :**
  - `{id}`: L'ID numérique de l'approbation.

**Permissions :**
  - **Enseignant** : Uniquement l'enseignant assigné à cette approbation peut la consulter ou la modifier.

**Description :**
    - `GET`: Récupère les détails de l'approbation.
    - `PUT`/`PATCH`: Met à jour le statut de l'approbation (APPROVED ou REJECTED).

**Corps de la requête pour PUT/PATCH :**
```json
{
    "status": "<approval_status>",
    "comment": "<optional_comment>"
}
```
  - `status`: Statut de l'approbation ("APPROVED" ou "REJECTED").
  - `comment`: Commentaire facultatif expliquant la décision.

**Réponse (200 OK) :**
```json
{
    "id": <approval_id>,
    "document_request": {
        "id": "<request_uuid>",
        "student": {...},
        "status": "<request_status>",
        "language": "<language>",
        "reception_type": "<reception_type>",
        "academic_year": "<academic_year>"
    },
    "teacher": {
        "id": <teacher_id>,
        "first_name": "<first_name>",
        "last_name": "<last_name>",
        "email": "<teacher_email>"
    },
    "status": "<approval_status>",
    "comment": "<comment>",
    "created_at": "<datetime>",
    "updated_at": "<datetime>"
}
```

**Notes :**
- **Logique métier automatique :**
  - Si un enseignant **rejette** la demande → Le statut de la demande passe automatiquement à "REJECTED".
  - Si les **deux enseignants approuvent** → Le statut de la demande passe automatiquement à "IN_PROGRESS" pour traitement administratif.
- Des notifications par email sont automatiquement envoyées à l'étudiant après chaque approbation/rejet.
- L'historique des changements de statut est automatiquement tracé.