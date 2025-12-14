import os
import json
import glob
import re
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    print("Will use system environment variables only")

# Use only keyword-based responses (no external AI models)
AI_AVAILABLE = False
print("Using keyword-based responses only")

class UniversityChatbot:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.knowledge_base = {
            'absence': {},
            'demarche': {},
            'license': {},
            'master': {}
        }
        self.load_data()

        # Use only keyword-based responses (no external AI models)
        self.ai_available = False
        self.tokenizer = None
        self.model = None
        print("Using keyword-based responses only")

        # Create comprehensive context from all data
        self.full_context = self._create_full_context()

        # Conversation memory
        self.current_program_context = None  # Store current program being discussed
        self.conversation_history = []  # Store recent conversation history

    def load_data(self):
        print("Loading data...")
        # Load absence
        absence_path = os.path.join(self.data_dir, 'absence.json')
        if os.path.exists(absence_path):
            with open(absence_path, 'r', encoding='utf-8') as f:
                self.knowledge_base['absence'] = json.load(f)
        
        # Load demarche
        demarche_path = os.path.join(self.data_dir, 'demarche.json')
        if os.path.exists(demarche_path):
            with open(demarche_path, 'r', encoding='utf-8') as f:
                self.knowledge_base['demarche'] = json.load(f)

        # Load licenses
        license_dir = os.path.join(self.data_dir, 'license')
        if os.path.exists(license_dir):
            for filepath in glob.glob(os.path.join(license_dir, '*.json')):
                name = os.path.basename(filepath).replace('.json', '')
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.knowledge_base['license'][name] = json.load(f)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")

        # Load masters (directory name is 'mastere' based on discovery)
        master_dir = os.path.join(self.data_dir, 'mastere')
        if os.path.exists(master_dir):
            for filepath in glob.glob(os.path.join(master_dir, '*.json')):
                name = os.path.basename(filepath).replace('.json', '')
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.knowledge_base['master'][name] = json.load(f)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
        
        print("Data loaded successfully.")

    def _create_full_context(self):
        """Create comprehensive context from all loaded data for Gemini"""
        context_parts = []

        # Add absence information
        if self.knowledge_base['absence']:
            context_parts.append(f"RÈGLES D'ABSENCE:\n{json.dumps(self.knowledge_base['absence'], ensure_ascii=False, indent=2)}")

        # Add administrative procedures
        if self.knowledge_base['demarche']:
            context_parts.append(f"DÉMARCHES ADMINISTRATIVES:\n{json.dumps(self.knowledge_base['demarche'], ensure_ascii=False, indent=2)}")

        # Add license programs
        if self.knowledge_base['license']:
            context_parts.append("PROGRAMMES DE LICENCE:")
            for name, data in self.knowledge_base['license'].items():
                context_parts.append(f"Licence {name}:\n{json.dumps(data, ensure_ascii=False, indent=2)}")

        # Add master programs
        if self.knowledge_base['master']:
            context_parts.append("PROGRAMMES DE MASTER:")
            for name, data in self.knowledge_base['master'].items():
                context_parts.append(f"Master {name}:\n{json.dumps(data, ensure_ascii=False, indent=2)}")

        return "\n\n".join(context_parts)

    def retrieve_context(self, query):
        """
        Simple keyword-based retrieval to find relevant JSON chunks.
        Uses conversation context to maintain program-specific discussions.
        """
        query = query.lower()
        context_chunks = []

        # Check for references to current program context
        program_references = ['ce programme', 'ce prgrammme', 'ce master', 'cette licence', 'ce cours', 'cette matière']
        if any(ref in query for ref in program_references) and self.current_program_context:
            # Use the stored program context
            context_chunks.append(f"Programme {self.current_program_context['name']}: {json.dumps(self.current_program_context['data'], ensure_ascii=False)}")
            return "\n\n".join(context_chunks)

        # 1. Administrative: Absence
        if any(w in query for w in ['absence', 'malade', 'justif', 'certificat', 'medical']):
            # Provide relevant section if possible, or broad absence info
            context_chunks.append("Règles d'absence: " + json.dumps(self.knowledge_base['absence'], ensure_ascii=False))

        # 2. Administrative: Procedures
        if any(w in query for w in ['demande', 'document', 'attestation', 'relevé', 'diplôme', 'demarche', 'papier', 'statut']):
            # Provide demarche info
            context_chunks.append("Démarches administratives: " + json.dumps(self.knowledge_base['demarche'], ensure_ascii=False))

        # 3. Academic Programs
        # Check for program names
        found_specific = False
        all_programs = {**self.knowledge_base['license'], **self.knowledge_base['master']}

        # First pass: look for exact diploma matches across all programs (highest priority)
        for name, data in all_programs.items():
            diplome_name = data.get('Diplome', '').lower() if isinstance(data, dict) else ''
            if diplome_name and diplome_name in query.lower():
                context_chunks.append(f"Programme {name}: {json.dumps(data, ensure_ascii=False)}")
                # Update conversation context
                self.current_program_context = {'name': name, 'data': data}
                found_specific = True
                break  # Found exact diploma match

        # Second pass: look for program name matches within preferred type
        if not found_specific:
            if 'licence' in query:
                target_programs = self.knowledge_base['license']
            elif 'master' in query:
                target_programs = self.knowledge_base['master']
            else:
                target_programs = all_programs

            for name, data in target_programs.items():
                name_keywords = [w for w in name.lower().split() if len(w) > 2]
                if name_keywords and any(k in query for k in name_keywords):
                    context_chunks.append(f"Programme {name}: {json.dumps(data, ensure_ascii=False)}")
                    # Update conversation context
                    self.current_program_context = {'name': name, 'data': data}
                    found_specific = True
                    break  # Stop at first program name match

        # If user asks about "licence" or "master" generally without specific name, maybe list them?
        if not found_specific and ('licence' in query or 'master' in query or 'filière' in query or 'options' in query or 'programme' in query or 'disponible' in query):
            licenses_list = list(self.knowledge_base['license'].keys())
            masters_list = list(self.knowledge_base['master'].keys())
            context_chunks.append(f"Licences disponibles: {', '.join(licenses_list)}")
            context_chunks.append(f"Masters disponibles: {', '.join(masters_list)}")

        # If asking about semesters in general
        if not found_specific and ('semestre' in query or 'semester' in query) and not any(w in query for w in ['matières', 'matiere', 'module', 'cours', 'sujet', 'subject']):
            context_chunks.append("Informations générales sur les semestres: Les programmes sont organisés en semestres avec différents modules et matières.")

        return "\n\n".join(context_chunks)

    def generate_response(self, user_input):
        """Generate response using keyword-based system with context from university data"""

        print("Using keyword-based response system...")
        try:
            response = self._fallback_structured_response(user_input)
            self._update_conversation_history(user_input, response)
            return response
        except Exception as e:
            print(f"Keyword-based response error: {e}")
            response = "Désolé, je rencontre des problèmes techniques. Pouvez-vous reformuler votre question ou réessayer plus tard ?"
            self._update_conversation_history(user_input, response)
            return response

    def _fallback_structured_response(self, user_input):
        """Fallback structured response when Gemini is unavailable"""
        context = self.retrieve_context(user_input)

        if not context.strip():
            return "Je ne trouve pas d'informations pertinentes dans ma base de connaissances pour votre question. Pouvez-vous reformuler votre question ou me demander quelque chose concernant les programmes universitaires, les absences ou les démarches administratives ?"

        # Use context for structured responses

        # Simple response generation based on context
        return self._generate_simple_response(user_input, context)

    def _generate_simple_response(self, user_input, context):
        """Generate a simple response based on the retrieved context"""
        user_input_lower = user_input.lower()

        # Handle specific question types
        # Prioritize coefficient extraction if asking about coefficients
        coefficient_keywords = ['coefficient', 'coef', 'cofficient', 'cofficent', 'coefficent']
        if any(word in user_input_lower for word in coefficient_keywords):
            return self._extract_coefficient_from_context(user_input, context)
        # Prioritize subject extraction if asking about subjects/materials
        elif any(word in user_input_lower for word in ['matières', 'matiere', 'module', 'cours', 'sujet', 'subject']):
            return self._extract_subjects_from_context(user_input, context)
        # Handle semester information (but not if also asking about subjects)
        elif any(word in user_input_lower for word in ['semestre', 'semester']) and not any(word in user_input_lower for word in ['matières', 'matiere', 'module', 'cours', 'sujet', 'subject']):
            return self._extract_semester_info_from_context(user_input, context)
        elif any(word in user_input_lower for word in ['absence', 'malade', 'justif']):
            return self._extract_absence_info_from_context(user_input, context)
        elif any(word in user_input_lower for word in ['demande', 'document', 'attestation']):
            return self._extract_demarche_info_from_context(user_input, context)
        else:
            # Generic response - try to provide a focused answer
            user_input_lower = user_input.lower()

            # Check if asking about programs in general
            if any(word in user_input_lower for word in ['programme', 'licence', 'master', 'filière', 'options', 'disponible']):
                # Always return available programs when asked
                licenses_list = list(self.knowledge_base['license'].keys())
                masters_list = list(self.knowledge_base['master'].keys())

                response = "Voici les programmes disponibles à l'université :\n\n"
                if licenses_list:
                    response += "Licences :\n"
                    for license in licenses_list:
                        response += f"- {license}\n"
                    response += "\n"

                if masters_list:
                    response += "Masters :\n"
                    for master in masters_list:
                        response += f"- {master}\n"

                response += "\nSi vous souhaitez en savoir plus sur un programme spécifique, dites-moi lequel vous intéresse !"
                return response

            # Check if asking about semester information in general
            if ('semestre' in user_input_lower or 'semester' in user_input_lower) and not any(word in user_input_lower for word in ['matières', 'matiere', 'module', 'cours', 'sujet', 'subject']):
                return "Je peux vous donner des informations détaillées sur les semestres d'un programme spécifique. Par exemple, vous pouvez me demander 'Quelles sont les matières du semestre 1 en licence d'informatique ?' ou 'Informations sur les semestres en master automatique'. Quel programme vous intéresse ?"

            # For other general questions, provide a summarized response
            return "J'ai trouvé quelques informations qui pourraient vous être utiles. Cependant, pour vous donner une réponse plus précise, pourriez-vous reformuler votre question ou me donner plus de détails sur ce que vous cherchez exactement ?"

    def _extract_subjects_from_context(self, user_input, context):
        """Extract and format subject information from context in a human-like response"""
        try:
            # Determine which semester the user is asking about
            user_input_lower = user_input.lower()

            # Extract semester number from user input
            semester_num = 1  # Default to semester 1
            if 'deuxième' in user_input_lower or 'deuxieme' in user_input_lower or '2ème' in user_input_lower or '2eme' in user_input_lower or 'second' in user_input_lower:
                semester_num = 2
            elif 'troisième' in user_input_lower or 'troisieme' in user_input_lower or '3ème' in user_input_lower or '3eme' in user_input_lower or 'third' in user_input_lower:
                semester_num = 3
            elif 'quatrième' in user_input_lower or 'quatrieme' in user_input_lower or '4ème' in user_input_lower or '4eme' in user_input_lower or 'fourth' in user_input_lower:
                semester_num = 4
            elif 'cinquième' in user_input_lower or 'cinquieme' in user_input_lower or '5ème' in user_input_lower or '5eme' in user_input_lower or 'fifth' in user_input_lower:
                semester_num = 5
            elif 'sixième' in user_input_lower or 'sixieme' in user_input_lower or '6ème' in user_input_lower or '6eme' in user_input_lower or 'sixth' in user_input_lower:
                semester_num = 6

            # Try to parse the JSON data directly from context
            json_start = context.find('{')
            if json_start != -1:
                json_part = context[json_start:]
                data = json.loads(json_part)

                # Extract program name
                program_name = ""
                if 'Parcours' in data:
                    program_name = data['Parcours']
                elif 'Diplome' in data:
                    program_name = data['Diplome']
                elif 'nom' in data:
                    program_name = data['nom']

                subjects_found = []

                # Handle license program structure (Semestres as array)
                if 'Semestres' in data and isinstance(data['Semestres'], list):
                    for sem_data in data['Semestres']:
                        if sem_data.get('Semestre') == semester_num:
                            for ue in sem_data.get('UE', []):
                                # Handle license structure: Elements[].Matiere
                                for element in ue.get('Elements', []):
                                    subject_name = element.get('Matiere', '')
                                    if subject_name:
                                        subjects_found.append(subject_name)
                                # Handle master structure: ECUE[].Matiere_ECUE
                                for ecue in ue.get('ECUE', []):
                                    subject_name = ecue.get('Matiere_ECUE', '')
                                    if subject_name:
                                        subjects_found.append(subject_name)

                # Handle master program structure (semestres as dict) - if exists
                elif 'semestres' in data and isinstance(data['semestres'], dict):
                    sem_key = str(semester_num)
                    if sem_key in data['semestres']:
                        semester_data = data['semestres'][sem_key]
                        if 'matières' in semester_data:
                            subjects_found = semester_data['matières']
                        # Also handle ECUE structure in master programs
                        elif 'UE' in semester_data:
                            for ue in semester_data['UE']:
                                for ecue in ue.get('ECUE', []):
                                    subject_name = ecue.get('Matiere_ECUE', '')
                                    if subject_name:
                                        subjects_found.append(subject_name)

                if subjects_found:
                    semester_ordinal = self._get_semester_ordinal(semester_num)
                    response = f"Pour le programme {program_name}, les matières enseignées au {semester_ordinal} semestre sont :\n\n"
                    for i, subject in enumerate(subjects_found[:10], 1):  # Limit to 10 subjects
                        response += f"{i}. {subject}\n"
                    if len(subjects_found) > 10:
                        response += f"\n... et {len(subjects_found) - 10} autres matières."
                    return response
                else:
                    semester_ordinal = self._get_semester_ordinal(semester_num)
                    return f"Je n'ai pas trouvé d'informations sur les matières du {semester_ordinal} semestre pour ce programme."

            # Fallback: try the old parsing method
            lines = context.split('\n')
            program_name = ""

            for line in lines:
                if line.startswith("Programme "):
                    program_name = line.replace("Programme ", "").replace(":", "")

            if program_name:
                return f"Je peux vous donner des informations sur le programme {program_name}, mais je n'ai pas pu extraire les détails des matières pour le moment."
            else:
                return "Je n'ai pas pu identifier le programme spécifique dont vous parlez. Pourriez-vous préciser de quel programme vous souhaitez connaître les matières ?"
        except:
            return "Je n'ai pas pu récupérer les informations sur les matières pour le moment. Pourriez-vous reformuler votre question ?"

    def _get_semester_ordinal(self, num):
        """Convert semester number to ordinal string in French"""
        ordinals = {
            1: "premier",
            2: "deuxième",
            3: "troisième",
            4: "quatrième",
            5: "cinquième",
            6: "sixième"
        }
        return ordinals.get(num, f"{num}ème")

    def _extract_semester_info_from_context(self, user_input, context):
        """Extract semester-specific information in a human-like response"""
        try:
            # Determine which semester the user is asking about
            user_input_lower = user_input.lower()

            # Extract semester number from user input
            semester_num = None
            if 'deuxième' in user_input_lower or 'deuxieme' in user_input_lower or '2ème' in user_input_lower or '2eme' in user_input_lower or 'second' in user_input_lower:
                semester_num = 2
            elif 'troisième' in user_input_lower or 'troisieme' in user_input_lower or '3ème' in user_input_lower or '3eme' in user_input_lower or 'third' in user_input_lower:
                semester_num = 3
            elif 'quatrième' in user_input_lower or 'quatrieme' in user_input_lower or '4ème' in user_input_lower or '4eme' in user_input_lower or 'fourth' in user_input_lower:
                semester_num = 4
            elif 'cinquième' in user_input_lower or 'cinquieme' in user_input_lower or '5ème' in user_input_lower or '5eme' in user_input_lower or 'fifth' in user_input_lower:
                semester_num = 5
            elif 'sixième' in user_input_lower or 'sixieme' in user_input_lower or '6ème' in user_input_lower or '6eme' in user_input_lower or 'sixth' in user_input_lower:
                semester_num = 6

            lines = context.split('\n')
            program_name = ""

            for line in lines:
                if line.startswith("Programme "):
                    program_name = line.replace("Programme ", "").replace(":", "")
                elif '"Semestres"' in line or '"Diplome"' in line:
                    try:
                        json_start = line.find('{')
                        if json_start != -1:
                            json_part = line[json_start:]
                            data = json.loads(json_part)

                            if 'Semestres' in data:
                                if semester_num:
                                    # Specific semester requested
                                    for sem_data in data['Semestres']:
                                        if sem_data.get('Semestre') == semester_num:
                                            total_credits = sum(ue.get('Cr', 0) for ue in sem_data.get('UE', []))
                                            num_modules = len(sem_data.get('UE', []))
                                            semester_ordinal = self._get_semester_ordinal(semester_num)

                                            response = f"Informations sur le {semester_ordinal} semestre du programme {program_name} :\n\n"
                                            response += f"- {num_modules} modules principaux\n"
                                            response += f"- Crédits totaux : {total_credits}\n\n"

                                            # List modules
                                            response += "Modules :\n"
                                            for ue in sem_data.get('UE', []):
                                                module_name = ue.get('Module', 'N/A')
                                                credits = ue.get('Cr', 0)
                                                response += f"- {module_name} ({credits} crédits)\n"

                                            return response

                                    return f"Je n'ai pas trouvé d'informations sur le {self._get_semester_ordinal(semester_num)} semestre pour ce programme."
                                else:
                                    # General semester overview
                                    response = f"Voici les informations sur les semestres pour le programme {program_name} :\n\n"

                                    for sem_data in data['Semestres'][:4]:  # Limit to first 4 semesters
                                        sem_num = sem_data.get('Semestre', 'N/A')
                                        total_credits = sum(ue.get('Cr', 0) for ue in sem_data.get('UE', []))
                                        num_modules = len(sem_data.get('UE', []))

                                        response += f"Semestre {sem_num} :\n"
                                        response += f"- {num_modules} modules principaux\n"
                                        response += f"- Crédits totaux : {total_credits}\n\n"

                                    if len(data['Semestres']) > 4:
                                        response += f"Le programme comprend {len(data['Semestres'])} semestres au total."

                                    return response
                    except:
                        continue

            if program_name:
                return f"J'ai des informations sur le programme {program_name}, mais je n'ai pas pu extraire les détails des semestres. Pourriez-vous préciser quelle information vous cherchez exactement ?"
            else:
                return "Je n'ai pas pu identifier le programme spécifique. Pourriez-vous me dire de quel programme vous souhaitez connaître les informations sur les semestres ?"

        except:
            return "Je n'ai pas pu récupérer les informations sur les semestres pour le moment. Pourriez-vous reformuler votre question ou préciser le programme qui vous intéresse ?"

    def _extract_absence_info_from_context(self, user_input, context):
        """Extract absence-related information in a human-like response"""
        # Check for specific common questions first
        user_input_lower = user_input.lower()

        # Address bus delay specifically - always return this for bus questions
        if 'bus' in user_input_lower or 'retard' in user_input_lower or 'transport' in user_input_lower:
            response = "Le retard de bus n'est généralement pas considéré comme une justification d'absence. Les problèmes de transport ne sont justifiés que dans des cas exceptionnels (grève générale, conditions météo extrêmes).\n\n"
            # Still provide the general absence information
            response += "Voici les règles générales concernant les absences :\n\n"
        else:
            response = "Voici les règles concernant les absences :\n\n"

        try:
            # Parse the absence JSON data
            json_start = context.find('{')
            if json_start != -1:
                json_part = context[json_start:]
                data = json.loads(json_part)

                # Justified absences
                if 'absences_justifiees' in data:
                    response += "Absences justifiées :\n"
                    categories = []
                    for category in data['absences_justifiees'][:3]:  # Limit to 3 categories
                        cat_name = category.get('categorie', '')
                        reasons = category.get('raisons', [])[:2]  # Limit to 2 reasons per category
                        if cat_name and reasons:
                            categories.append(f"- {cat_name} : {', '.join(reasons)}")
                    response += "\n".join(categories)
                    response += "\n\n"

                    # Add common non-justified absences
                    if 'absences_non_justifiees' in data:
                        response += "Absences non justifiées (exemples) :\n"
                        non_justified = data['absences_non_justifiees'][:4]  # Limit to 4 examples
                        for reason in non_justified:
                            response += f"- {reason}\n"
                        response += "\n"

                # Procedures
                if 'demarches' in data:
                    demarches = data['demarches']
                    if 'avant_absence' in demarches:
                        response += "Avant l'absence :\n"
                        for step in demarches['avant_absence']:
                            response += f"- {step}\n"

                    if 'apres_absence' in demarches:
                        response += "\nAprès l'absence :\n"
                        for step in demarches['apres_absence']:
                            response += f"- {step}\n"

                # Key advice
                if 'conseils' in data:
                    response += "\nConseils importants :\n"
                    for conseil in data['conseils'][:3]:  # Limit to 3 tips
                        response += f"- {conseil}\n"

                response += "\nPour toute absence, il est préférable de prévenir à l'avance et de fournir un justificatif dans les délais."
                return response

        except Exception as e:
            # If JSON parsing fails, still provide basic information
            if 'bus' in user_input_lower or 'retard' in user_input_lower:
                return response + "Les absences médicales, familiales ou administratives peuvent être justifiées avec les documents appropriés."
            pass

        return "Concernant les absences, il est important de prévenir vos professeurs et de fournir un justificatif médical ou administratif dans les 3 jours. Les absences non justifiées peuvent avoir des conséquences sur votre scolarité. Si vous avez une question spécifique sur les procédures d'absence, n'hésitez pas à la poser."

    def _extract_coefficient_from_context(self, user_input, context):
        """Extract coefficient information for a specific subject"""
        try:
            # Extract subject name from user input
            user_input_lower = user_input.lower()

            # Common patterns for coefficient questions
            patterns = [
                r'coefficient.*matiere\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)',
                r'coef.*matiere\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)',
                r'cofficient.*matiere\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)',
                r'cofficent.*matiere\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)',
                r'coefficent.*matiere\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)',
                r'coefficient.*de\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)',
                r'coef.*de\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)',
                r'cofficient.*de\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)',
                r'cofficent.*de\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)',
                r'coefficent.*de\s+(.+?)(?:\s+dans|\s+en|\s+du|\s+de|\s+ce|\s+cette|\s+programme|$)'            ]

            subject_name = None
            for pattern in patterns:
                import re
                match = re.search(pattern, user_input_lower, re.IGNORECASE)
                if match:
                    subject_name = match.group(1).strip()
                    # Clean up the subject name by removing extra words
                    subject_name = re.sub(r'\s+(dans|en|du|de|ce|cette|programme).*$', '', subject_name)
                    break

            if not subject_name:
                # Try to extract subject name after "matiere" or similar
                words = user_input_lower.split()
                try:
                    matiere_idx = next(i for i, word in enumerate(words) if 'matiere' in word or 'matière' in word)
                    if matiere_idx + 1 < len(words):
                        # Extract until common stop words or end of sentence
                        subject_words = []
                        for word in words[matiere_idx + 1:]:
                            # Stop at program references or other keywords
                            if word in ['dans', 'en', 'du', 'de', 'ce', 'cette', 'programme', 'master', 'licence', 'coefficient', 'coef']:
                                break
                            subject_words.append(word)
                        subject_name = ' '.join(subject_words).strip()
                except StopIteration:
                    pass

            if not subject_name:
                return "Je n'ai pas pu identifier la matière dont vous voulez connaître le coefficient. Pourriez-vous préciser le nom de la matière ?"


            # First try to extract from the provided context (program-specific)
            try:
                # Parse context to find specific program data
                context_parts = context.split('\n\n')
                for part in context_parts:
                    if part.startswith('Programme '):
                        # Extract program data from context
                        json_start = part.find('{')
                        if json_start != -1:
                            json_part = part[json_start:]
                            program_data = json.loads(json_part)

                            coefficient = self._find_subject_coefficient(program_data, subject_name)
                            if coefficient is not None:
                                prog_display_name = program_data.get('Parcours', program_data.get('Diplome', program_data.get('Mention', 'inconnu')))
                                return f"Le coefficient de la matière '{subject_name}' dans le programme {prog_display_name} est de {coefficient}."

                            # Try broader search
                            coefficient = self._find_subject_coefficient_broad(program_data, subject_name)
                            if coefficient is not None:
                                prog_display_name = program_data.get('Parcours', program_data.get('Diplome', program_data.get('Mention', 'inconnu')))
                                return f"Le coefficient de la matière '{subject_name}' dans le programme {prog_display_name} est de {coefficient}."
            except:
                pass

            # If no context found but we have current program context, use it
            if self.current_program_context:
                coefficient = self._find_subject_coefficient(self.current_program_context['data'], subject_name)
                if coefficient is not None:
                    prog_data = self.current_program_context['data']
                    prog_display_name = prog_data.get('Parcours', prog_data.get('Diplome', self.current_program_context['name']))
                    return f"Le coefficient de la matière '{subject_name}' dans le programme {prog_display_name} est de {coefficient}."

                # Try broader search
                coefficient = self._find_subject_coefficient_broad(self.current_program_context['data'], subject_name)
                if coefficient is not None:
                    prog_data = self.current_program_context['data']
                    prog_display_name = prog_data.get('Parcours', prog_data.get('Diplome', self.current_program_context['name']))
                    return f"Le coefficient de la matière '{subject_name}' dans le programme {prog_display_name} est de {coefficient}."

            # If no specific program found in context, search all programs
            all_programs = {**self.knowledge_base['license'], **self.knowledge_base['master']}
            for program_name, data in all_programs.items():
                coefficient = self._find_subject_coefficient(data, subject_name)
                if coefficient is not None:
                    prog_display_name = data.get('Parcours', data.get('Diplome', program_name))
                    return f"Le coefficient de la matière '{subject_name}' dans le programme {prog_display_name} est de {coefficient}."

                # Try broader search
                coefficient = self._find_subject_coefficient_broad(data, subject_name)
                if coefficient is not None:
                    prog_display_name = data.get('Parcours', data.get('Diplome', program_name))
                    return f"Le coefficient de la matière '{subject_name}' dans le programme {prog_display_name} est de {coefficient}."

            return f"Je n'ai pas trouvé d'informations sur le coefficient de la matière '{subject_name}'. Il se peut que cette matière n'existe pas dans ma base de données ou qu'elle soit formulée différemment."

        except Exception as e:
            return "Je n'ai pas pu récupérer les informations sur le coefficient pour le moment. Pourriez-vous reformuler votre question ?"

    def _find_subject_coefficient(self, data, subject_name):
        """Find coefficient for a specific subject in program data"""
        subject_name_lower = subject_name.lower()

        # Handle license program structure (Semestres as array)
        if 'Semestres' in data and isinstance(data['Semestres'], list):
            for sem_data in data['Semestres']:
                if 'UE' in sem_data:
                    for ue in sem_data['UE']:
                        # Handle license structure: Elements[].Matiere with Coef
                        if 'Elements' in ue:
                            for element in ue['Elements']:
                                matiere = element.get('Matiere', '').lower()
                                # Check for exact match or close match
                                if subject_name_lower in matiere or matiere in subject_name_lower:
                                    return element.get('Coef')
                        # Handle master structure: ECUE[].Matiere_ECUE with Coefficient_ECUE
                        if 'ECUE' in ue:
                            for ecue in ue['ECUE']:
                                matiere = ecue.get('Matiere_ECUE', '').lower()
                                # Check for exact match or close match
                                if subject_name_lower in matiere or matiere in subject_name_lower:
                                    return ecue.get('Coefficient_ECUE')

        # Handle master program structure (semestres as dict) - if exists
        elif 'semestres' in data and isinstance(data['semestres'], dict):
            for sem_key, sem_data in data['semestres'].items():
                if 'UE' in sem_data:
                    for ue in sem_data['UE']:
                        if 'ECUE' in ue:
                            for ecue in ue['ECUE']:
                                matiere = ecue.get('Matiere_ECUE', '').lower()
                                if subject_name_lower in matiere or matiere in subject_name_lower:
                                    return ecue.get('Coefficient_ECUE')

        return None

    def _find_subject_coefficient_broad(self, data, subject_name):
        """Broader search for subject coefficient"""
        subject_name_lower = subject_name.lower()

        # Search all text in JSON for coefficient information
        def search_dict(d, target):
            if isinstance(d, dict):
                for key, value in d.items():
                    # Check for license structure: matiere with Coef
                    if key.lower() == 'matiere' and target in str(value).lower():
                        # Found the subject, now find its coefficient in the same dict
                        return d.get('Coef')
                    # Check for master structure: Matiere_ECUE with Coefficient_ECUE
                    elif key.lower() == 'matiere_ecue' and target in str(value).lower():
                        # Found the subject, now find its coefficient in the same dict
                        return d.get('Coefficient_ECUE')
                    elif isinstance(value, (dict, list)):
                        result = search_dict(value, target)
                        if result is not None:
                            return result
            elif isinstance(d, list):
                for item in d:
                    result = search_dict(item, target)
                    if result is not None:
                        return result
            return None

        return search_dict(data, subject_name_lower)

    def _update_conversation_history(self, user_input, response):
        """Update conversation history with the latest interaction"""
        self.conversation_history.append({
            'user_input': user_input,
            'response': response,
            'timestamp': None  # Could add timestamp if needed
        })

        # Keep only last 10 conversations to avoid memory issues
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

    def _extract_demarche_info_from_context(self, user_input, context):
        """Extract administrative procedure information in a human-like response"""
        try:
            # Parse the demarche JSON data
            json_start = context.find('{')
            if json_start != -1:
                json_part = context[json_start:]
                data = json.loads(json_part)

                if 'demarches_administratives' in data:
                    demarches = data['demarches_administratives']

                    # Check what type of document the user is asking about
                    user_input_lower = user_input.lower()

                    # Look for specific document types - more precise matching
                    # Check for attendance certificate (presence)
                    if ('presence' in user_input_lower and 'attestation' in user_input_lower) or \
                       ('présence' in user_input_lower and 'attestation' in user_input_lower):
                        if 'attestation_de_presence' in demarches:
                            doc = demarches['attestation_de_presence']
                            response = f"{doc['titre']}\n\n"
                            response += f"{doc['description']}\n\n"
                            response += f"Délai total : {doc['delai_total']}\n"
                            response += f"Validité : {doc['validite']}\n\n"

                            response += "Étapes principales :\n"
                            for etape in doc['etapes'][:5]:  # Limit to 5 steps
                                response += f"{etape['numero']}. {etape['action']} ({etape['duree']})\n"

                            if 'conseils' in doc:
                                response += "\nConseils :\n"
                                for conseil in doc['conseils'][:2]:
                                    response += f"- {conseil}\n"

                            return response

                    # Check for success certificate (reussite)
                    elif ('reussite' in user_input_lower and 'attestation' in user_input_lower) or \
                         ('réussite' in user_input_lower and 'attestation' in user_input_lower) or \
                         ('reussir' in user_input_lower) or ('réussir' in user_input_lower):
                        # Look for the success certificate entry
                        success_key = None
                        for key in demarches.keys():
                            if 'reussite' in key.lower() or 'réussite' in key.lower():
                                success_key = key
                                break

                        if success_key and success_key in demarches:
                            doc = demarches[success_key]
                            response = f"{doc['titre']}\n\n"
                            response += f"{doc['description']}\n\n"
                            response += f"Délai : {doc.get('delai_total', '1 à 2 jours ouvrables')}\n"
                            response += f"Validité : {doc.get('validite', '1 an')}\n\n"

                            response += "Le processus est simple :\n"
                            response += "1. Faire la demande en ligne via la plateforme\n"
                            response += "2. Attendre le traitement (1-2 jours)\n"
                            response += "3. Télécharger le document une fois disponible\n\n"

                            if 'conseils' in doc:
                                response += "Astuces :\n"
                                for conseil in doc['conseils'][:2]:
                                    response += f"- {conseil}\n"

                            return response

                    elif 'relevé' in user_input_lower or 'notes' in user_input_lower or 'diplôme' in user_input_lower:
                        if 'releve_de_notes' in demarches:
                            doc = demarches['releve_de_notes']
                            response = f"{doc['titre']}\n\n"
                            response += f"{doc['description']}\n\n"
                            response += f"Délai : {doc['delai_total']}\n"
                            response += f"Validité : {doc['validite']}\n\n"

                            response += "Le processus est simple :\n"
                            response += "1. Faire la demande en ligne via la plateforme\n"
                            response += "2. Attendre le traitement (1-2 jours)\n"
                            response += "3. Télécharger le document une fois disponible\n\n"

                            if 'conseils' in doc:
                                response += "Astuces :\n"
                                for conseil in doc['conseils'][:2]:
                                    response += f"- {conseil}\n"

                            return response

                    # General response for administrative procedures
                    available_docs = list(demarches.keys())
                    doc_names = []
                    for doc_key in available_docs[:3]:  # Limit to 3
                        if doc_key in demarches:
                            doc_names.append(demarches[doc_key].get('titre', doc_key))

                    response = "Je peux vous aider avec plusieurs types de documents administratifs :\n\n"
                    for i, doc_name in enumerate(doc_names, 1):
                        response += f"{i}. {doc_name}\n"

                    response += "\nPouvez-vous préciser quel document vous souhaitez demander ? Par exemple :\n"
                    response += "- Attestation de présence\n- Attestation de réussite\n- Relevé de notes\n- Attestation de diplôme"

                    if 'informations_generales' in data:
                        info = data['informations_generales']
                        if 'horaires_bureau' in info:
                            response += f"\n\nHoraires du bureau : {info['horaires_bureau']}"

                    return response

        except:
            pass

        return "Pour les démarches administratives, vous pouvez faire vos demandes directement via la plateforme étudiante. Les documents comme les attestations de présence, relevés de notes, ou attestations de diplôme sont généralement disponibles en ligne. Si vous avez une question spécifique sur une procédure, n'hésitez pas à me la poser plus précisément."

def main():
    # Assume data is in 'data' subdirectory relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'data')
    
    bot = UniversityChatbot(data_dir)
    print("=== Chatbot Universitaire ===")
    print("Tapez 'quit' ou 'exit' pour quitter.")
    
    while True:
        try:
            user_input = input("\nVous: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            if not user_input.strip():
                continue
                
            response = bot.generate_response(user_input)
            print(f"Bot: {response}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
