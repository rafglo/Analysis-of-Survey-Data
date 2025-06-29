def bootstrap_ci_complex_survey(df, zmienna, kategoria, klaster_col, waga_col, B=1000, alpha=0.05):
    """Oblicza estymatę, błąd standardowy i przedział ufności za pomocą bootstrapu dla prób złożonych."""
    
    unikalne_klastry = df[klaster_col].unique()
    n_klastrow = len(unikalne_klastry)
    
    # Mapowanie id klastra do indeksów wierszy - robimy to raz przed pętlą
    indeksy_w_klastrach = df.groupby(klaster_col).groups
    wyniki_bootstrap = []
    
    for i in range(B):
        # Krok 1: Losujemy klastry ze zwracaniem
        id_klastrow_replikacji = np.random.choice(unikalne_klastry, size=n_klastrow, replace=True)
        
        # Krok 2: Budujemy listę indeksów dla próby replikacyjnej
        indeksy_replikacji = np.concatenate([indeksy_w_klastrach[klaster_id] for klaster_id in id_klastrow_replikacji])
        
        # Krok 3: Obliczenia na podzbiorze oryginalnej ramki danych
        proba_replikacji = df.loc[indeksy_replikacji]

        if waga_col and waga_col in proba_replikacji.columns:
            licznik = proba_replikacji[proba_replikacji[zmienna] == kategoria][waga_col].sum()
            mianownik = proba_replikacji[waga_col].sum()
        else:
            licznik = (proba_replikacji[zmienna] == kategoria).sum()
            mianownik = len(proba_replikacji)
        
        wynik_replikacji = licznik / mianownik
        wyniki_bootstrap.append(wynik_replikacji)
        
    se_boot = np.std(wyniki_bootstrap)
    ci_lower = np.percentile(wyniki_bootstrap, 100 * (alpha / 2))
    ci_upper = np.percentile(wyniki_bootstrap, 100 * (1 - alpha / 2))
    
    return se_boot, ci_lower, ci_upper

partia_analizowana = 'Partia Trójkątnych'
prawdziwy_wynik_pkt = populacja['glos'].value_counts(normalize=True)[partia_analizowana]

surowy_wynik_pkt = (finalna_proba_z_bledem['glos'] == partia_analizowana).mean()
se_surowy, ci_l_surowy, ci_u_surowy = bootstrap_ci_complex_survey(
    finalna_proba_z_bledem, 'glos', partia_analizowana, 'komisja_id', waga_col=None)


wyniki_wazone_seria = finalna_proba_z_bledem.groupby('glos')['waga'].sum() / finalna_proba_z_bledem['waga'].sum()
wazony_wynik_pkt = wyniki_wazone_seria[partia_analizowana]
se_wazony, ci_l_wazony, ci_u_wazony = bootstrap_ci_complex_survey(
    finalna_proba_z_bledem, 'glos', partia_analizowana, 'komisja_id', waga_col='waga')