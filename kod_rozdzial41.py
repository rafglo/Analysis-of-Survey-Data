# 1. Prawdziwe proporcje wieku w populacji
pop_proporcje_wieku = populacja['wiek_grupa'].value_counts(normalize=True)

# 2. Proporcje wieku w obciążonej próbie
proba_proporcje_wieku = finalna_proba_z_bledem['wiek_grupa'].value_counts(normalize=True)

# 3. Obliczamy wagi i dodajemy je do ramki danych
wagi = pop_proporcje_wieku / proba_proporcje_wieku

# Dodanie kolumny z wagą do naszej próby
finalna_proba_z_bledem['waga'] = finalna_proba_z_bledem['wiek_grupa'].map(wagi)
