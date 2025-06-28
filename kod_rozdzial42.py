# Obliczenie ważonych proporcji
wyniki_wazone = finalna_proba_z_bledem.groupby('glos')['waga'].sum() / finalna_proba_z_bledem['waga'].sum()
wyniki_wazone = wyniki_wazone.sort_index()
