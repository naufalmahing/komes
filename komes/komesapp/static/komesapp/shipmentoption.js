
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


    
    // options.forEach(option => {
    //     option.addEventListener('click', (e) => {
    //         e.stopPropagation()
    //         console.log(option.id)
            
    //         options.forEach(option => option.classList.remove('highlight'))
    //         option.classList.add('highlight')

    //         courierInput.value = option.id
            
    //         parent.firstElementChild.innerHTML = option.innerHTML

    //         console.log(child[0].style.display)
    //         console.log(overlay[0].style.visibility)
    //         // idk it's not working
    //         child[0].style.display = 'none'
    //         overlay[0].style.visibility = 'hidden'

    //         console.log('after')
            
    //         console.log(child[0].style.display)
    //         console.log(overlay[0].style.visibility)

    //         parentNotClicked = true
        // })
    // });

}

// Call the function to create the new child element
createChildAtSamePosition();


/*
Every time there's a change in courier update hidden value in pay form
*/


const options = document.querySelectorAll('.courier-option')
console.log(options)

const courierInput = document.getElementById('courier-input')

function updateCourier() {
    const options = document.querySelectorAll('.courier-option')
    console.log(options)

    const courierInput = document.getElementById('courier-input')
    
    options.forEach(option => {
        option.addEventListener('click', (evt) => {
            evt.stopPropagation()

            console.log(option.id)
            
            options.forEach(option => option.classList.remove('highlight'))
            option.classList.add('highlight')

            courierInput.value = option.id
            
            parent.firstElementChild.innerHTML = option.innerHTML

            console.log(child[0].style.display)
            console.log(overlay[0].style.visibility)
            // idk it's not working
            child[0].style.display = 'none'
            overlay[0].style.visibility = 'hidden'

            console.log('after')
            
            console.log(child[0].style.display)
            console.log(overlay[0].style.visibility)

            parentNotClicked = true
        })
    });

}

updateCourier()

// update 