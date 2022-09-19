"""
Résoudre le problème des cavaliers

Algorithme à Essais Successifs (AES), implementation naïve, avec backtracking simple
"""
from time import time
import numpy as np

TAB_DELTA_X_Y = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]]


def creer_matrice(dim):
    """Créer une matrice carrée de taille n"""
    return -1 * np.ones((dim, dim))


def AES_parcours_cavalier_un_succes_suffit(echiquier, taille, derniere_case_traitee,
                                           prochain_num_etape, compteurs):
    compteurs[0] += 1
    if prochain_num_etape > taille * taille:
        return True
    for i in range(8):
        next_x = derniere_case_traitee[0] + TAB_DELTA_X_Y[i][0]
        next_y = derniere_case_traitee[1] + TAB_DELTA_X_Y[i][1]
        if prometteur(echiquier, taille, next_x, next_y):
            echiquier[next_x][next_y] = prochain_num_etape
            res = AES_parcours_cavalier_un_succes_suffit(
                echiquier, taille, (next_x, next_y), prochain_num_etape + 1, compteurs)
            if res:
                return True
            echiquier[next_x][next_y] = -1
            compteurs[1] += 1
    return False


def prometteur(echiquier, taille, next_x, next_y):
    return 0 <= next_x < taille and 0 <= next_y < taille and echiquier[next_x][next_y] == -1


if __name__ == '__main__':
    N = int(input("Taille de la matrice ? (>4; défaut 5) ") or 5)
    depart = tuple(
        map(int, (input(f"Départ du cavalier ? (0<=x,y<={N-1}; défaut 0 0) ") or "0 0").split()))

    G = creer_matrice(N)
    G[depart[0], depart[1]] = 1

    prochaine_numero = 2

    stats = [0, 0]

    t_1 = time()
    final_res = AES_parcours_cavalier_un_succes_suffit(G, N, depart, prochaine_numero, stats)
    t_2 = time()

    if final_res:
        print(G)
    else:
        print('échec')

    print('Nombre de tentatives :', stats[0])
    print('Nombre de backtracks :', stats[1])
    print('Temps de calcul :', t_2 - t_1)
