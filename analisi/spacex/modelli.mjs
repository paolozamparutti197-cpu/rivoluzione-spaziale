// Modelli didattici originali, condivisi da calcoli, grafici e interfaccia.
function number(value,name,min,max){
 const n=Number(value);if(!Number.isFinite(n)||n<min||n>max)throw Error(`${name}: valore fra ${min} e ${max}.`);return n;
}
export function costModel({stage=100,refurb=5,other=35,flights=10}={}){
 const C=number(stage,'Costo stadio',0,1e9),R=number(refurb,'Ricondizionamento',0,1e9),A=number(other,'Altri costi',0,1e9),n=number(flights,'Voli',1,10000);
 if(!Number.isInteger(n))throw Error('Voli: usare un numero intero.');
 const average=C/n+R*(n-1)/n+A,disposable=C+A;
 return {stage:C,refurb:R,other:A,flights:n,average,disposable,ratio:disposable?average/disposable:null};
}
export function replacementModel({satellites=5000,lifetime=5}={}){
 const N=number(satellites,'Satelliti',1,1e6),L=number(lifetime,'Vita media',.1,100);
 if(!Number.isInteger(N))throw Error('Satelliti: usare un numero intero.');
 return {satellites:N,lifetime:L,perYear:N/L,perDay:N/L/365.25};
}
