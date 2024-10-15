
const parent = document.getElementById("parent");
const child = document.getElementsByClassName("child");
const overlay = document.getElementsByClassName('overlay')

let parentNotClicked = true
function createChildAtSamePosition() {

    console.log(overlay)

    parent.addEventListener('click', (evt) => {
        evt.stopPropagation()

        if (parentNotClicked) {
            console.log(overlay[0].style.visibility)
    
            overlay[0].style.visibility ='visible'
            child[0].style.display = 'unset'

            parentNotClicked = false
        }
    })
    

    overlay[0].addEventListener('click', (evt) => {
        evt.stopPropagation()

        console.log(overlay[0].style.visibility)

        overlay[0].style.visibility = 'hidden'
        child[0].style.display = 'none'

        parentNotClicked = true
    })

    parent.addEventListener('focusout', () => {
        console.log('focusout')
        child[0].style.display = 'none'
        overlay[0].style.visibility = 'hidden'

        parentNotClicked = true
    })


}

// Call the function to create the new child element
createChildAtSamePosition();


/*
Every time there's a change in courier update hidden value in pay form
*/


const options = document.querySelectorAll('.courier-option')
console.log(options)

// const courierInput = document.getElementById('courier-input')

const payForm = document.getElementById('pay-form')

function updateCourier() {
    const options = document.querySelectorAll('.courier-option')
    console.log(options)

    // const courierInput = document.getElementById('courier-input')
    
    options.forEach(option => {
        option.addEventListener('click', (evt) => {
            evt.stopPropagation()

            console.log(option.id)
            
            options.forEach(option => option.classList.remove('highlight'))
            option.classList.add('highlight')

            // courierInput.value = option.id
            
            parent.firstElementChild.innerHTML = option.innerHTML

            // console.log(child[0].style.display)
            // console.log(overlay[0].style.visibility)

            // idk it's not working, it's working now
            child[0].style.display = 'none'
            overlay[0].style.visibility = 'hidden'

            // console.log('after')
            
            // console.log(child[0].style.display)
            // console.log(overlay[0].style.visibility)

            parentNotClicked = true

            // update courier form
            payForm.elements['courier-fee'].value = parent.querySelector('#courier-fee').textContent.trim()
            payForm.elements['delivery-type'].value = parent.querySelector('#delivery-type').textContent.trim()
            payForm.elements['courier-name'].value = parent.querySelector('#courier-name').textContent.trim()
            payForm.elements['courier-type'].value = parent.querySelector('#courier-type').textContent.trim()

            // Add courier fee and display
            let courierFee = payForm.elements['courier-fee'].value
            courierFee = Number(courierFee)

            let productTotalFee = document.getElementById('products-total-payment').textContent.slice(3)
            productTotalFee = productTotalFee.split('.')[0].replace(',', '')
            productTotalFee = Number(productTotalFee)

            console.log(courierFee)
            
            document.getElementById('total-payment').textContent = courierFee + productTotalFee
        })
    });

}

updateCourier()

// update 