// Annotazioni vettoriali su una fotografia autentica, senza alterare il JPEG.
// Coordinate controllate sul file 1024 × 683: booster x=480/547, centrale x=512.
import fs from 'node:fs';
import path from 'node:path';
export function falconHeavyPhoto(root) {
 const photo=fs.readFileSync(path.resolve(root,'../../documenti per sito/assets_fondazione/falcon-heavy-2018/preparazione.jpg')).toString('base64');
 const labels=[
  ['Carenatura',25,145,165,165,511,140],
  ['Secondo stadio',25,260,240,280,512,239],
  ['Booster laterale sinistro',25,440,350,460,480,400],
  ['Booster laterale destro',680,440,680,460,547,400],
  ['Corpo centrale',710,575,710,595,512,500]
 ];
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 850" role="img" aria-labelledby="title desc"><title id="title">Falcon Heavy: fotografia annotata</title><desc id="desc">Fotografia SpaceX del 28 dicembre 2017. Le linee terminano sulla carenatura, sul secondo stadio, sui due booster laterali separatamente e sul corpo centrale. I motori e il carico utile sono nascosti e non vengono indicati come visibili.</desc><metadata>Fotografia: SpaceX, CC0 1.0. https://commons.wikimedia.org/wiki/File:Falcon_Heavy_Demo_Mission_(38583829295).jpg . Annotazioni editoriali: Rivoluzione Spaziale, 11 ottobre 2026. Nessuna modifica al JPEG.</metadata><rect width="1024" height="850" fill="#11232f"/><image x="0" y="65" width="1024" height="683" href="data:image/jpeg;base64,${photo}"/><style>text{font-family:Arial,sans-serif;fill:#fff} .label{font-size:24px;font-weight:bold} .note{font-size:21px} .leader{fill:none;stroke:#00616b;stroke-width:4} .halo{fill:none;stroke:white;stroke-width:8} .target{fill:#00616b;stroke:white;stroke-width:2}</style><text x="25" y="42" font-size="29">Falcon Heavy · i componenti visibili</text>${labels.map(([t,x,y,sx,sy,tx,ty])=>`<path class="halo" d="M${sx} ${sy} L${tx} ${ty+65}"/><path class="leader" d="M${sx} ${sy} L${tx} ${ty+65}"/><circle class="target" cx="${tx}" cy="${ty+65}" r="6"/><rect x="${x-10}" y="${y-7}" width="${t.length*13+20}" height="45" rx="4" fill="#11232f"/><text class="label" x="${x}" y="${y+24}">${t}</text>`).join('')}<text class="note" x="25" y="782">Primo stadio: 9 Merlin per corpo × 3 = 27 motori.</text><text class="note" x="25" y="814">Secondo stadio: 1 Merlin Vacuum, interno e non visibile.</text><text x="25" y="840" font-size="16">Foto SpaceX · 28 dicembre 2017 · CC0 1.0 · annotazioni aggiunte dal sito</text></svg>`;
}
