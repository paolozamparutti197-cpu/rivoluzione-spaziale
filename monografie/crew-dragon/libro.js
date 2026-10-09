document.querySelectorAll('.bookaside details').forEach(el => {if (window.matchMedia('(max-width:950px)').matches) el.open = false;});
const search = document.querySelector('#cerca-voli');
const type = document.querySelector('#tipo-volo');
function filterFlights(){
  const query = (search?.value || '').toLocaleLowerCase('it').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  let visible = 0;
  document.querySelectorAll('#registro tbody tr').forEach(row => {
    const text = row.textContent.toLocaleLowerCase('it').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
    row.hidden = !text.includes(query) || (type.value !== 'tutti' && row.dataset.tipo !== type.value);
    if (!row.hidden) visible++;
  });
  const result = document.querySelector('#risultati');
  if(result) result.textContent = `${visible} missioni visualizzate. I conteggi complessivi non cambiano con il filtro.`;
}
search?.addEventListener('input',filterFlights);
type?.addEventListener('change',filterFlights);
