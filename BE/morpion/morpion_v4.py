
from __future__ import annotations

import sys
from collections import defaultdict, deque
from random import choice
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from utils import Case


class Morpion():

    JOUEURS = ['croix', 'rond']

    def __init__(self, dimension: int, player1='humain', player2='humain'):
        self.dimension = dimension
        self.cases_per_joueur = self.dimension
        self.cases_a_la_suite_gagnants = self.dimension
        self.joueurs = {
            'croix': player1,
            'rond': player2,
        }
        self.silent = False

        self.cases_vides: list[Case]
        self.joueur_actuel: str
        self.nombre_tour: int
        self.coords_joueur: dict[str, list[Case]]
        self.case_videe: Union[None, Case]
        self.vainqueur: Union[None, str]
        self.etats_precedents: deque[tuple[tuple[Case], ...]]
        self.res_stack = []

        self.reinitialiser()

    def reinitialiser(self):
        """Réinitialiser le morpion
        """
        self.cases_vides = [(i, j) for i in range(self.dimension) for j in range(self.dimension)]
        self.joueur_actuel = choice(self.JOUEURS)
        self.nombre_tour = 0
        self.coords_joueur = {joueur: [] for joueur in self.JOUEURS}
        self.case_videe = None
        self.vainqueur = None
        self.etats_precedents = deque((tuple(), tuple(), tuple()))

    def quitter(self):
        sys.exit(0)

    def commencer(self):
        self.log('Morpion !')
        self.log(f'Dimension = {self.dimension}')
        self.jouer()

    # Fonctions principales

    def jouer(self):
        # Choisir une joueur
        self.joueur_actuel = choice(self.JOUEURS)
        fini = False
        while not fini:
            self.log(f'Joueur actuel: {self.joueur_actuel} ({self.joueurs[self.joueur_actuel]})')
            self.print_matrice()
            case_placee = self.placer_un_pion()
            if case_placee:
                fini = self.gagnant(case_placee)
                if not fini:
                    self.basculer_joueur()
        self.vainqueur = self.joueur_actuel
        self.print_matrice()
        self.log(f'Joueur {self.vainqueur} a gagné !')

    def placer_un_pion(self):
        joueur_est_humain = self.joueurs[self.joueur_actuel] == 'humain'
        if not self.joueur_peut_ajouter_nouvelle_forme(self.joueur_actuel):
            # retirer pion
            if joueur_est_humain:
                case_choisi = self.get_input()
                if not self.essai_marquer_case(case_choisi):
                    return None
            else:
                if not self.essai_marquer_case(self.jouer_ia()):
                    return None
            self.print_matrice()
        # ajouter pion
        if joueur_est_humain:
            case_choisi = self.get_input()
            if self.essai_marquer_case(case_choisi):
                return case_choisi
        else:
            case_choisi = self.jouer_ia()
            if self.essai_marquer_case(case_choisi):
                return case_choisi
        return None

    def gagnant(self, case_placee: Case) -> bool:
        fil, col = case_placee
        cases_joueur = self.coords_joueur[self.joueur_actuel]
        if self.get_nombre_cases_occupees_du_joueur(self.joueur_actuel) < self.dimension:
            return False
        # check file
        cases_a_la_suite = 1
        # check left
        for j in range(col - 1, -1, -1):
            if (fil, j) in cases_joueur:
                cases_a_la_suite += 1
            else:
                break
        # check right
        for j in range(col + 1, self.dimension):
            if (fil, j) in cases_joueur:
                cases_a_la_suite += 1
            else:
                break
        if cases_a_la_suite == self.cases_a_la_suite_gagnants:
            return True
        # check colonne
        cases_a_la_suite = 1
        # check up
        for i in range(fil - 1, -1, -1):
            if (i, col) in cases_joueur:
                cases_a_la_suite += 1
            else:
                break
        # check down
        for i in range(fil + 1, self.dimension):
            if (i, col) in cases_joueur:
                cases_a_la_suite += 1
            else:
                break
        if cases_a_la_suite == self.cases_a_la_suite_gagnants:
            return True
        # check diag 1
        cases_a_la_suite = 1
        # check up-left
        for k in range(1, min(fil, col) + 1):
            if (fil - k, col - k) in cases_joueur:
                cases_a_la_suite += 1
            else:
                break
        # check down-right
        for k in range(1, self.dimension - max(fil, col)):
            if (fil + k, col + k) in cases_joueur:
                cases_a_la_suite += 1
            else:
                break
        if cases_a_la_suite == self.cases_a_la_suite_gagnants:
            return True
        # check diag 2
        cases_a_la_suite = 1
        # check up-right
        for k in range(1, min(fil, self.dimension - col) + 1):
            if (fil - k, col + k) in cases_joueur:
                cases_a_la_suite += 1
            else:
                break
        # check down-left
        for k in range(1, min(self.dimension - fil, col) + 1):
            if (fil + k, col - k) in cases_joueur:
                cases_a_la_suite += 1
            else:
                break
        if cases_a_la_suite == self.cases_a_la_suite_gagnants:
            return True
        return False

    # Fonctions morpion

    def enregistrer_etat(self):
        entity = [tuple(self.coords_joueur[k]) for k in self.coords_joueur]
        entity.append(tuple(self.cases_vides))
        self.etats_precedents.append(tuple(entity))
        if len(self.etats_precedents) > 3:
            self.etats_precedents.popleft()

    def essai_marquer_case(self, case: Case) -> Union[bool, tuple[Case, Union[str, None]]]:
        res = self._essai_marquer_case(case)
        if res is False:
            self.log(f'Choix {case} invalide ! ', end='')
            if self.joueur_peut_ajouter_nouvelle_forme(self.joueur_actuel):
                if self.case_videe == case:
                    self.log('Veuillez choisir une case différente !')
                else:
                    self.log('Veuillez choisir une case vide !')
            else:
                self.log('Veuillez choisir une de vos cases !')
        elif isinstance(res, tuple):
            self.log(f'Choix {case} valide ! ')
            case, forme = res
            if forme is None:
                self.log(f'Case {case} effacée')
            else:
                self.log(f'Case {case} marquée avec {forme}')
        return res

    def _essai_marquer_case(self, case: Case) -> Union[bool, tuple[Case, Union[str, None]]]:
        if (self.case_est_libre(case) and
                self.joueur_peut_ajouter_nouvelle_forme(self.joueur_actuel) and
                self.case_videe != case):
            self.marquer_case(case, self.joueur_actuel)
            self.case_videe = None
            self.enregistrer_etat()
            return case, self.joueur_actuel
        if (self.case_videe is None and
            not self.joueur_peut_ajouter_nouvelle_forme(self.joueur_actuel) and
                self.case_est_de_joueur(case, self.joueur_actuel)):
            self.liberer_case(case, self.joueur_actuel)
            self.case_videe = case
            return case, None
        return False

    def joueur_peut_ajouter_nouvelle_forme(self, joueur: str) -> bool:
        """Vérifier si le joueur peut ajouter une nouvelle forme (remplir une nouvelle case)

        Args:
            joueur (str): Joueur

        Returns:
            bool: True si le joueur peut ajouter une nouvelle forme, sinon False
        """
        return self.get_nombre_cases_occupees_du_joueur(joueur) < self.cases_per_joueur

    def get_nombre_cases_occupees_du_joueur(self, joueur: str) -> int:
        """Obtenir le nombre de cases occupées par le joueur

        Args:
            joueur (str): Joueur

        Returns:
            int: Nombre de cases occupées par le joueur
        """
        return len(self.coords_joueur[joueur])

    def case_est_libre(self, case: Case) -> bool:
        """Vérifier si la case est vide

        Args:
            case (Case): Case à vérifier

        Returns:
            bool: True si la case est vide, sinon False
        """
        return case in self.cases_vides

    def case_est_de_joueur(self, case: Case, joueur: str) -> bool:
        """Vérifier si la case appartient au joueur

        Args:
            case (Case): Case à vérifier
            joueur (str): Joueur

        Returns:
            bool: True si la case appartient au joueur, sinon False
        """
        return case in self.coords_joueur[joueur]

    def marquer_case(self, case: Case, joueur: str):
        """Marquer une case

        Args:
            case (Case): Case à marquer
            joueur (str): Joueur
        """
        self.cases_vides.remove(case)
        self.coords_joueur[joueur].append(case)

    def liberer_case(self, case: Case, joueur: str):
        """Libérer une case

        Args:
            case (Case): Case à marquer
            joueur (str): Joueur
        """
        self.coords_joueur[joueur].remove(case)
        self.cases_vides.append(case)

    def basculer_joueur(self):
        """Changer le joueur actuel
        """
        self.joueur_actuel = 'rond' if self.joueur_actuel == 'croix' else 'croix'

    # Fonctions IA

    def jouer_ia(self):
        if len(self.res_stack) != 0:
            return self.res_stack.pop()
        self.res_stack.extend(self.best_first())
        return self.res_stack.pop()

    def best_first(self):
        valeurs = defaultdict(list)
        if self.joueur_peut_ajouter_nouvelle_forme(self.joueur_actuel):
            for case in self.cases_vides:
                valeurs[self.obtenir_valeur_case(case)].append((case,))
        else:
            for case_a_enlever in [*self.coords_joueur[self.joueur_actuel]]:
                cases_vides_avant = [*self.cases_vides]
                self.liberer_case(case_a_enlever, self.joueur_actuel)
                for case_a_placer in cases_vides_avant:
                    valeurs[self.obtenir_valeur_case(case_a_placer)].append(
                        (case_a_placer, case_a_enlever))
                self.marquer_case(case_a_enlever, self.joueur_actuel)
        best = valeurs[max(valeurs)]
        # privilégier diag
        best_diags = list(filter(lambda x: x[0][0] == x[0][1]
                          or x[0][0] + x[0][1] == self.dimension - 1, best))
        if best_diags:
            return choice(best_diags)
        return choice(best)

    def obtenir_valeur_case(self, case: Case):
        nl = self.nombre_pions_ligne(case)
        nc = self.nombre_pions_colonne(case)
        nd1 = self.nombre_pions_diag_1(case)
        nd2 = self.nombre_pions_diag_2(case)
        autre = 'croix' if self.joueur_actuel == 'rond' else 'rond'
        nl_1 = nl[self.joueur_actuel]
        nc_1 = nc[self.joueur_actuel]
        nd1_1 = nd1[self.joueur_actuel]
        nd2_1 = nd2[self.joueur_actuel]
        nl_2 = nl[autre]
        nc_2 = nc[autre]
        nd1_2 = nd1[autre]
        nd2_2 = nd2[autre]
        facteur_nl = -1 if nl_2 > nl_1 else 1
        facteur_nc = -1 if nc_2 > nc_1 else 1
        facteur_nd1 = -1 if nd1_2 > nd1_1 else 1
        facteur_nd2 = -1 if nd2_2 > nd2_1 else 1
        g = facteur_nl * (nl_1 - nl_2)**2 + facteur_nc * (nc_1 - nc_2)**2 + \
            facteur_nd1 * (nd1_1 - nd1_2)**2 + facteur_nd2 * (nd2_1 - nd2_2)**2
        return g

    def nombre_pions_ligne(self, case: Case):
        compteur = {'croix': 0, 'rond': 0}
        i = case[0]
        for j in range(self.dimension):
            if (i, j) in self.coords_joueur['croix']:
                compteur['croix'] += 1
            elif (i, j) in self.coords_joueur['rond']:
                compteur['rond'] += 1
        return compteur

    def nombre_pions_colonne(self, case: Case):
        compteur = {'croix': 0, 'rond': 0}
        j = case[1]
        for i in range(self.dimension):
            if (i, j) in self.coords_joueur['croix']:
                compteur['croix'] += 1
            elif (i, j) in self.coords_joueur['rond']:
                compteur['rond'] += 1
        return compteur

    def nombre_pions_diag_1(self, case: Case):
        compteur = {'croix': 0, 'rond': 0}
        i, j = case
        min_coord = min(i, j)
        fil, col = i - min_coord, j - min_coord
        for _ in range(self.dimension - fil - col):
            if (fil, col) in self.coords_joueur['croix']:
                compteur['croix'] += 1
            elif (fil, col) in self.coords_joueur['rond']:
                compteur['rond'] += 1
            fil += 1
            col += 1
        return compteur

    def nombre_pions_diag_2(self, case: Case):
        compteur = {'croix': 0, 'rond': 0}
        i, j = case
        min_desp = min(self.dimension - j - 1, i)
        fil, col = i - min_desp, j + min_desp
        for _ in range(min(self.dimension - fil, col + 1)):
            if (fil, col) in self.coords_joueur['croix']:
                compteur['croix'] += 1
            elif (fil, col) in self.coords_joueur['rond']:
                compteur['rond'] += 1
            fil += 1
            col -= 1
        return compteur

    def choisir_case_vide(self, restriction: Union[None, list[Case]] = None) -> Case:
        cases = self.cases_vides
        if restriction:
            cases = [case for case in cases if case not in restriction]
        return choice(cases)

    def choisir_case_propre(self, restriction: Union[None, list[Case]] = None) -> Case:
        cases = self.coords_joueur[self.joueur_actuel]
        if restriction:
            cases = [case for case in cases if case not in restriction]
        return choice(cases)

    # Fonctions interface

    def log(self, *args, **kwargs):
        """Afficher un message avec print()
        """
        if not self.silent:
            print(*args, **kwargs)

    def get_input(self) -> Case:
        input_valide = False
        while not input_valide:
            prompt = 'Veuillez introduire une case (format i j, q -> quitter): '
            value = input(prompt).strip()
            if value == 'q':
                self.quitter()
            case = value.split()
            if len(case) == 2 and all(k.isnumeric() for k in case):
                tentative = tuple(int(x) for x in case)
                if all(0 <= k < self.dimension for k in tentative):
                    input_valide = True
                    return tentative
            if not input_valide:
                self.log('Input invalide')
        return (0, 0)

    def demander_y_n(self, prompt: str) -> str:
        input_valide = False
        res = ''
        while not input_valide:
            value = input(prompt).strip().lower()
            if value in ('y', 'n'):
                input_valide = True
                res = value
            if not input_valide:
                self.log('Input invalide')
        return res

    def print_matrice(self):
        """Affiche la matrice M

        Args:
            M (list): Matrice à afficher
        """
        self.log('╔' + '═'*(2*self.dimension - 1) + '╗')
        for i in range(self.dimension):
            self.log('║', end='')
            symboles = []
            for j in range(self.dimension):
                symbole = ' '
                if (i, j) in self.coords_joueur['croix']:
                    symbole = 'X'
                elif (i, j) in self.coords_joueur['rond']:
                    symbole = 'O'
                symboles.append(symbole)
            self.log(*symboles, sep=' ', end='')
            self.log('║')
        self.log('╚' + '═'*(2*self.dimension - 1) + '╝')


if __name__ == "__main__":
    dim = 3
    # humain vs humain
    # morpion = Morpion(dim)

    # humain vs ia
    # morpion = Morpion(dim, 'ia')

    # ia vs ia
    morpion = Morpion(dim, 'ia', 'ia')

    morpion.commencer()