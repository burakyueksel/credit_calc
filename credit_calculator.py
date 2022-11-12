import pandas as pd
import numpy as np
 
 
def compute_yearly_annuity(kreditsumme, nominalzins_prozent, tilgungssatz_prozent):
    """ Berechnet die _jährliche_ Annuität.
        Jährliche_Rate = (nominalzins + tilgungssatz) * Kreditsumme
        Quelle: https://de.wikipedia.org/wiki/Annuit%C3%A4tendarlehen
    """ 
 
    zinssatz = nominalzins_prozent / 100
    tilgung = tilgungssatz_prozent / 100
    return round(kreditsumme * (zinssatz + tilgung), 2)
 
 
def compute_monthly_annuity(kreditsumme, nominalzins_prozent, tilgungssatz_prozent):
    """ Berechnet die _monatliche_ Annuität.
        Jährliche_Rate = (nominalzins + tilgungssatz) * Kreditsumme
        Monatliche_Rate = Jährliche_Rate / 12
    """ 
 
    zinssatz = nominalzins_prozent / 100
    tilgung = tilgungssatz_prozent / 100
    return round(kreditsumme * (zinssatz + tilgung) / 12, 2)
 
def tilgungsplan_df(kreditsumme, nominalzins_prozent, tilgungssatz_prozent, sondert, wartezeit, monate):
    """ 
        Gibt DataFrame der monatlichen Tilgungen zurück
 
        "monate" für wieviele Monate wird der Tilgungsplan erstellt
        "sondert" Betrag der jährlichen Sondertilgung
        "wartezeit" Anzahl der Jahre ohne Sondertilgung
    """
 
    df = pd.DataFrame()
    restschuld = kreditsumme # Am Anfang entspricht die Restschuld der Kreditsumme
    zinssatz = nominalzins_prozent / 100
    tilgung = tilgungssatz_prozent / 100
 
    annuitaet = compute_monthly_annuity(kreditsumme, nominalzins_prozent, tilgungssatz_prozent)
    zinsen = 0
 
    for j in range(1,monate+1):
        # Split der Annuität in ihre Komponenten Zinslast und Tilgung
        zinsen = restschuld * zinssatz / 12 
        # Wenn Restschuld kleiner Annuität, dann wird die komplette 
        # Restschuld getilgt
        tilgung = restschuld if restschuld < annuitaet else annuitaet - zinsen    
 
        anfangsschuld = restschuld
        jahr = ((j-1) // 12) + 1 # in welchem Monat befinden wir uns
 
        # Sondertilgungen im Dezember eines Jahres, wenn wir 
        # nicht in der Wartezeit sind
        if j % 12 == 0 and anfangsschuld > 0 and jahr > wartezeit:
            sondertilgung = sondert
        else:
            sondertilgung = 0
 
        # Restschuld_neu = Restschuld_alt minus Tilgung minus Sondertilgung
        restschuld = restschuld - tilgung - sondertilgung
        
        # monthly paid sum
        monthly_sum = zinsen + tilgung + sondertilgung
 
        # Dataframe befüllen
        df = df.append({'Monat': j, 'Jahr': jahr,'Anfangsschuld': anfangsschuld, 
        'Zinsen':zinsen, 'Tilgung': tilgung, 'Sondertilgung': sondertilgung,
        'Restschuld': restschuld, 'MonthSum': monthly_sum}, ignore_index=True)    
 
    # Indikatorspalte, "1" wenn der Kredit noch nicht abbezahlt ist, sonst "0"
    df['Indikator'] = np.where(df['Anfangsschuld']>0, 1, 0)
    # Umsortieren der Spalten
    df = df[['Monat', 'Jahr', 'Anfangsschuld', 'Zinsen', 'Tilgung', 'Sondertilgung', 'Restschuld', 'MonthSum', 'Indikator']]
 
    # Runden auf 2 Nachkommastellen
    for i in ['Anfangsschuld', 'Zinsen', 'Tilgung', 'Restschuld', 'MonthSum']:
        df[i] = df[i].apply(lambda x: round(x, 2))    
 
    # Monat als Index nutzen
    df.set_index('Monat', inplace=True)
    return df

# config
kredit_summe =  150000
nominalzins_prozent = 4.0
tilgungssatz_prozent = 4.0
sondertiltung_jahr_betrag = 4800
wartezeit_jahr = 0
monate = 200

print('===CASE STUDY===')
print(kredit_summe, 'kredit sum in EUR')
print(nominalzins_prozent, 'nom zinsen prozent')
print(tilgungssatz_prozent, 'tilgungssatz prozent')
print(sondertiltung_jahr_betrag, 'sondertilgung per year in EUR')
print('===ANALYSIS===')
print(compute_yearly_annuity(kredit_summe, nominalzins_prozent, tilgungssatz_prozent), 'jährliche Annuität')
print(compute_monthly_annuity(kredit_summe, nominalzins_prozent, tilgungssatz_prozent), 'monatliche Annuität')
 
tilgungsplan = tilgungsplan_df(kredit_summe, nominalzins_prozent, tilgungssatz_prozent, sondertiltung_jahr_betrag, wartezeit_jahr, monate)

#Wie lange läuft der Kredit
kredit_laufzeit_months = round(tilgungsplan['Indikator'].sum(),1)
kredit_laufzeit_years = round(kredit_laufzeit_months/12,2)
print('Gesamtlaufzeit:', kredit_laufzeit_months, 'Monate')
print('Gesamtlaufzeit:', kredit_laufzeit_years, 'Jahre')

#How much did you pay at the end?
total_zinsen_payments = tilgungsplan['Zinsen'].sum()
total_tilgung_payments = tilgungsplan['Tilgung'].sum()
total_sonder_tilgung_payments = tilgungsplan['Sondertilgung'].sum()
total_payments = tilgungsplan['MonthSum'].sum()
geschenkt_to_bank = total_payments - kredit_summe

print('Total Zinsen Payment:', total_zinsen_payments, 'EUR')
print('Total Tilgung Payment:', total_tilgung_payments, 'EUR')
print('Sondern Tilgung Payment:', total_sonder_tilgung_payments, 'EUR')
print('TOTAL Payment:', total_payments, 'EUR')
print('GESCHENKT to Bank:', geschenkt_to_bank, 'EUR')


 
tilgungsplan.to_excel('tilgungsplan_gesamt.xlsx')
