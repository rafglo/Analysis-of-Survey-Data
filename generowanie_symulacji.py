import pandas as pd
import numpy as np

# --- PARAMETRY SYMULACJI ---
N_POPULACJI = 1_000_000
N_KOMISJI = 500
N_LOSOWANYCH_KOMISJI = 50
N_WYBORCOW_W_KOMISJI = 50

# Ustawienie ziarna losowości dla powtarzalności wyników
np.random.seed(42)

# --- KROK 1: GENEROWANIE POPULACJI ---
def generuj_populacje(n_populacji, n_komisji):
    """
    Tworzy populację wyborców o zdefiniowanej strukturze demograficznej i politycznej.
    Głosowanie jest skorelowane z wiekiem.
    """
    # 1. Komisje o różnej wielkości
    rozmiary_komisji = np.random.lognormal(mean=7, sigma=0.5, size=n_komisji).astype(int)
    rozmiary_komisji = (rozmiary_komisji / rozmiary_komisji.sum() * n_populacji).astype(int)
    rozmiary_komisji[-1] += n_populacji - rozmiary_komisji.sum() # Korekta do pełnej sumy

    komisja_ids = np.repeat(range(n_komisji), rozmiary_komisji)
    
    df = pd.DataFrame({
        'komisja_id': komisja_ids
    })

    # 2. Przypisanie grup wiekowych
    df['wiek_grupa'] = np.random.choice(
        ['18-29', '30-49', '50+'],
        size=n_populacji,
        p=[0.25, 0.40, 0.35] # Proporcje grup wiekowych w populacji
    )

    # 3. Definiujemy preferencje partyjne zależne od wieku
    partie = ['Partia Kwadratowych', 'Partia Okrągłych', 'Partia Trójkątnych']
    
    # Głosowanie w zależności od wieku
    def przypisz_glos(wiek):
        if wiek == '18-29':
            # Młodzi preferują Trójkątnych
            return np.random.choice(partie, p=[0.20, 0.30, 0.50])
        elif wiek == '30-49':
            # Średnia grupa wiekowa preferuje Okrągłych
            return np.random.choice(partie, p=[0.35, 0.45, 0.20])
        else: # 50+
            # Starsi preferują Kwadratowych
            return np.random.choice(partie, p=[0.55, 0.35, 0.10])

    df['glos'] = df['wiek_grupa'].apply(przypisz_glos)
    return df

# --- KROK 2: SYMULACJA ZŁOŻONEGO SCHEMATU LOSOWANIA ---
def losuj_probe_zlozona(populacja_df, n_losowanych_komisji, n_wyborcow_w_komisji):
    """
    Losuje próbę w dwuetapowym losowaniu grupowym.
    Etap 1: Losowanie komisji (klastrów).
    Etap 2: Losowanie wyborców wewnątrz wylosowanych komisji.
    """
    # Etap 1: Losujemy N komisji bez zwracania
    wszystkie_komisje_ids = populacja_df['komisja_id'].unique()
    wylosowane_komisje_ids = np.random.choice(
        wszystkie_komisje_ids,
        size=n_losowanych_komisji,
        replace=False
    )
    
    # Etap 2: Losujemy N wyborców z każdej wylosowanej komisji
    fragmenty_proby = []
    for komisja_id in wylosowane_komisje_ids:
        wyborcy_w_komisji = populacja_df[populacja_df['komisja_id'] == komisja_id]
        n_do_wylosowania = min(n_wyborcow_w_komisji, len(wyborcy_w_komisji))
        probka_z_komisji = wyborcy_w_komisji.sample(n=n_do_wylosowania)
        fragmenty_proby.append(probka_z_komisji)
        
    proba_df = pd.concat(fragmenty_proby)
    return proba_df

# --- KROK 3: WPROWADZENIE BŁĘDU BRAKU ODPOWIEDZI ---
def wprowadz_blad_braku_odpowiedzi(proba_df):
    """
    Symuluje błąd braku odpowiedzi. Respondenci z grupy 18-29
    znacznie rzadziej zgadzają się na udział w ankiecie.
    """
    def czy_odpowiedzial(wiek):
        if wiek == '18-29':
            # Tylko 40% szans na odpowiedź wśród młodych
            return np.random.choice([True, False], p=[0.4, 0.6])
        else:
            # 90% szans na odpowiedź dla pozostałych grup wiekowych
            return np.random.choice([True, False], p=[0.9, 0.1])
            
    proba_df['odpowiedz'] = proba_df['wiek_grupa'].apply(czy_odpowiedzial)
    
    finalna_proba_df = proba_df[proba_df['odpowiedz'] == True].copy()
    finalna_proba_df.drop(columns=['odpowiedz'], inplace=True)
    return finalna_proba_df

# --- GŁÓWNA CZĘŚĆ SKRYPTU ---
if __name__ == '__main__':
    populacja = generuj_populacje(N_POPULACJI, N_KOMISJI)
    idealna_proba = losuj_probe_zlozona(populacja, N_LOSOWANYCH_KOMISJI, N_WYBORCOW_W_KOMISJI)
    finalna_proba_z_bledem = wprowadz_blad_braku_odpowiedzi(idealna_proba)

    prawdziwe_wyniki = populacja['glos'].value_counts(normalize=True).sort_index()
    wyniki_idealne = idealna_proba['glos'].value_counts(normalize=True).sort_index()
    wyniki_finalne = finalna_proba_z_bledem['glos'].value_counts(normalize=True).sort_index()
