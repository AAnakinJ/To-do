# -*- coding: utf-8 -*-
"""
To-Do hebdomadaire — une liste de taches par jour, jamais reinitialisee.

- Chaque jour de la semaine a sa propre liste de taches.
- Tout est conserve indefiniment dans un fichier JSON (aucune remise a zero).
- Le lundi a 00:01, le bilan de la semaine ecoulee s'affiche automatiquement :
  un diagramme circulaire avec le pourcentage de taches accomplies + le detail
  jour par jour.
- Un historique permet de revoir le bilan de n'importe quelle semaine passee.
- Interface disponible en francais et en anglais (bouton d'en-tete, Ctrl+L,
  ou --lang en) ; le choix est memorise dans le fichier de donnees.

Aucune dependance externe : uniquement la bibliotheque standard (tkinter).

Lancement :   python todo_semaine.py
En anglais :  python todo_semaine.py --lang en
Auto-tests :  python todo_semaine.py --test
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

import tkinter as tk
from tkinter import font as tkfont
from tkinter import simpledialog

# --------------------------------------------------------------------------- #
#  Configuration
# --------------------------------------------------------------------------- #

DOSSIER = os.path.dirname(os.path.abspath(__file__))
FICHIER_DONNEES = os.path.join(DOSSIER, "todo_data.json")

# Palette
BG = "#161a25"
PANEL = "#20263a"
PANEL_WE = "#1c2134"
PANEL2 = "#272e45"
BORD = "#333c58"
TXT = "#e9edf7"
MUTED = "#8d97b0"
ACCENT = "#5b8cff"
VERT = "#3ddc97"
ORANGE = "#f7b955"
ROUGE = "#f2686a"

POLICE = "Segoe UI"

# Intervalle de verification du passage a la semaine suivante (ms)
PERIODE_VERIF = 30_000


# --------------------------------------------------------------------------- #
#  Traductions (francais / anglais)
# --------------------------------------------------------------------------- #

LANGUES = ("fr", "en")
LANGUE_DEFAUT = "fr"

TEXTES: dict[str, dict[str, object]] = {
    "fr": {
        "titre_app": "To-Do hebdomadaire",
        "jours": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi",
                  "Samedi", "Dimanche"],
        "jours_courts": ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
        "mois": ["janvier", "février", "mars", "avril", "mai", "juin",
                 "juillet", "août", "septembre", "octobre", "novembre",
                 "décembre"],
        "mois_courts": ["janv.", "févr.", "mars", "avr.", "mai", "juin",
                        "juil.", "août", "sept.", "oct.", "nov.", "déc."],
        # {jour}, {mois} et {mois_court} sont fournis : chaque langue choisit.
        "date_courte": "{jour:02d}/{mois:02d}",
        "langue_bouton": "English",
        "semaine_en_cours": "semaine en cours",
        "aujourdhui": "Aujourd'hui",
        "bouton_bilan": "Bilan de cette semaine",
        "historique": "Historique",
        "colonne_vide": "aucune tâche",
        "placeholder": "+ nouvelle tâche",
        "menu_renommer": "Renommer...",
        "menu_reporter": "Reporter au lendemain",
        "menu_supprimer": "Supprimer",
        "dlg_renommer_titre": "Renommer la tâche",
        "dlg_renommer_invite": "Nouveau libellé :",
        "pied_accomplies": "{faites} / {total} tâches accomplies  ·  {pct} %",
        "pied_vide": "Aucune tâche cette semaine",
        "pied_aide": ("Clic = fait/à faire   ·   Clic droit = options"
                      "   ·   Ctrl+← / Ctrl+→ = semaines"),
        "bilan_fenetre": "Bilan de la semaine",
        "bilan_auto": "Semaine terminée !",
        "bilan_manuel": "Bilan de semaine",
        "bilan_taux": "TAUX D'ACCOMPLISSEMENT",
        "bilan_detail": "DÉTAIL PAR JOUR",
        "bilan_vide": "aucune tâche",
        "bilan_sur_total": "{faites} / {total} tâches",
        "carte_creees": "Tâches créées",
        "carte_accomplies": "Accomplies",
        "carte_restantes": "Non terminées",
        "carte_meilleur": "Meilleur jour",
        "fermer": "Fermer",
        "histo_fenetre": "Historique des semaines",
        "histo_bouton": "Historique des semaines",
        "histo_titre": "Historique",
        "histo_aide": "Double-cliquez sur une semaine pour voir son bilan.",
        "histo_vide": "Aucune tâche enregistrée pour l'instant.",
        "histo_voir": "Voir le bilan",
    },
    "en": {
        "titre_app": "Weekly To-Do",
        "jours": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                  "Saturday", "Sunday"],
        "jours_courts": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "mois": ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November",
                 "December"],
        "mois_courts": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "date_courte": "{mois_court} {jour}",
        "langue_bouton": "Français",
        "semaine_en_cours": "current week",
        "aujourdhui": "Today",
        "bouton_bilan": "This week's report",
        "historique": "History",
        "colonne_vide": "no task",
        "placeholder": "+ new task",
        "menu_renommer": "Rename...",
        "menu_reporter": "Move to next day",
        "menu_supprimer": "Delete",
        "dlg_renommer_titre": "Rename task",
        "dlg_renommer_invite": "New label:",
        "pied_accomplies": "{faites} / {total} tasks completed  ·  {pct} %",
        "pied_vide": "No task this week",
        "pied_aide": ("Click = done/to do   ·   Right-click = options"
                      "   ·   Ctrl+← / Ctrl+→ = weeks"),
        "bilan_fenetre": "Weekly report",
        "bilan_auto": "Week complete!",
        "bilan_manuel": "Weekly report",
        "bilan_taux": "COMPLETION RATE",
        "bilan_detail": "DAY BY DAY",
        "bilan_vide": "no task",
        "bilan_sur_total": "{faites} / {total} tasks",
        "carte_creees": "Tasks created",
        "carte_accomplies": "Completed",
        "carte_restantes": "Unfinished",
        "carte_meilleur": "Best day",
        "fermer": "Close",
        "histo_fenetre": "Week history",
        "histo_bouton": "Week history",
        "histo_titre": "History",
        "histo_aide": "Double-click a week to open its report.",
        "histo_vide": "No task recorded yet.",
        "histo_voir": "Open report",
    },
}

_langue = LANGUE_DEFAUT


def definir_langue(code: str) -> None:
    global _langue
    _langue = code if code in LANGUES else LANGUE_DEFAUT


def langue() -> str:
    return _langue


def t(cle: str, **kw) -> str:
    """Texte traduit dans la langue courante (repli sur le francais)."""
    valeur = TEXTES[_langue].get(cle, TEXTES[LANGUE_DEFAUT].get(cle, cle))
    return valeur.format(**kw) if kw else valeur


def noms_jours(courts: bool = False) -> list[str]:
    return TEXTES[_langue]["jours_courts" if courts else "jours"]


def noms_mois(courts: bool = False) -> list[str]:
    return TEXTES[_langue]["mois_courts" if courts else "mois"]


# --------------------------------------------------------------------------- #
#  Utilitaires de dates / semaines
# --------------------------------------------------------------------------- #

def lundi_de(jour: date) -> date:
    """Lundi de la semaine contenant `jour`."""
    return jour - timedelta(days=jour.weekday())


def cle_semaine(lundi: date) -> str:
    """Cle triable d'une semaine, ex. '2026-W31'."""
    annee, semaine, _ = lundi.isocalendar()
    return f"{annee}-W{semaine:02d}"


def jours_semaine(lundi: date) -> list[date]:
    return [lundi + timedelta(days=i) for i in range(7)]


def jour_court(jour: date) -> str:
    """Date compacte de l'en-tete de colonne ('27/07' en fr, 'Jul 27' en en)."""
    return t("date_courte", jour=jour.day, mois=jour.month,
             mois_court=noms_mois(courts=True)[jour.month - 1])


def libelle_semaine(lundi: date) -> str:
    dimanche = lundi + timedelta(days=6)
    mois = noms_mois()
    if lundi.month == dimanche.month:
        return (f"{lundi.day} - {dimanche.day} {mois[dimanche.month - 1]} "
                f"{dimanche.year}")
    if lundi.year == dimanche.year:
        return (f"{lundi.day} {mois[lundi.month - 1]} - "
                f"{dimanche.day} {mois[dimanche.month - 1]} {dimanche.year}")
    return (f"{lundi.day} {mois[lundi.month - 1]} {lundi.year} - "
            f"{dimanche.day} {mois[dimanche.month - 1]} {dimanche.year}")


def couleur_pct(pct: float) -> str:
    """Couleur associee a un taux de reussite (0.0 -> 1.0)."""
    if pct >= 0.8:
        return VERT
    if pct >= 0.5:
        return ACCENT
    if pct >= 0.25:
        return ORANGE
    return ROUGE


# --------------------------------------------------------------------------- #
#  Stockage
# --------------------------------------------------------------------------- #

class Store:
    """Persistance des taches dans un fichier JSON.

    Les taches sont indexees par date ISO ('2026-07-30'). Rien n'est jamais
    supprime automatiquement : la fin de semaine ne remet aucune liste a zero.
    """

    VERSION = 1

    def __init__(self, chemin: str | None = FICHIER_DONNEES):
        self.chemin = chemin              # None => stockage en memoire (tests)
        self.taches: dict[str, list[dict]] = {}
        self.dernier_bilan: str | None = None   # derniere semaine deja bilantee
        self.langue = LANGUE_DEFAUT             # langue d'interface memorisee
        self.charger()

    # -- fichier ----------------------------------------------------------- #

    def charger(self) -> None:
        if not self.chemin or not os.path.exists(self.chemin):
            return
        try:
            with open(self.chemin, "r", encoding="utf-8") as f:
                brut = json.load(f)
        except (OSError, ValueError):
            # Fichier illisible : on le met de cote plutot que de l'ecraser.
            try:
                os.replace(self.chemin, self.chemin + ".corrompu")
            except OSError:
                pass
            return

        self.dernier_bilan = brut.get("dernier_bilan")
        if brut.get("langue") in LANGUES:
            self.langue = brut["langue"]
        taches = brut.get("taches", {})
        if isinstance(taches, dict):
            for jour, elements in taches.items():
                if isinstance(elements, list):
                    self.taches[jour] = [x for x in elements
                                         if isinstance(x, dict)]

    def sauver(self) -> None:
        if not self.chemin:
            return
        donnees = {
            "version": self.VERSION,
            "langue": self.langue,
            "dernier_bilan": self.dernier_bilan,
            "taches": {j: l for j, l in sorted(self.taches.items()) if l},
        }
        tmp = self.chemin + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.chemin)

    # -- taches ------------------------------------------------------------ #

    def liste(self, jour: date) -> list[dict]:
        return self.taches.get(jour.isoformat(), [])

    def ajouter(self, jour: date, texte: str) -> None:
        texte = texte.strip()
        if not texte:
            return
        self.taches.setdefault(jour.isoformat(), []).append({
            "id": uuid.uuid4().hex[:12],
            "texte": texte,
            "fait": False,
            "cree_le": datetime.now().isoformat(timespec="seconds"),
            "fait_le": None,
        })
        self.sauver()

    def basculer(self, jour: date, tid: str) -> None:
        for tache in self.liste(jour):
            if tache["id"] == tid:
                tache["fait"] = not tache.get("fait", False)
                tache["fait_le"] = (datetime.now().isoformat(timespec="seconds")
                                    if tache["fait"] else None)
                break
        self.sauver()

    def renommer(self, jour: date, tid: str, texte: str) -> None:
        texte = texte.strip()
        if not texte:
            return
        for tache in self.liste(jour):
            if tache["id"] == tid:
                tache["texte"] = texte
                break
        self.sauver()

    def supprimer(self, jour: date, tid: str) -> None:
        cle = jour.isoformat()
        if cle in self.taches:
            self.taches[cle] = [x for x in self.taches[cle] if x["id"] != tid]
            if not self.taches[cle]:
                del self.taches[cle]
        self.sauver()

    def deplacer(self, source: date, tid: str, cible: date) -> None:
        """Reporte une tache sur un autre jour."""
        for tache in list(self.liste(source)):
            if tache["id"] == tid:
                self.supprimer(source, tid)
                self.taches.setdefault(cible.isoformat(), []).append(tache)
                self.sauver()
                return

    # -- semaines ---------------------------------------------------------- #

    def semaines_connues(self) -> dict[str, date]:
        """{cle_semaine: lundi} pour toutes les semaines contenant des taches."""
        res: dict[str, date] = {}
        for iso, liste in self.taches.items():
            if not liste:
                continue
            try:
                lundi = lundi_de(date.fromisoformat(iso))
            except ValueError:
                continue
            res[cle_semaine(lundi)] = lundi
        return res


# --------------------------------------------------------------------------- #
#  Statistiques
# --------------------------------------------------------------------------- #

@dataclass
class StatsJour:
    jour: date
    total: int
    faites: int

    @property
    def pct(self) -> float:
        return self.faites / self.total if self.total else 0.0


@dataclass
class StatsSemaine:
    lundi: date
    jours: list[StatsJour]

    @property
    def total(self) -> int:
        return sum(j.total for j in self.jours)

    @property
    def faites(self) -> int:
        return sum(j.faites for j in self.jours)

    @property
    def restantes(self) -> int:
        return self.total - self.faites

    @property
    def pct(self) -> float:
        return self.faites / self.total if self.total else 0.0

    @property
    def meilleur_jour(self) -> StatsJour | None:
        candidats = [j for j in self.jours if j.total]
        if not candidats:
            return None
        return max(candidats, key=lambda j: (j.pct, j.faites))


def stats_semaine(store: Store, lundi: date) -> StatsSemaine:
    jours = []
    for jour in jours_semaine(lundi):
        liste = store.liste(jour)
        jours.append(StatsJour(jour, len(liste),
                               sum(1 for x in liste if x.get("fait"))))
    return StatsSemaine(lundi, jours)


# --------------------------------------------------------------------------- #
#  Declenchement du bilan (lundi 00:01)
# --------------------------------------------------------------------------- #

def bilan_en_attente(store: Store,
                     maintenant: datetime | None = None
                     ) -> tuple[date | None, str | None]:
    """Determine s'il faut afficher un bilan de fin de semaine.

    Renvoie (lundi_a_afficher, cle_a_memoriser) :
      - (None, None)  : rien a faire (semaine en cours, ou bilan deja fait) ;
      - (None, cle)   : rien a montrer (aucune tache) mais on marque la semaine ;
      - (lundi, cle)  : afficher le bilan de la semaine commencant a `lundi`.

    La bascule a lieu le lundi a 00:01 : avant cette minute, la semaine
    precedente n'est pas encore consideree comme cloturee.
    """
    maintenant = maintenant or datetime.now()
    lundi_courant = lundi_de(maintenant.date())
    seuil = datetime.combine(lundi_courant, time(0, 1))
    if maintenant < seuil:
        return None, None

    lundi_precedent = lundi_courant - timedelta(days=7)
    cle_precedente = cle_semaine(lundi_precedent)
    if store.dernier_bilan is not None and store.dernier_bilan >= cle_precedente:
        return None, None

    # Semaines non encore bilantees et deja terminees, la plus recente d'abord.
    candidates = sorted(
        (cle, lundi) for cle, lundi in store.semaines_connues().items()
        if cle <= cle_precedente
        and (store.dernier_bilan is None or cle > store.dernier_bilan)
    )
    if not candidates:
        return None, cle_precedente
    return candidates[-1][1], cle_precedente


# --------------------------------------------------------------------------- #
#  Widgets utilitaires
# --------------------------------------------------------------------------- #

class Bouton(tk.Label):
    """Petit bouton plat, coherent avec le theme sombre."""

    def __init__(self, parent, texte, commande, *, bg=PANEL2, fg=TXT,
                 survol=None, gras=False, padx=12, pady=6, taille=10):
        super().__init__(parent, text=texte, bg=bg, fg=fg, padx=padx, pady=pady,
                         font=(POLICE, taille, "bold" if gras else "normal"),
                         cursor="hand2")
        self._bg = bg
        self._survol = survol or BORD
        self._commande = commande
        self.bind("<Button-1>", lambda _e: self._commande())
        self.bind("<Enter>", lambda _e: self.configure(bg=self._survol))
        self.bind("<Leave>", lambda _e: self.configure(bg=self._bg))


class CadreDefilant(tk.Frame):
    """Zone defilante verticalement (canvas + frame interieur)."""

    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.barre = tk.Scrollbar(self, orient="vertical",
                                  command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.barre.set)
        self.barre.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.interieur = tk.Frame(self.canvas, bg=bg)
        self._fenetre = self.canvas.create_window((0, 0), window=self.interieur,
                                                  anchor="nw")
        self._dim = (0, 0)
        self.interieur.bind("<Configure>", self._ajuster)
        self.canvas.bind("<Configure>", self._ajuster)
        self.bind_all("<MouseWheel>", self._molette, add="+")

    def _ajuster(self, _e=None):
        """Le contenu occupe toute la hauteur visible, et defile s'il depasse."""
        largeur = self.canvas.winfo_width()
        hauteur = max(self.canvas.winfo_height(), self.interieur.winfo_reqheight())
        if (largeur, hauteur) == self._dim:      # evite une boucle de Configure
            return
        self._dim = (largeur, hauteur)
        self.canvas.itemconfigure(self._fenetre, width=largeur, height=hauteur)
        self.canvas.configure(scrollregion=(0, 0, largeur, hauteur))

    def destroy(self):
        # Cette classe est la seule a poser un bind_all("<MouseWheel>") et il
        # n'en existe qu'une a la fois : on le retire pour ne pas empiler les
        # liaisons a chaque changement de langue (qui reconstruit la fenetre).
        try:
            self.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass
        super().destroy()

    def _molette(self, e):
        if not self.winfo_exists():
            return
        w = self.winfo_containing(e.x_root, e.y_root)
        while w is not None:
            if w is self:
                break
            w = getattr(w, "master", None)
        else:
            return
        self.canvas.yview_scroll(-1 * (e.delta // 120), "units")


# --------------------------------------------------------------------------- #
#  Colonne d'un jour
# --------------------------------------------------------------------------- #

class ColonneJour(tk.Frame):
    def __init__(self, parent, app: "App", index: int):
        self.app = app
        self.index = index
        self.jour: date | None = None
        self.placeholder = t("placeholder")
        self._wrap = 120                 # largeur de retour a la ligne courante
        self._libelles: list[tk.Label] = []
        fond = PANEL_WE if index >= 5 else PANEL
        self._fond = fond
        super().__init__(parent, bg=fond, highlightthickness=1,
                         highlightbackground=BORD)

        entete = tk.Frame(self, bg=fond)
        entete.pack(fill="x", padx=10, pady=(10, 4))
        self.lbl_jour = tk.Label(entete, text=noms_jours()[index], bg=fond, fg=TXT,
                                 font=(POLICE, 11, "bold"), anchor="w")
        self.lbl_jour.pack(side="left")
        self.lbl_compteur = tk.Label(entete, text="", bg=fond, fg=MUTED,
                                     font=(POLICE, 9), anchor="e")
        self.lbl_compteur.pack(side="right")

        self.lbl_date = tk.Label(self, text="", bg=fond, fg=MUTED,
                                 font=(POLICE, 9), anchor="w")
        self.lbl_date.pack(fill="x", padx=10)

        self.jauge = tk.Canvas(self, height=4, bg=fond, highlightthickness=0,
                               bd=0)
        self.jauge.pack(fill="x", padx=10, pady=(6, 8))

        self.zone = tk.Frame(self, bg=fond)
        self.zone.pack(fill="both", expand=True, padx=6)
        self.zone.bind("<Configure>", self._maj_retour_ligne)

        bas = tk.Frame(self, bg=fond)
        bas.pack(fill="x", padx=8, pady=8)
        self.saisie = tk.Entry(bas, bg=PANEL2, fg=MUTED, insertbackground=TXT,
                               relief="flat", font=(POLICE, 10),
                               highlightthickness=1, highlightbackground=BORD,
                               highlightcolor=ACCENT)
        self.saisie.pack(side="left", fill="x", expand=True, ipady=4)
        self.saisie.insert(0, self.placeholder)
        self._vide = True
        self.saisie.bind("<Return>", lambda _e: self._ajouter())
        self.saisie.bind("<FocusIn>", self._entrer_saisie)
        self.saisie.bind("<FocusOut>", self._quitter_saisie)
        Bouton(bas, "+", self._ajouter, bg=ACCENT, survol="#7ba2ff",
               gras=True, padx=8, pady=2, taille=11).pack(side="left", padx=(4, 0))

    # ------------------------------------------------------------------ #

    # -- champ de saisie ------------------------------------------------- #

    def _entrer_saisie(self, _e=None):
        if self._vide:
            self.saisie.delete(0, "end")
            self.saisie.configure(fg=TXT)
            self._vide = False

    def _quitter_saisie(self, _e=None):
        if not self.saisie.get().strip():
            self.saisie.delete(0, "end")
            self.saisie.insert(0, self.placeholder)
            self.saisie.configure(fg=MUTED)
            self._vide = True

    def _maj_retour_ligne(self, e):
        """Estimation de la largeur de repli quand la colonne change de taille."""
        wrap = max(e.width - 58, 60)
        if wrap == self._wrap:
            return
        self._wrap = wrap
        for lbl in self._libelles:
            if lbl.winfo_exists():
                lbl.configure(wraplength=wrap)

    @staticmethod
    def _caler_libelle(e):
        """Cale le repli sur la largeur reellement allouee au libelle.

        Indispensable : si wraplength depasse ne serait-ce que de quelques
        pixels la place reelle, Tk n'enroule pas et rogne la fin du texte.
        """
        lbl = e.widget
        cible = max(e.width - 6, 50)
        if abs(int(lbl.cget("wraplength")) - cible) > 2:
            lbl.configure(wraplength=cible)

    # ------------------------------------------------------------------ #

    def _ajouter(self):
        if self.jour is None or self._vide:
            return
        texte = self.saisie.get()
        if texte.strip():
            self.app.store.ajouter(self.jour, texte)
            self.saisie.delete(0, "end")
            self.app.rafraichir()

    def _menu(self, event, tache: dict):
        menu = tk.Menu(self, tearoff=0, bg=PANEL2, fg=TXT,
                       activebackground=ACCENT, activeforeground="white",
                       font=(POLICE, 9))
        menu.add_command(label=t("menu_renommer"),
                         command=lambda: self._renommer(tache))
        menu.add_command(label=t("menu_reporter"),
                         command=lambda: self._reporter(tache))
        menu.add_separator()
        menu.add_command(label=t("menu_supprimer"),
                         command=lambda: self._supprimer(tache))
        menu.tk_popup(event.x_root, event.y_root)

    def _renommer(self, tache: dict):
        nouveau = simpledialog.askstring(t("dlg_renommer_titre"),
                                         t("dlg_renommer_invite"),
                                         initialvalue=tache["texte"],
                                         parent=self.app)
        if nouveau:
            self.app.store.renommer(self.jour, tache["id"], nouveau)
            self.app.rafraichir()

    def _reporter(self, tache: dict):
        self.app.store.deplacer(self.jour, tache["id"],
                                self.jour + timedelta(days=1))
        self.app.rafraichir()

    def _supprimer(self, tache: dict):
        self.app.store.supprimer(self.jour, tache["id"])
        self.app.rafraichir()

    # ------------------------------------------------------------------ #

    def afficher(self, jour: date, taches: list[dict], aujourdhui: bool):
        self.jour = jour
        fond = self._fond
        self.lbl_date.configure(text=jour_court(jour))
        self.lbl_jour.configure(fg=ACCENT if aujourdhui else TXT)
        self.configure(highlightbackground=ACCENT if aujourdhui else BORD,
                       highlightthickness=2 if aujourdhui else 1)

        faites = sum(1 for x in taches if x.get("fait"))
        total = len(taches)
        self.lbl_compteur.configure(text=f"{faites}/{total}" if total else "")

        # jauge de progression
        self.jauge.delete("all")
        larg = max(self.jauge.winfo_width(), 1)
        self.jauge.create_rectangle(0, 0, larg, 4, fill=PANEL2, outline="")
        if total:
            p = faites / total
            self.jauge.create_rectangle(0, 0, larg * p, 4,
                                        fill=couleur_pct(p), outline="")

        for enfant in self.zone.winfo_children():
            enfant.destroy()
        self._libelles.clear()

        if not total:
            tk.Label(self.zone, text=t("colonne_vide"), bg=fond, fg=BORD,
                     font=(POLICE, 9, "italic")).pack(pady=6)
            return

        for tache in taches:
            fait = bool(tache.get("fait"))
            ligne = tk.Frame(self.zone, bg=fond)
            ligne.pack(fill="x", pady=1)

            case = tk.Label(ligne, text="☑" if fait else "☐", bg=fond,
                            fg=VERT if fait else MUTED, font=(POLICE, 12),
                            cursor="hand2")
            case.pack(side="left", padx=(2, 4))

            # La croix est placee avant le libelle pour que pack lui reserve
            # sa place : sinon le texte l'ecrase dans les colonnes etroites.
            croix = tk.Label(ligne, text="✕", bg=fond, fg=BORD,
                             font=(POLICE, 9), cursor="hand2")
            croix.pack(side="right", padx=(4, 2))

            police = tkfont.Font(family=POLICE, size=10, overstrike=fait)
            libelle = tk.Label(ligne, text=tache["texte"], bg=fond,
                               fg=MUTED if fait else TXT, font=police,
                               wraplength=self._wrap, justify="left", anchor="w",
                               cursor="hand2")
            libelle.pack(side="left", fill="x", expand=True)
            libelle.bind("<Configure>", self._caler_libelle)
            self._libelles.append(libelle)

            for w in (ligne, case, libelle):
                w.bind("<Button-1>", lambda _e, t=tache: self._basculer(t))
                w.bind("<Button-3>", lambda e, t=tache: self._menu(e, t))
            croix.bind("<Button-1>", lambda _e, t=tache: self._supprimer(t))
            croix.bind("<Enter>", lambda e: e.widget.configure(fg=ROUGE))
            croix.bind("<Leave>", lambda e: e.widget.configure(fg=BORD))

    def _basculer(self, tache: dict):
        self.app.store.basculer(self.jour, tache["id"])
        self.app.rafraichir()


# --------------------------------------------------------------------------- #
#  Fenetre de bilan
# --------------------------------------------------------------------------- #

class FenetreBilan(tk.Toplevel):
    LARGEUR_CANVAS = 780
    HAUTEUR_CANVAS = 320

    def __init__(self, master: "App", store: Store, lundi: date,
                 automatique: bool = False):
        super().__init__(master)
        self.store = store
        self.lundi = lundi
        self.stats = stats_semaine(store, lundi)

        self.title(t("bilan_fenetre"))
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(master)

        entete = tk.Frame(self, bg=BG)
        entete.pack(fill="x", padx=24, pady=(20, 0))
        titre = t("bilan_auto") if automatique else t("bilan_manuel")
        tk.Label(entete, text=titre, bg=BG, fg=TXT,
                 font=(POLICE, 17, "bold")).pack(anchor="w")
        tk.Label(entete, text=libelle_semaine(lundi), bg=BG, fg=MUTED,
                 font=(POLICE, 10)).pack(anchor="w", pady=(2, 0))

        self.canvas = tk.Canvas(self, width=self.LARGEUR_CANVAS,
                                height=self.HAUTEUR_CANVAS, bg=BG,
                                highlightthickness=0, bd=0)
        self.canvas.pack(padx=24, pady=(12, 0))
        self._dessiner_anneau()
        self._dessiner_barres()

        self._cartes()

        pied = tk.Frame(self, bg=BG)
        pied.pack(fill="x", padx=24, pady=(14, 20))
        Bouton(pied, t("fermer"), self.destroy, bg=ACCENT, survol="#7ba2ff",
               gras=True, padx=18).pack(side="right")
        Bouton(pied, t("histo_bouton"),
               lambda: FenetreHistorique(master, store)).pack(side="right",
                                                              padx=(0, 8))

        self.update_idletasks()
        self._centrer(master)
        self.bind("<Escape>", lambda _e: self.destroy())
        self.focus_set()

    def _centrer(self, master):
        try:
            x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
            y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        except tk.TclError:
            pass

    # -- diagramme circulaire -------------------------------------------- #

    def _dessiner_anneau(self):
        c = self.canvas
        bbox = (40, 70, 230, 260)
        cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
        epaisseur = 26

        c.create_text(cx, 46, text=t("bilan_taux"), fill=MUTED,
                      font=(POLICE, 9, "bold"))
        c.create_oval(*bbox, outline=PANEL2, width=epaisseur)

        pct = self.stats.pct
        if self.stats.total and pct > 0:
            etendue = -359.99 if pct >= 1 else -360 * pct
            c.create_arc(*bbox, start=90, extent=etendue, style=tk.ARC,
                         outline=couleur_pct(pct), width=epaisseur)

        if self.stats.total:
            c.create_text(cx, cy - 10, text=f"{round(pct * 100)} %", fill=TXT,
                          font=(POLICE, 30, "bold"))
            c.create_text(cx, cy + 20,
                          text=t("bilan_sur_total", faites=self.stats.faites,
                                 total=self.stats.total),
                          fill=MUTED, font=(POLICE, 10))
        else:
            c.create_text(cx, cy, text=t("bilan_vide"), fill=MUTED,
                          font=(POLICE, 11, "italic"))

    # -- histogramme par jour -------------------------------------------- #

    def _dessiner_barres(self):
        c = self.canvas
        x0, x1 = 290, 760
        base, sommet = 258, 92
        hauteur_max = base - sommet
        largeur, ecart = 52, 15

        c.create_text(x0, 46, text=t("bilan_detail"), fill=MUTED, anchor="w",
                      font=(POLICE, 9, "bold"))
        c.create_line(x0 - 6, base, x1, base, fill=BORD)

        for i, sj in enumerate(self.stats.jours):
            gx = x0 + i * (largeur + ecart)
            # Piste de fond : plus discrete pour un jour sans aucune tache.
            c.create_rectangle(gx, sommet, gx + largeur, base,
                               fill=PANEL2 if sj.total else PANEL, outline="")
            if sj.total:
                h = max(hauteur_max * sj.pct, 2)
                c.create_rectangle(gx, base - h, gx + largeur, base,
                                   fill=couleur_pct(sj.pct), outline="")
                c.create_text(gx + largeur / 2, sommet - 12,
                              text=f"{round(sj.pct * 100)}%", fill=TXT,
                              font=(POLICE, 9, "bold"))
                c.create_text(gx + largeur / 2, base + 30,
                              text=f"{sj.faites}/{sj.total}", fill=MUTED,
                              font=(POLICE, 8))
            else:
                c.create_text(gx + largeur / 2, base + 30, text="-", fill=BORD,
                              font=(POLICE, 9))
            c.create_text(gx + largeur / 2, base + 14,
                          text=noms_jours(courts=True)[i], fill=TXT,
                          font=(POLICE, 9, "bold"))

    # -- cartes de synthese ---------------------------------------------- #

    def _cartes(self):
        cadre = tk.Frame(self, bg=BG)
        cadre.pack(fill="x", padx=24, pady=(16, 0))

        meilleur = self.stats.meilleur_jour
        if meilleur is None:
            txt_meilleur = "-"
        else:
            txt_meilleur = (f"{noms_jours()[meilleur.jour.weekday()]} "
                            f"({round(meilleur.pct * 100)}%)")

        cartes = [
            (t("carte_creees"), str(self.stats.total), TXT),
            (t("carte_accomplies"), str(self.stats.faites), VERT),
            (t("carte_restantes"), str(self.stats.restantes),
             ROUGE if self.stats.restantes else MUTED),
            (t("carte_meilleur"), txt_meilleur, ACCENT),
        ]
        for i, (titre, valeur, couleur) in enumerate(cartes):
            cadre.columnconfigure(i, weight=1, uniform="cartes")
            carte = tk.Frame(cadre, bg=PANEL, highlightthickness=1,
                             highlightbackground=BORD)
            carte.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            tk.Label(carte, text=titre.upper(), bg=PANEL, fg=MUTED,
                     font=(POLICE, 8, "bold")).pack(pady=(10, 2))
            tk.Label(carte, text=valeur, bg=PANEL, fg=couleur,
                     font=(POLICE, 14, "bold")).pack(pady=(0, 10))


# --------------------------------------------------------------------------- #
#  Historique
# --------------------------------------------------------------------------- #

class FenetreHistorique(tk.Toplevel):
    def __init__(self, master: "App", store: Store):
        super().__init__(master)
        self.store = store
        self.title(t("histo_fenetre"))
        self.configure(bg=BG)
        self.geometry("520x460")
        self.transient(master)

        tk.Label(self, text=t("histo_titre"), bg=BG, fg=TXT,
                 font=(POLICE, 15, "bold")).pack(anchor="w", padx=20,
                                                 pady=(18, 0))
        tk.Label(self, text=t("histo_aide"),
                 bg=BG, fg=MUTED, font=(POLICE, 9)).pack(anchor="w", padx=20,
                                                         pady=(2, 12))

        # Police a largeur fixe : les colonnes du tableau restent alignees.
        self.liste = tk.Listbox(self, bg=PANEL, fg=TXT, relief="flat",
                                font=("Consolas", 10), selectbackground=ACCENT,
                                selectforeground="white", highlightthickness=0,
                                activestyle="none")
        self.liste.pack(fill="both", expand=True, padx=20)
        self.liste.bind("<Double-Button-1>", lambda _e: self._ouvrir())
        self.liste.bind("<Return>", lambda _e: self._ouvrir())

        self.lundis: list[date] = []
        for _cle, lundi in sorted(store.semaines_connues().items(), reverse=True):
            st = stats_semaine(store, lundi)
            self.lundis.append(lundi)
            self.liste.insert(
                "end",
                f"  {libelle_semaine(lundi):<34}  {round(st.pct * 100):>3} %"
                f"   ({st.faites}/{st.total})")
        if not self.lundis:
            self.liste.insert("end", "  " + t("histo_vide"))

        pied = tk.Frame(self, bg=BG)
        pied.pack(fill="x", padx=20, pady=16)
        Bouton(pied, t("fermer"), self.destroy).pack(side="right")
        Bouton(pied, t("histo_voir"), self._ouvrir, bg=ACCENT,
               survol="#7ba2ff", gras=True).pack(side="right", padx=(0, 8))
        self.bind("<Escape>", lambda _e: self.destroy())

    def _ouvrir(self):
        sel = self.liste.curselection()
        if not sel or not self.lundis:
            return
        FenetreBilan(self.master, self.store, self.lundis[sel[0]])


# --------------------------------------------------------------------------- #
#  Application
# --------------------------------------------------------------------------- #

class App(tk.Tk):
    def __init__(self, store: Store):
        super().__init__()
        self.store = store
        self.lundi = lundi_de(date.today())

        self.title(t("titre_app"))
        self.geometry("1200x740")
        self.minsize(980, 600)
        self.configure(bg=BG)

        self._construire()

        self.bind("<Control-Left>", lambda _e: self._changer_semaine(-1))
        self.bind("<Control-Right>", lambda _e: self._changer_semaine(1))
        self.bind("<Control-b>", lambda _e: self._bilan_semaine_precedente())
        self.bind("<Control-l>", lambda _e: self._basculer_langue())

        self.after(400, self._boucle_verification)

    # -- construction ----------------------------------------------------- #

    def _construire(self):
        self._entete()
        self._tableau()
        self._pied()
        self.rafraichir()

    def _basculer_langue(self):
        """Passe de francais a anglais (et inversement) et reconstruit l'ecran."""
        definir_langue("en" if langue() == "fr" else "fr")
        self.store.langue = langue()
        self.store.sauver()
        # On repart d'une fenetre vierge : cela retraduit tout d'un coup, y
        # compris les eventuels bilans ouverts (qui sont des enfants de self).
        for enfant in self.winfo_children():
            enfant.destroy()
        self.title(t("titre_app"))
        self._construire()

    def _entete(self):
        barre = tk.Frame(self, bg=BG)
        barre.pack(fill="x", padx=20, pady=(18, 10))

        gauche = tk.Frame(barre, bg=BG)
        gauche.pack(side="left")
        tk.Label(gauche, text=t("titre_app"), bg=BG, fg=TXT,
                 font=(POLICE, 18, "bold")).pack(anchor="w")
        self.lbl_semaine = tk.Label(gauche, text="", bg=BG, fg=MUTED,
                                    font=(POLICE, 10))
        self.lbl_semaine.pack(anchor="w", pady=(2, 0))

        droite = tk.Frame(barre, bg=BG)
        droite.pack(side="right")
        Bouton(droite, t("langue_bouton"), self._basculer_langue,
               taille=9).pack(side="right")
        Bouton(droite, t("historique"),
               lambda: FenetreHistorique(self, self.store)).pack(side="right",
                                                                 padx=(0, 8))
        Bouton(droite, t("bouton_bilan"),
               self._bilan_semaine_affichee, bg=ACCENT, survol="#7ba2ff",
               gras=True).pack(side="right", padx=(0, 8))

        nav = tk.Frame(barre, bg=BG)
        nav.pack(side="right", padx=(0, 24))
        Bouton(nav, "◀", lambda: self._changer_semaine(-1),
               padx=10).pack(side="left")
        Bouton(nav, t("aujourdhui"), self._revenir_aujourdhui).pack(side="left",
                                                                    padx=6)
        Bouton(nav, "▶", lambda: self._changer_semaine(1),
               padx=10).pack(side="left")

    def _tableau(self):
        zone = CadreDefilant(self, bg=BG)
        zone.pack(fill="both", expand=True, padx=14)
        grille = zone.interieur
        self.colonnes: list[ColonneJour] = []
        for i in range(7):
            grille.columnconfigure(i, weight=1, uniform="jours", minsize=150)
            col = ColonneJour(grille, self, i)
            col.grid(row=0, column=i, sticky="nsew", padx=3, pady=3)
            self.colonnes.append(col)
        grille.rowconfigure(0, weight=1)

    def _pied(self):
        pied = tk.Frame(self, bg=BG)
        pied.pack(fill="x", padx=20, pady=(6, 14))
        self.lbl_total = tk.Label(pied, text="", bg=BG, fg=MUTED,
                                  font=(POLICE, 10))
        self.lbl_total.pack(side="left")
        tk.Label(pied, text=t("pied_aide"),
                 bg=BG, fg=BORD, font=(POLICE, 9)).pack(side="right")

    # -- navigation ------------------------------------------------------- #

    def _changer_semaine(self, delta: int):
        self.lundi += timedelta(days=7 * delta)
        self.rafraichir()

    def _revenir_aujourdhui(self):
        self.lundi = lundi_de(date.today())
        self.rafraichir()

    # -- rafraichissement ------------------------------------------------- #

    def rafraichir(self):
        aujourdhui = date.today()
        courante = lundi_de(aujourdhui) == self.lundi
        suffixe = ("  ·  " + t("semaine_en_cours")) if courante else ""
        self.lbl_semaine.configure(text=libelle_semaine(self.lundi) + suffixe)

        for col, jour in zip(self.colonnes, jours_semaine(self.lundi)):
            col.afficher(jour, self.store.liste(jour), jour == aujourdhui)

        st = stats_semaine(self.store, self.lundi)
        if st.total:
            self.lbl_total.configure(
                text=t("pied_accomplies", faites=st.faites, total=st.total,
                       pct=round(st.pct * 100)),
                fg=couleur_pct(st.pct))
        else:
            self.lbl_total.configure(text=t("pied_vide"), fg=MUTED)

    # -- bilans ----------------------------------------------------------- #

    def _bilan_semaine_affichee(self):
        FenetreBilan(self, self.store, self.lundi)

    def _bilan_semaine_precedente(self):
        FenetreBilan(self, self.store, self.lundi - timedelta(days=7))

    def _boucle_verification(self):
        """Verifie periodiquement le passage du lundi 00:01."""
        try:
            self._verifier_bilan()
        finally:
            self.after(PERIODE_VERIF, self._boucle_verification)

    def _verifier_bilan(self):
        lundi, cle = bilan_en_attente(self.store)
        if cle is None:
            return
        self.store.dernier_bilan = cle
        self.store.sauver()
        if lundi is None:
            return          # semaine ecoulee sans aucune tache : rien a montrer
        # On recale l'affichage sur la semaine courante puis on montre le bilan.
        self.lundi = lundi_de(date.today())
        self.rafraichir()
        FenetreBilan(self, self.store, lundi, automatique=True)


# --------------------------------------------------------------------------- #
#  Auto-tests de la logique de fin de semaine
# --------------------------------------------------------------------------- #

def _tests() -> int:
    echecs = []

    def verifier(nom, obtenu, attendu):
        if obtenu != attendu:
            echecs.append(f"{nom}: obtenu {obtenu!r}, attendu {attendu!r}")
        else:
            print(f"  ok  {nom}")

    # Semaine du lundi 20 juillet 2026 au dimanche 26 juillet 2026.
    lundi_p = date(2026, 7, 20)

    def store_avec(taches_jours, dernier=None):
        s = Store(chemin=None)
        s.dernier_bilan = dernier
        for jour, (total, faites) in taches_jours.items():
            s.taches[jour.isoformat()] = [
                {"id": str(i), "texte": f"t{i}", "fait": i < faites}
                for i in range(total)
            ]
        return s

    # Semaines precedentes deja bilantees jusqu'a W29 incluse.
    s = store_avec({lundi_p: (4, 3), lundi_p + timedelta(days=2): (2, 0)},
                   dernier="2026-W29")

    verifier("sunday 23:59 -> no report",
             bilan_en_attente(s, datetime(2026, 7, 26, 23, 59)), (None, None))
    verifier("monday 00:00 -> not yet",
             bilan_en_attente(s, datetime(2026, 7, 27, 0, 0)), (None, None))
    verifier("monday 00:01 -> report for the week just ended",
             bilan_en_attente(s, datetime(2026, 7, 27, 0, 1)),
             (lundi_p, "2026-W30"))
    verifier("monday 09:00 -> report still pending",
             bilan_en_attente(s, datetime(2026, 7, 27, 9, 0)),
             (lundi_p, "2026-W30"))

    s.dernier_bilan = "2026-W30"
    verifier("already shown -> nothing again",
             bilan_en_attente(s, datetime(2026, 7, 27, 9, 0)), (None, None))
    verifier("next week triggers again",
             bilan_en_attente(s, datetime(2026, 8, 3, 0, 1)),
             (None, "2026-W31"))    # semaine W31 sans tache : marquee, non montree

    vide = store_avec({})
    verifier("no task at all -> marked, not shown",
             bilan_en_attente(vide, datetime(2026, 7, 27, 0, 1)),
             (None, "2026-W30"))

    # Absence prolongee : la derniere semaine non vide est retenue.
    ancien = store_avec({date(2026, 7, 7): (5, 5), lundi_p: (3, 1)})
    verifier("several weeks away -> latest week holding tasks",
             bilan_en_attente(ancien, datetime(2026, 7, 27, 0, 1)),
             (lundi_p, "2026-W30"))

    # Les listes ne sont jamais purgees.
    verifier("past tasks are kept",
             len(ancien.liste(date(2026, 7, 7))), 5)

    # -- traductions ------------------------------------------------------ #

    verifier("both languages define the same keys",
             sorted(TEXTES["fr"]) == sorted(TEXTES["en"]), True)
    verifier("no empty translation",
             [c for c in TEXTES["en"] if not TEXTES["en"][c]], [])
    for code in LANGUES:
        definir_langue(code)
        verifier(f"[{code}] 7 day names", len(noms_jours()), 7)
        verifier(f"[{code}] 12 month names", len(noms_mois()), 12)
        verifier(f"[{code}] placeholders are filled",
                 "{" in t("pied_accomplies", faites=1, total=2, pct=50), False)

    definir_langue("en")
    verifier("[en] monday label", noms_jours()[0], "Monday")
    verifier("[en] week label", libelle_semaine(lundi_p), "20 - 26 July 2026")
    verifier("[en] short date", jour_court(lundi_p), "Jul 20")
    definir_langue("fr")
    verifier("[fr] week label", libelle_semaine(lundi_p), "20 - 26 juillet 2026")
    verifier("[fr] short date", jour_court(lundi_p), "20/07")
    verifier("unknown code falls back to french",
             (definir_langue("de"), langue())[1], "fr")

    # Persistance sur disque (taches + langue choisie).
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        chemin = os.path.join(tmp, "d.json")
        a = Store(chemin)
        a.langue = "en"
        a.ajouter(date(2026, 7, 30), "acheter du pain")
        tid = a.liste(date(2026, 7, 30))[0]["id"]
        a.basculer(date(2026, 7, 30), tid)
        b = Store(chemin)
        verifier("reloaded after save",
                 [(x["texte"], x["fait"]) for x in b.liste(date(2026, 7, 30))],
                 [("acheter du pain", True)])
        verifier("language remembered", b.langue, "en")

    print()
    if echecs:
        for e in echecs:
            print("FAILED:", e)
        return 1
    print("All tests pass.")
    return 0


# --------------------------------------------------------------------------- #

def langue_demandee(argv: list[str]) -> str | None:
    """Lit '--lang en' ou '--lang=en' sur la ligne de commande."""
    for i, arg in enumerate(argv):
        if arg.startswith("--lang="):
            return arg.split("=", 1)[1]
        if arg == "--lang" and i + 1 < len(argv):
            return argv[i + 1]
    return None


def main() -> int:
    if "--test" in sys.argv:
        return _tests()

    store = Store(FICHIER_DONNEES)
    demandee = langue_demandee(sys.argv)
    if demandee in LANGUES:            # --lang a la priorite et est memorise
        store.langue = demandee
        store.sauver()
    definir_langue(store.langue)

    app = App(store)
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
