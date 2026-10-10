"""Schemi vettoriali originali e grafici calcolati per Starmind."""
from pathlib import Path
from html import escape
import json, math
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'monografie/starmind/assets'; A.mkdir(parents=True,exist_ok=True)
SIGMA=5.670374419e-8; records=[]
def txt(x,y,s,size=26,color='#dce2e7',anchor='start'):
 return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" text-anchor="{anchor}">{escape(s)}</text>'
def base(title,desc,content,height=650):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc><rect width="900" height="{height}" fill="#0c1520"/><g font-family="Segoe UI,Arial,sans-serif">{txt(40,58,title,32,"#f5b941")}{content}</g></svg>'
def save(name,title,desc,content,height=650):
 (A/(name+'.svg')).write_text(base(title,desc,content,height),encoding='utf8');records.append(dict(file=name+'.svg',titolo=title,descrizione=desc,autore='Rivoluzione Spaziale',licenza='CC BY 4.0',metodo='Schema didattico originale; non disegno costruttivo SpaceX.'))
def boxes(name,title,steps,desc):
 h=140+len(steps)*132;parts=[]
 for i,(label,lines) in enumerate(steps):
  y=95+i*132;parts.append(f'<rect x="40" y="{y}" width="820" height="106" rx="10" fill="#132433" stroke="#496b83"/>');parts.append(txt(62,y+34,label,28,'#67c7ff'))
  for j,line in enumerate(lines):parts.append(txt(62,y+66+j*29,line,24))
  if i<len(steps)-1:parts.append(f'<path d="M450 {y+110} v17 m-7 -7 l7 7 7 -7" fill="none" stroke="#f5b941" stroke-width="3"/>')
 save(name,title,desc,''.join(parts),h)
FLOWS=[
('energia-calcolo','Il percorso che il Sole deve alimentare', [('Sole e pannelli',['La radiazione diventa potenza elettrica.']),('Conversione e distribuzione',['Una parte dell’energia si perde prima di arrivare ai chip.']),('Processori e memoria',['Il lavoro informatico produce soprattutto calore.']),('Circuito termico e radiatori',['Il calore viene trasportato e irradiato verso lo spazio.'])], 'Catena funzionale; la luce raccolta non equivale alla potenza utile del payload.'),
('precedenti','Tre ambienti, tre prove differenti',[('Computer nella ISS',['Stazione abitata, energia e raffreddamento condivisi.']),('Dimostratore autonomo',['Un veicolo prova componenti e carichi di lavoro in orbita.']),('Rete commerciale',['Molti nodi devono offrire un servizio ripetibile e sostenibile.'])], 'Una prova locale non dimostra automaticamente un servizio mondiale.'),
('programma','Da una proposta a una capacità operativa',[('Domanda e progetto',['Definire il sistema e aprire l’istruttoria.']),('Qualificazione e volo',['Provare l’hardware nelle condizioni della missione.']),('Produzione e servizio',['Connettere nodi, utenti, fabbrica e trasporti.']),('Ricambio e fine vita',['Continuare il servizio e rimuovere i veicoli dismessi.'])], 'Soglie diverse, non calendario garantito.'),
('chip-moduli','Un processore non lavora da solo',[('CPU',['Prepara dati e coordina le operazioni.']),('GPU e memoria veloce',['Eseguono il calcolo parallelo e conservano i dati vicini.']),('Interconnessioni',['Spostano informazioni fra unità e nodi.']),('Alimentazione e controllo',['Mantengono il sistema entro i limiti elettrici e termici.'])], 'Schema generale di una piattaforma di calcolo; non distinta AI1.'),
('carichi','Tre lavori che chiedono reti diverse',[('Inferenza locale',['Modello già caricato; richieste relativamente piccole.']),('Addestramento distribuito',['Sincronizzazione frequente fra gruppi di processori.']),('Dati prodotti in orbita',['Elaborazione vicino al sensore, poi risultati verso terra.'])], 'La convenienza dipende da dati trasferiti, comunicazioni e uso dei processori.'),
('termico','Dove passa il calore',[('Chip → interfaccia termica',['Il calore deve attraversare materiali e contatti.']),('Interfaccia → circuito',['Fluido o altri dispositivi trasportano il calore.']),('Circuito → radiatore',['La superficie trasferisce energia sotto forma di infrarosso.']),('Radiatore → ambiente',['Sole e Terra possono aggiungere calore assorbito.'])], 'Conduzione e trasporto interno, irraggiamento verso l’esterno.'),
('rete-laser','Dalla richiesta al risultato',[('Utente / rete terrestre',['La richiesta raggiunge un ingresso autorizzato.']),('Starlink / collegamenti ottici',['La rete instrada i dati verso un nodo disponibile.']),('Starmind / calcolo locale',['Il nodo esegue il lavoro con modello e dati caricati.']),('Ritorno attraverso la rete',['Il risultato raggiunge il cliente; restano code e ritardi.'])], 'Schema funzionale, non topologia reale o garanzia di latenza.'),
('radiazioni','Proteggere il risultato, oltre al satellite',[('Particella o dose accumulata',['Può alterare bit, circuiti o parametri dei componenti.']),('Rilevazione e contenimento',['Controlli, memoria corretta e isolamento dei guasti.']),('Ripresa del lavoro',['Riavvio, replica o ripartenza da uno stato salvato.']),('Verifica del risultato',['Un sistema acceso può ancora produrre dati errati.'])], 'Mitigazioni generali; efficacia e tassi di guasto vanno misurati.'),
('dispiegamento','Da carico compatto a grande satellite',[('Trasporto',['Strutture ripiegate e vincoli di carico.']),('Separazione',['Allontanamento controllato dal veicolo di lancio.']),('Apertura',['Pannelli e superfici assumono la configurazione di lavoro.']),('Controlli e trasferimento',['Verifica del satellite prima dell’orbita operativa.'])], 'Sequenza didattica; non procedura di dispiegamento SpaceX.'),
('prove','Una catena di prove rappresentative',[('Componenti',['Dose, eventi singoli, materiali e dispositivi.']),('Sottosistemi',['Circuito termico, apertura, alimentazione e laser.']),('Satellite integrato',['Vibrazioni, termovuoto e funzionamento combinato.']),('Missione sperimentale',['Dati in orbita, affidabilità e carichi reali.'])], 'Una modifica successiva può richiedere nuove prove.'),
('fabbrica','La fabbrica deve imparare a ripetere',[('Fornitura',['Chip, celle, materiali e componenti disponibili.']),('Assemblaggio',['Processi misurati, tracciabilità e integrazione.']),('Verifica',['Collaudi compatibili con il ritmo della linea.']),('Feedback dal volo',['Le anomalie cambiano progetto e produzione.'])], 'Modello industriale generale, non pianta Gigasat.'),
('operazioni','Il ciclo di un nodo di calcolo',[('Entrata in servizio',['Controlli, collegamenti, modelli e dati.']),('Lavoro quotidiano',['Assegnazione dei compiti e gestione della temperatura.']),('Degrado o guasto',['Riduzione della capacità e migrazione dei carichi.']),('Uscita e ricambio',['Fine vita programmato e sostituzione del nodo.'])], 'La capacità venduta deve includere riserve e indisponibilità.'),
('costi','Che cosa entra nel costo del servizio',[('Investimento',['Payload, satellite, lancio e infrastrutture.']),('Disponibilità',['Durata, guasti, riserve e aggiornamento hardware.']),('Uso effettivo',['Quanto tempo i processori fanno lavoro pagato.']),('Prestazione utile',['Risultati verificati, tempi e costo per il cliente.'])], 'Il costo per watt installato non è il costo per risultato utile.'),
('concorrenti','Confrontare lo stesso livello di maturità',[('Studio',['Verifica ipotesi, architettura e condizioni economiche.']),('Dimostratore',['Produce misure su hardware e ambiente.']),('Servizio iniziale',['Esegue compiti per clienti con limiti dichiarati.']),('Scala industriale',['Ripete il servizio con produzione e ricambio sostenibili.'])], 'Non è una classifica fra aziende; il livello va attribuito a una capacità specifica.'),
('astronomia','La luce che raggiunge un telescopio',[('Illuminazione del satellite',['Dipende dalla geometria Sole–Terra–veicolo.']),('Riflessione',['Materiali, pannelli e assetto modificano la luce riflessa.']),('Osservazione',['Esposizione, campo e orario definiscono l’impatto.']),('Mitigazione e misura',['Modifiche al satellite e verifica con gli astronomi.'])], 'Nessuna stima di magnitudine Starmind viene ricavata dalla sola apertura.'),
('atmosfera','Seguire il materiale fino all’atmosfera',[('Fabbricazione e lancio',['Energia, materiali, propellenti e logistica.']),('Lavoro in orbita',['Energia solare e durata della capacità di calcolo.']),('Fine vita',['Rientro, sopravvivenza di frammenti e prodotti di ablazione.']),('Valutazione complessiva',['Misure e modelli, con confronto a parità di servizio.'])], 'Il bilancio ambientale non termina al distacco dalla rampa.'),
('soglie','Che cosa dovrà misurare la prossima edizione',[('Hardware in orbita',['Apertura, energia, temperatura e qualità del calcolo.']),('Servizio con clienti',['Latenza, disponibilità e costo per lavoro utile.']),('Ricambio verificabile',['Guasti, dismissione e convivenza con altre missioni.']),('Scala sostenibile',['Produzione, lanci e impatti cumulativi documentati.'])], 'Criteri editoriali per valutare il progresso.'),
]
for a,b,c,d in FLOWS:boxes(a,b,c,d)
# Anatomia concettuale, volutamente distinta dalla geometria ufficiale.
c=''
for x in [70,550]:
 c+=f'<rect x="{x}" y="135" width="280" height="150" fill="#173e63" stroke="#67c7ff" stroke-width="3"/>'
 for dx in range(0,281,40):c+=f'<path d="M{x+dx} 135 v150" stroke="#467aa2"/>'
 for y in [185,235]:c+=f'<path d="M{x} {y} h280" stroke="#467aa2"/>'
c+='<rect x="374" y="155" width="152" height="260" fill="#243846" stroke="#f5b941" stroke-width="3"/><path d="M350 220 h24 M526 220 h24" stroke="#ccc" stroke-width="8"/><rect x="100" y="355" width="250" height="82" fill="#51626c" stroke="#fff"/><rect x="550" y="355" width="250" height="82" fill="#51626c" stroke="#fff"/>'
c+=txt(210,322,'Pannelli solari',26,'#67c7ff','middle')+txt(690,322,'Pannelli solari',26,'#67c7ff','middle')+txt(450,212,'Bus e',25,'#fff','middle')+txt(450,246,'calcolo',25,'#fff','middle')+txt(225,398,'Radiatore',26,'#fff','middle')+txt(675,398,'Radiatore',26,'#fff','middle')
c+=txt(40,500,'AI1 dichiarato: altezza 30 m · apertura 75 m',27)+txt(40,550,'Payload: 250 kW di picco · 175 kW medi',27)+txt(40,602,'Schema funzionale originale, senza proporzioni costruttive.',23,'#aab4be')
save('ai1-anatomia','AI1: funzioni e dati dichiarati','Schema concettuale originale. Posizioni e proporzioni non sono il progetto SpaceX.',c)
# Orbita: indicazione del terminatore e della direzione solare.
c='<circle cx="440" cy="312" r="145" fill="#225478"/><path d="M440 167 a145 145 0 0 1 0 290z" fill="#091521"/><ellipse cx="440" cy="312" rx="190" ry="255" fill="none" stroke="#67c7ff" stroke-width="5"/><circle cx="440" cy="57" r="10" fill="#f5b941"/>'
for y in [215,315,415]:c+=f'<path d="M65 {y} h170 m-15 -10 l15 10 -15 10" stroke="#f5b941" fill="none" stroke-width="4"/>'
c+=txt(50,150,'Luce solare',27,'#f5b941')+txt(660,290,'Lato',27)+txt(660,325,'notturno',27)+txt(40,615,'Orbita al terminatore: schema, non traiettoria AI1.',25,'#aab4be')
save('orbita-sole','Cercare il Sole vicino al terminatore','Proiezione illustrativa di un’orbita alba-tramonto; stagioni e ombre reali richiedono calcolo orbitale.',c)
def chart(name,title,xs,ys,xlabel,ylabel,foot,labels=None):
 x0,y0,w,h=115,130,725,365;lo=min(xs);hi=max(xs); ymax=max(ys)*1.12
 points=' '.join(f'{x0+(x-lo)/(hi-lo)*w:.2f},{y0+h-y/ymax*h:.2f}' for x,y in zip(xs,ys));c=''
 for j in range(5):
  val=ymax*j/4;y=y0+h-j*h/4;c+=f'<path d="M{x0} {y} h{w}" stroke="#293b49"/>'+txt(x0-18,y+8,str(round(val)),23,'#aab4be','end')
 c+=f'<path d="M{x0} {y0} v{h} h{w}" fill="none" stroke="#aab4be" stroke-width="2"/><polyline points="{points}" fill="none" stroke="#67c7ff" stroke-width="5"/>'
 for i in range(5):
  x=lo+(hi-lo)*i/4;c+=txt(x0+w*i/4,y0+h+38,str(round(x)),23,'#dce2e7','middle')
 c+=txt(40,103,ylabel,25,'#aab4be')+txt(470,566,xlabel,26,'#fff','middle')
 for j,line in enumerate(foot):c+=txt(40,608+j*31,line,22,'#aab4be')
 save(name,title,'Grafico didattico calcolato. '+ ' '.join(foot),c,690 if len(foot)>1 else 650)
temps=list(range(280,421,5));chart('radiatore-area','Più freddo significa più superficie',temps,[175000/(.9*SIGMA*t**4) for t in temps],'Temperatura del radiatore (K)','Superficie radiante efficace (m²)',['175 kW · emissività 0,90 · fondo ideale a 0 K.','Esclusi Sole, Terra, margini e differenze fra chip e radiatore.'])
eff=list(range(15,36));chart('solare-area','Dalla luce alla superficie fotovoltaica',eff,[200000/(1361*e/100*.85) for e in eff],'Efficienza delle celle (%)','Superficie solare (m²)',['Esempio: 200 kW elettrici, 1.361 W/m², fattore residuo 0,85.','Pannelli normali al Sole. Non dimensionamento AI1.'])
dist=list(range(0,10001,200));chart('ritardo-luce','Il limite posto dalla distanza',dist,[2*d/299792.458*1000 for d in dist],'Percorso in una direzione (km)','Andata e ritorno nel vuoto (ms)',['Solo propagazione; niente code, elaborazione o accessi radio.'])
use=list(range(20,101,5));chart('utilizzo-costo','Il costo cresce quando il nodo resta vuoto',use,[100/u for u in use],'Utilizzo del payload (%)','Costo relativo per lavoro utile',['Investimento e vita costanti; valore 1 a utilizzo 100%.','Modello didattico senza prezzi o prestazioni SpaceX.'])
N=[1000,10000,100000,1000000];c=txt(40,110,'Esempio: indisponibilità definitiva dell’1%',26,'#aab4be')
for i,n in enumerate(N):
 y=155+i*110;v=n*.01;length=80+math.log10(n/1000)*95;c+=txt(40,y+25,f'{n:,}'.replace(',','.')+' nodi',25)+f'<rect x="300" y="{y}" width="{length}" height="43" fill="#67c7ff"/>'+txt(300+length+12,y+30,f'{v:,.0f}'.replace(',','.')+' guasti',24)
c+=txt(40,622,'Barre illustrative compresse; conteggi = N × 0,01.',23,'#aab4be')
save('guasti-scala','Una percentuale piccola su una rete grande','Esempio aritmetico, non previsione di affidabilità Starmind. Lunghezze compresse logaritmicamente.',c)
(ROOT/'monografie/starmind/schemi.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('Schemi SVG',len(records))
