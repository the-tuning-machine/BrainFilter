"""
Générateur de dataset de titres YouTube pour l'entraînement du classificateur.
"""
import random
import pandas as pd
from pathlib import Path


# Templates de titres par catégorie
TITLE_TEMPLATES = {
    "jeux": [
        # Gaming populaire
        "{jeu} - {action} #{numero}",
        "JE {action_caps} {jeu} ! {emoji}",
        "{jeu} : {description}",
        "TOP {numero} {chose} dans {jeu}",
        "{jeu} {mode} - {description}",
        "TUTO {jeu} : {conseil}",
        "{jeu} GAMEPLAY FR #{numero}",
        "LIVE {jeu} - {description}",
        "{jeu} FUNNY MOMENTS",
        "ON TEST {jeu} !",
        "{jeu} - C'EST DE LA FOLIE",
        "DÉCOUVERTE {jeu}",
        "{jeu} SPEEDRUN {temps}",
        "{jeu} - {personnage} BUILD OP",
        "RAGE QUIT {jeu}",
    ],
    "musique": [
        "{artiste} - {titre}",
        "{titre} ({style})",
        "{artiste} - {titre} [Official Video]",
        "{titre} - {artiste} (Lyrics)",
        "{style} Mix {annee}",
        "Best of {artiste}",
        "{titre} Cover",
        "{instrument} Tutorial - {titre}",
        "{style} Playlist {humeur}",
        "{titre} - Live Performance",
        "Comment jouer {titre} au {instrument}",
        "{artiste} - {titre} (Acoustic)",
        "{style} Relaxation Music",
        "{titre} Remix {annee}",
    ],
    "math": [
        "Comprendre {concept} en {duree} minutes",
        "{concept} : Explication simple",
        "Exercice corrigé : {sujet}",
        "Introduction à {concept}",
        "Les {concept} expliqués simplement",
        "{concept} : Ce que votre prof ne vous dit pas",
        "Résoudre {probleme} facilement",
        "Cours de {niveau} : {concept}",
        "{concept} - Démonstration",
        "Pourquoi {concept} ?",
        "Applications de {concept}",
        "{concept} : Méthode rapide",
        "Les secrets de {concept}",
    ],
    "sciences": [
        "{phenomene} expliqué en {duree} minutes",
        "Comment fonctionne {chose} ?",
        "La science de {sujet}",
        "{phenomene} : Les dernières découvertes",
        "Expérience : {experience}",
        "Pourquoi {question} ?",
        "{sujet} - Documentaire",
        "Les mystères de {phenomene}",
        "Comprendre {concept_sci}",
        "{phenomene} - Ce que vous ne savez pas",
        "La physique de {chose}",
        "Biologie : {sujet}",
        "Chimie : {experience}",
        "Astronomie - {phenomene}",
    ],
    "documentaires": [
        "{sujet} - Documentaire complet",
        "L'histoire de {sujet}",
        "{evenement} : Le documentaire",
        "Dans les coulisses de {lieu}",
        "Voyage à {lieu}",
        "{sujet} - La vérité révélée",
        "Enquête sur {sujet}",
        "Les secrets de {chose}",
        "{civilisation} : Histoire et mystères",
        "À la découverte de {lieu}",
        "{personnage} - Biographie",
        "Le monde de {sujet}",
        "{evenement} - Retour sur l'histoire",
    ],
    "philosophie": [
        "{philosophe} et {concept}",
        "Introduction à {courant}",
        "Qu'est-ce que {concept_philo} ?",
        "{philosophe} expliqué simplement",
        "Le problème de {question_philo}",
        "Philosophie : {theme}",
        "{concept_philo} selon {philosophe}",
        "Débat : {question_philo}",
        "Les idées de {philosophe}",
        "Éthique : {question_ethique}",
        "Existe-t-il {question_philo} ?",
        "{courant} : Les grands principes",
    ],
    "divertissement": [
        "{emotion_caps} ! {description}",
        "TOP {numero} {chose_drole}",
        "{chose_drole} COMPILATION",
        "PRANK : {description_prank}",
        "DÉFI : {defi}",
        "ON TESTE {chose_test}",
        "{chose_drole} - BEST OF",
        "JE RÉAGIS À {contenu}",
        "FAIL COMPILATION #{numero}",
        "{description_drole} {emoji}",
        "VLOG : {activite}",
        "24H {defi}",
        "ON A ACHETÉ {chose_bizarre}",
        "STORYTIME : {histoire}",
        "{chose_drole} TIKTOK",
    ],
    "shorts": [
        "{action_courte} #shorts",
        "{astuce} #shorts",
        "{fait} 😱 #shorts",
        "POV: {situation} #shorts",
        "{question_courte} #shorts",
        "#shorts {action_courte}",
        "{fait_choc} #shorts",
        "{conseil_court} #shorts",
        "{meme} #shorts",
        "Wait for it... #shorts",
    ]
}

# Vocabulaire par catégorie
VOCABULARY = {
    "jeux": {
        "jeu": ["Minecraft", "Fortnite", "GTA 5", "League of Legends", "Valorant",
                "Call of Duty", "FIFA", "Rocket League", "Among Us", "Apex Legends",
                "CS:GO", "Overwatch", "Warzone", "Clash Royale", "Elden Ring"],
        "action": ["gameplay", "découverte", "test", "let's play", "partie", "run"],
        "action_caps": ["TESTE", "DÉCOUVRE", "JOUE À", "DÉTRUIS TOUT DANS"],
        "description": ["c'est incroyable", "premier essai", "nouvelle map", "nouvelle saison",
                       "mode hardcore", "avec les abonnés", "en solo"],
        "numero": [str(i) for i in range(1, 101)],
        "chose": ["KILLS", "TRICKS", "FAILS", "MOMENTS", "PLAYS"],
        "mode": ["Battle Royale", "Ranked", "Casual", "Custom"],
        "conseil": ["Devenir meilleur", "Gagner facilement", "Techniques de pro"],
        "emoji": ["😱", "🔥", "💀", "⚡"],
        "temps": ["WR", "Any%", "100%"],
        "personnage": ["OP", "META", "BROKEN"],
    },
    "musique": {
        "artiste": ["The Beatles", "Queen", "Pink Floyd", "Led Zeppelin", "Metallica",
                    "Nirvana", "AC/DC", "Radiohead", "Coldplay", "Muse"],
        "titre": ["Bohemian Rhapsody", "Imagine", "Hotel California", "Stairway to Heaven",
                 "Smells Like Teen Spirit", "Wonderwall", "Sweet Child O' Mine"],
        "style": ["Rock", "Pop", "Jazz", "Classical", "Blues", "Metal", "Electro", "Hip Hop"],
        "annee": ["2023", "2024", "2025"],
        "instrument": ["guitare", "piano", "batterie", "basse", "violon"],
        "humeur": ["Relax", "Workout", "Study", "Sleep", "Party"],
    },
    "math": {
        "concept": ["les dérivées", "les intégrales", "les limites", "les probabilités",
                   "les matrices", "les équations différentielles", "les nombres complexes",
                   "la géométrie analytique", "les suites", "les fonctions"],
        "duree": ["5", "10", "15", "20"],
        "sujet": ["équations du second degré", "théorème de Pythagore", "trigonométrie",
                 "logarithmes", "exponentielle"],
        "niveau": ["Terminale", "Première", "Seconde", "Licence", "Prépa"],
        "probleme": ["ce problème", "cette équation", "cet exercice"],
    },
    "sciences": {
        "phenomene": ["La relativité", "La mécanique quantique", "L'évolution", "Le big bang",
                     "Les trous noirs", "La photosynthèse", "L'ADN", "Les ondes gravitationnelles"],
        "duree": ["5", "10", "15", "20", "30"],
        "chose": ["le cerveau", "l'univers", "les atomes", "la lumière", "l'électricité",
                 "Internet", "les smartphones", "les vaccins"],
        "question": ["le ciel est bleu", "nous rêvons", "les oiseaux volent",
                    "l'eau bout", "les saisons existent"],
        "sujet": ["le système solaire", "les cellules", "l'écosystème", "le climat"],
        "experience": ["Créer un volcan", "Extraire l'ADN", "Fabriquer un circuit"],
        "concept_sci": ["la gravité", "l'électromagnétisme", "la thermodynamique"],
    },
    "documentaires": {
        "sujet": ["l'Égypte ancienne", "la Seconde Guerre mondiale", "les pyramides",
                 "les océans", "la nature", "l'espace", "les civilisations perdues"],
        "evenement": ["Tchernobyl", "Le débarquement", "La chute du mur de Berlin"],
        "lieu": ["Tokyo", "New York", "la forêt amazonienne", "l'Antarctique", "Mars"],
        "chose": ["l'univers", "la Terre", "l'humanité", "la vie"],
        "civilisation": ["Les Mayas", "Les Romains", "Les Vikings", "Les Égyptiens"],
        "personnage": ["Einstein", "Napoléon", "Churchill", "Cléopâtre"],
    },
    "philosophie": {
        "philosophe": ["Platon", "Aristote", "Kant", "Nietzsche", "Sartre", "Descartes",
                      "Spinoza", "Hegel", "Socrate", "Épicure"],
        "concept": ["la morale", "la vérité", "la liberté", "le bonheur", "la justice"],
        "courant": ["le stoïcisme", "l'existentialisme", "l'utilitarisme", "le rationalisme"],
        "concept_philo": ["la conscience", "le libre arbitre", "l'existence", "le bien"],
        "question_philo": ["vraiment libres", "une réalité objective", "un sens à la vie"],
        "theme": ["L'éthique", "La métaphysique", "L'épistémologie"],
        "question_ethique": ["Peut-on mentir", "Le devoir moral", "La justice sociale"],
    },
    "divertissement": {
        "emotion_caps": ["INCROYABLE", "WTF", "OMG", "FOU", "CHOQUANT", "MDR"],
        "description": ["Vous n'allez pas le croire", "C'est trop drôle", "Regardez ça"],
        "numero": [str(i) for i in range(5, 51, 5)],
        "chose_drole": ["FAILS", "MOMENTS GÊNANTS", "SITUATIONS AWKWARD", "VIDÉOS DRÔLES"],
        "description_prank": ["Il croit que je suis...", "On piège mon ami", "Caméra cachée"],
        "defi": ["Ne pas rire", "Manger épicé", "24h sans téléphone", "Parler qu'en anglais"],
        "chose_test": ["LE TRUC BIZARRE D'AMAZON", "LA NOURRITURE AMÉRICAINE", "LES GADGETS INUTILES"],
        "contenu": ["des vidéos TikTok", "mes anciens posts", "vos commentaires"],
        "description_drole": ["C'EST N'IMPORTE QUOI", "ON EST CHOQUÉS", "TROP MARRANT"],
        "emoji": ["😂", "🤣", "😱", "🔥"],
        "activite": ["MA JOURNÉE", "VACANCES", "SHOPPING", "ROUTINE"],
        "chose_bizarre": ["LE TRUC LE PLUS CHER", "100 TRUCS BIZARRES"],
        "histoire": ["Comment j'ai raté mon exam", "Ma pire date", "J'ai rencontré..."],
    },
    "shorts": {
        "action_courte": ["Incroyable astuce", "Regarde ça", "Tu savais ça ?"],
        "astuce": ["Astuce de ouf", "Life hack", "Trick"],
        "fait": ["Saviez-vous que", "Ce truc est fou", "Incroyable"],
        "situation": ["Tu es étudiant", "C'est lundi matin", "Tu rentres chez toi"],
        "question_courte": ["C'est quoi ça ?", "Comment ?", "Pourquoi ?"],
        "fait_choc": ["😱 INCROYABLE", "🔥 FOU", "💀 WTF"],
        "conseil_court": ["Conseil du jour", "Astuce rapide", "À savoir"],
        "meme": ["POV", "When", "Me trying to"],
    }
}


def generate_title(category):
    """Génère un titre aléatoire pour une catégorie donnée."""
    template = random.choice(TITLE_TEMPLATES[category])
    vocab = VOCABULARY[category]

    # Remplacer les placeholders par des valeurs aléatoires
    title = template
    for key, values in vocab.items():
        placeholder = "{" + key + "}"
        if placeholder in title:
            title = title.replace(placeholder, random.choice(values))

    return title


def generate_dataset(samples_per_category=200, seed=42):
    """
    Génère un dataset complet de titres YouTube.

    Args:
        samples_per_category: Nombre d'échantillons par catégorie
        seed: Seed pour la reproductibilité

    Returns:
        DataFrame avec colonnes 'title' et 'category'
    """
    random.seed(seed)

    data = []
    categories = list(TITLE_TEMPLATES.keys())

    for category in categories:
        for _ in range(samples_per_category):
            title = generate_title(category)
            data.append({
                'title': title,
                'category': category
            })

    df = pd.DataFrame(data)

    # Mélanger le dataset
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    return df


def main():
    """Génère et sauvegarde le dataset."""
    print("Génération du dataset...")

    # Générer le dataset
    df = generate_dataset(samples_per_category=200)

    # Créer le dossier data/raw s'il n'existe pas
    output_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sauvegarder
    output_path = output_dir / "youtube_titles.csv"
    df.to_csv(output_path, index=False)

    print(f"\n✓ Dataset généré : {output_path}")
    print(f"  - Total : {len(df)} titres")
    print(f"  - Catégories : {df['category'].nunique()}")
    print(f"\nRépartition :")
    print(df['category'].value_counts().sort_index())

    # Afficher quelques exemples
    print("\n--- Exemples de titres par catégorie ---")
    for category in sorted(df['category'].unique()):
        examples = df[df['category'] == category].head(3)
        print(f"\n{category.upper()}:")
        for _, row in examples.iterrows():
            print(f"  • {row['title']}")


if __name__ == "__main__":
    main()
