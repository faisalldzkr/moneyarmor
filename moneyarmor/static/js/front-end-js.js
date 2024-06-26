/*=============== SHOW SIDEBAR ===============*/
const showSidebar = (toggleId, sidebarId, mainId) =>{
    const toggle = document.getElementById(toggleId),
          sidebar = document.getElementById(sidebarId),
          main = document.getElementById(mainId)

    if(toggle && sidebar && main){
        toggle.addEventListener('click', () =>{
            // Show sidebar
            sidebar.classList.toggle('show-sidebar')
            // Add padding main
            main.classList.toggle('main-pd')
        })
    }
}
showSidebar('header-toggle','sidebar','main')

/*=============== LINK ACTIVE ===============*/
const sidebarLink = document.querySelectorAll('.sidebar-link')

function linkColor(){
    sidebarLink.forEach(t => t.classList.remove('active-link'))
    this.classList.add('active-link')
}

sidebarLink.forEach(t => t.addEventListener('click', linkColor))

/*=============== 70/10/10/10 ===============*/
function addSavings1() {
    const amount = parseInt(document.getElementById('amount1').value);

    if (!isNaN(amount) && amount > 0) {
        const totalPokok = amount * 70 / 100;
        const totalTabungan = amount * 10 / 100;
        const totalSedekah = amount * 10 / 100;
        const totalHiburan = amount * 10 / 100;

        document.getElementById('totalPokok1').textContent = `Rp ${totalPokok.toFixed(2)}`;
        document.getElementById('totalTabungan1').textContent = `Rp ${totalTabungan.toFixed(2)}`;
        document.getElementById('totalSedekah1').textContent = `Rp ${totalSedekah.toFixed(2)}`;
        document.getElementById('totalHiburan1').textContent = `Rp ${totalHiburan.toFixed(2)}`;
        document.getElementById('amount1').value = '';
    } else {
        alert('Masukkan jumlah yang valid!');
    }
}