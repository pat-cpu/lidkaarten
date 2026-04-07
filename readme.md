<<<<<<< HEAD
📘 README — Lidkaarten The Whiskies
Overzicht van alle belangrijke Python-commando’s (2025)

Dit document bevat alle commando’s die je gebruikt om lidkaarten te genereren:

één enkel kaartje recto/verso

alle kaartjes voor alle leden

filters, samples, front/back-only

projectstructuur

tips voor recto-verso printen

📂 1. Bestandsstructuur

Je map lidkaartenPython bevat:

lidkaartenPython/
│
├─ leden.xlsx                 # bronbestand met nummers + namen
├─ logo.png                   # logo voor de kaartjes
│
├─ print_single_card.py       # één kaartje recto/verso
├─ Lidkaart_2025_2026.py      # hoofdscript voor alle kaarten
│
├─ kaartjes_svg/              # tijdelijke SVG-bestanden
├─ kaartjes_pdf/              # PDF-uitvoer
│
└─ README.md                  # deze handleiding

🎯 2. Eén kaartje printen (recto/verso)

Gebruik:

python print_single_card.py --pos 1 --name "Patrick"

Betekenis:
Optie	Uitleg
--pos 1	Op welke positie op A4 (1 t/m 10) de voorkant moet komen
--name "Patrick"	Naam zoeken in leden.xlsx
(automatisch)	achterkant wordt op positie 6 gezet zodat recto-verso klopt
Output:

single_pdf/front_SINGLE.pdf

single_pdf/back_SINGLE.pdf

Printinstelling:
Duplex – flip on long edge (lange zijde omdraaien)

📚 3. Alle lidkaarten genereren (recto/verso voor iedereen)

Volledig pakket:

python Lidkaart_2025_2026.py


Dit maakt:

alle individuele kaarten (PDF)

A4 FRONT bundel

A4 BACK bundel

alles in kaartjes_pdf/

🔍 4. Nuttige opties
👉 Alle leden tonen
python Lidkaart_2025_2026.py --list

👉 Enkel bepaalde namen
python Lidkaart_2025_2026.py --filter "Geys"

👉 Testen met 3 kaartjes
python Lidkaart_2025_2026.py --sample 3

👉 Volgorde uit Excel behouden
python Lidkaart_2025_2026.py --keep-order

👉 Enkel voorkant of achterkant produceren
python Lidkaart_2025_2026.py --only-front
python Lidkaart_2025_2026.py --only-back

👉 Geen aparte PDF per kaartje (sneller)
python Lidkaart_2025_2026.py --no-single-pdfs

🖨️ 5. Perfect recto-verso printen
Voor één kaartje (single)

FRONT komt op positie 1

BACK komt automatisch op correcte positie 6

Gebruik in je printer‐driver:
Duplex — Flip on Long Edge

Voor volledige A4-bundels

Beide bestanden worden perfect uitgelijnd:

Lidkaartjes_A4_FRONT_…pdf

Lidkaartjes_A4_BACK_…pdf

Print zo:

Print FRONT eerst

Print BACK erop, met
duplex flip on long edge

🧹 6. Opschonen (optioneel)
python cleanup.py


Verwijdert:

oude SVG’s

oude PDF’s

tijdelijke bestanden

Laat staan:

leden.xlsx

scripts

logo.png

📞 Hulp nodig?

Patrick, wil je:

een nog mooier README met iconen?

een automatische installer?

een GUI (knoppen: "Print Patrick", "Print alles")?

Dan bouwen we dat er gewoon bij.
=======
📘 README — Lidkaarten The Whiskies
Overzicht van alle belangrijke Python-commando’s (2025)

Dit document bevat alle commando’s die je gebruikt om lidkaarten te genereren:

één enkel kaartje recto/verso

alle kaartjes voor alle leden

filters, samples, front/back-only

projectstructuur

tips voor recto-verso printen

📂 1. Bestandsstructuur

Je map lidkaartenPython bevat:

lidkaartenPython/
│
├─ leden.xlsx                 # bronbestand met nummers + namen
├─ logo.png                   # logo voor de kaartjes
│
├─ print_single_card.py       # één kaartje recto/verso
├─ Lidkaart_2025_2026.py      # hoofdscript voor alle kaarten
│
├─ kaartjes_svg/              # tijdelijke SVG-bestanden
├─ kaartjes_pdf/              # PDF-uitvoer
│
└─ README.md                  # deze handleiding

🎯 2. Eén kaartje printen (recto/verso)

Gebruik:

python print_single_card.py --pos 1 --name "Patrick"

Betekenis:
Optie	Uitleg
--pos 1	Op welke positie op A4 (1 t/m 10) de voorkant moet komen
--name "Patrick"	Naam zoeken in leden.xlsx
(automatisch)	achterkant wordt op positie 6 gezet zodat recto-verso klopt
Output:

single_pdf/front_SINGLE.pdf

single_pdf/back_SINGLE.pdf

Printinstelling:
Duplex – flip on long edge (lange zijde omdraaien)

📚 3. Alle lidkaarten genereren (recto/verso voor iedereen)

Volledig pakket:

python Lidkaart_2025_2026.py


Dit maakt:

alle individuele kaarten (PDF)

A4 FRONT bundel

A4 BACK bundel

alles in kaartjes_pdf/

🔍 4. Nuttige opties
👉 Alle leden tonen
python Lidkaart_2025_2026.py --list

👉 Enkel bepaalde namen
python Lidkaart_2025_2026.py --filter "Geys"

👉 Testen met 3 kaartjes
python Lidkaart_2025_2026.py --sample 3

👉 Volgorde uit Excel behouden
python Lidkaart_2025_2026.py --keep-order

👉 Enkel voorkant of achterkant produceren
python Lidkaart_2025_2026.py --only-front
python Lidkaart_2025_2026.py --only-back

👉 Geen aparte PDF per kaartje (sneller)
python Lidkaart_2025_2026.py --no-single-pdfs

🖨️ 5. Perfect recto-verso printen
Voor één kaartje (single)

FRONT komt op positie 1

BACK komt automatisch op correcte positie 6

Gebruik in je printer‐driver:
Duplex — Flip on Long Edge

Voor volledige A4-bundels

Beide bestanden worden perfect uitgelijnd:

Lidkaartjes_A4_FRONT_…pdf

Lidkaartjes_A4_BACK_…pdf

Print zo:

Print FRONT eerst

Print BACK erop, met
duplex flip on long edge

🧹 6. Opschonen (optioneel)
python cleanup.py


Verwijdert:

oude SVG’s

oude PDF’s

tijdelijke bestanden

Laat staan:

leden.xlsx

scripts

logo.png

📞 Hulp nodig?

Patrick, wil je:

een nog mooier README met iconen?

een automatische installer?

een GUI (knoppen: "Print Patrick", "Print alles")?

Dan bouwen we dat er gewoon bij.
>>>>>>> 14b142486c61fce67c54e7dc87a5c29fdb29e6d5
Je project is al topklasse — we maken het graag nóg professioneler. 💪😄