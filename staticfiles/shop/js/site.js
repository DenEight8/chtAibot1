// ===== DARK / LIGHT =================================================
const btnTheme=document.getElementById('toggle-theme');
if(localStorage.getItem('theme')==='dark'){
  document.documentElement.setAttribute('data-theme','dark');
  btnTheme.checked=true;
}
btnTheme.addEventListener('change',e=>{
  if(e.target.checked){
    document.documentElement.setAttribute('data-theme','dark');
    localStorage.setItem('theme','dark');
  }else{
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('theme','light');
  }
});

// ===== QUICK SEARCH (client-side filter без перезавантаження) =======
const q=document.getElementById('product-search');
if(q){
  q.addEventListener('input',e=>{
    const term=e.target.value.toLowerCase();
    document.querySelectorAll('.product-card').forEach(c=>{
      c.style.display = c.dataset.name.includes(term) ? '' : 'none';
    });
  });
}
