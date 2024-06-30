const navButton = document.querySelector('#header__nav__button');
const menuImg = document.querySelector('#header__nav__img')
const navegationBar = document.querySelector('#navBar')

/******** main menu *********/

navButton.addEventListener('click', ()=>{
    console.log(navegationBar.style)
    if (navegationBar.style.display ===''){
        navegationBar.style.display = 'flex'
        menuImg.setAttribute('src','assets/images/shared/mobile/icon-close.svg')
    }else {
        navegationBar.style.display = ''
        menuImg.setAttribute('src','assets/images/shared/mobile/icon-hamburger.svg')
    }
})

