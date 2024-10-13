
document.addEventListener('DOMContentLoaded', async () => {

    console.log('this is form')

    // change action url for address choosing form
    const chooseAddressForm = document.getElementById('choose-address-form')

    const baseUrl = chooseAddressForm.action.split('/')
    baseUrl.length = baseUrl.length - 2

    console.log(baseUrl)
    // Highlight box animation and get id for choosing latest address
    // Get all div elements with the class 'box'
    const divs = document.querySelectorAll('.address-option-container');

    // Add click event listener to each div
    divs.forEach(div => {
        div.addEventListener('click', () => {
            console.log('clicked')
            console.log(div.id)
            
            // Update form action
            chooseAddressForm.action = baseUrl.join('/') + '/'+ div.id +'/'

            // Remove highlight from all divs
            divs.forEach(d => d.classList.remove('highlight'));
            
            // Add highlight to the clicked div
            div.classList.add('highlight');
        });
    });
})