/*************** Functions **************/

/*************** get text elements from choice selections *********
 *************** and add them to the full modal card      *********/

function getText(idSelector,idUnclick1,idUnclick2, case1, case2, case3, orderId1, orderId2, idStep, idStepNum, acordionsId) {
    document.querySelector(idSelector).addEventListener('click',()=>{

        valueBill(orderId1)
        valueBill(idSelector)
        selectSteps(idSelector, idUnclick1, idUnclick2, idStep, idStepNum, acordionsId)


        console.log(document.querySelector(idSelector).firstElementChild.textContent)
        switch (document.querySelector(idSelector).firstElementChild.textContent) {

            case case1:
                document.querySelector(orderId1).textContent =
                    document.querySelector(idSelector).firstElementChild.textContent;
                document.querySelector(orderId2).textContent =
                    document.querySelector(idSelector).firstElementChild.textContent;
                changeColor(idSelector,idUnclick1,idUnclick2);
                break;

            case case2:
                document.querySelector(orderId1).textContent =
                    document.querySelector(idSelector).firstElementChild.textContent;
                document.querySelector(orderId2).textContent =
                    document.querySelector(idSelector).firstElementChild.textContent;
                changeColor(idSelector,idUnclick1,idUnclick2);
                break;

            case case3:
                document.querySelector(orderId1).textContent =
                    document.querySelector(idSelector).firstElementChild.textContent;
                document.querySelector(orderId2).textContent =
                    document.querySelector(idSelector).firstElementChild.textContent;
                changeColor(idSelector,idUnclick1,idUnclick2)
                break;
        }
        validateButton()
    })
}


/*************** change the background color ************
 *************** of the choice selections    ************/

function changeColor(idClick,idUnclick1,idUnclick2) {
    document.querySelector(idClick).style.backgroundColor = 'var(--color--dark-cyan)';
    document.querySelector(idClick).style.color = 'var(--color--light-cream)';
    document.querySelector(idUnclick1).style.backgroundColor = 'rgb(244, 241, 234)';
    document.querySelector(idUnclick1).style.color = 'var(--color--dark-grey-blue)';
    document.querySelector(idUnclick2).style.backgroundColor = 'rgb(244, 241, 234)';
    document.querySelector(idUnclick2).style.color = 'var(--color--dark-grey-blue)';
}

/*************** validate the bill button ****************/

function validateBill() {
    let value = document.querySelector('#modalText').textContent
    if (value.includes('_____')){
        console.log('cant be zero')
        alert('please !!! select all choice options')
        return false
    }else {
        return true
    }
}

function validateButton() {
    let value = document.querySelector('#modalText').textContent
    if (value.includes('_____')){
        return false
    }else {
        document.querySelector('#open-modal').classList.toggle("button_green")
        document.querySelector('#open-modal').classList.toggle("button_gray")
        return true
    }
}

/*************** fill in the amounts of *************
 *************** the chosen monthly fee *************/

function valueBill(idSelector){

    if (idSelector === '#every' || idSelector === '#every2' || idSelector ==='#month'){
        createButton()
        switch (idSelector) {
            case '#every':

                document.querySelector('#value').textContent = '$14.00/ mo';
                break;
            case '#every2':
                document.querySelector('#value').textContent = '$17.25/ mo';
                break;
            case '#month':
                document.querySelector('#value').textContent = '$22.50/ mo';
                break;
        }
    }}

function selectSteps(idSelector, id1, id2, idStep, idStepNum, acordionsId) {

        [idSelector, id1 , id2].map((key)=>{
        if (idSelector === key){
            document.querySelector(idStep).style.color = 'var(--color--dark-grey-blue)'
            document.querySelector(idStepNum).style.color = 'var(--color--dark-cyan)'
            document.querySelector(acordionsId).style.color = 'rgb(111, 111, 112)'
        }
    })
}

/*************** modal *************/


function toggleModal() {
    [modal, fade].forEach((e)=>{e.classList.toggle('hide')})
}

function createButton() {

    let div = document.querySelector('#modal-button')
    const span = document.createElement('span')
    const button = document.createElement('button')

    if (window.screen.width < 768){
    span.id = 'modalVal';
    span.classList.add('title_m');
    button.id = "close-modal"
    button.classList.add('modal__card__button')
    button.classList.add('button_green')
    button.innerHTML = 'Checkout - <span id="value">_____</span>'
    div.append(span)
    div.append(button)
    }else {
        span.id = "value";
        span.classList.add('title_m');
        button.id = "close-modal"
        button.classList.add('modal__card__button-desk')
        button.classList.add('button_green')
        button.innerHTML = 'Checkout'
        div.append(span)
        div.append(button)
    }
}

