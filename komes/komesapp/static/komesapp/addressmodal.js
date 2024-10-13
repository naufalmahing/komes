
document.addEventListener('DOMContentLoaded', async () => {
    const url = document.getElementById('change-address-url').value
    const modalContainer = document.getElementById('change-address-modal-container')

    const changeAddressButton = document.getElementById('change-address-button')
    
    console.log(url)
    changeAddressButton.addEventListener('click', async() => {
        fetch(url)
            .then(r => r.text())
            .then(html => {
                modalContainer.innerHTML = html

                // update redirect path using base url path
                const baseRedirectUrl = document.getElementById('base-url')

                // change address redirect url
                const changeAddressRedirectUrl = document.getElementById('change-address-redirect-url')
                changeAddressRedirectUrl.value = baseRedirectUrl.value
                
                // create new address button
                const createAddressButton = document.getElementById('create-address-button')
                
                createAddressButton.addEventListener('click', async() => {
                    // display create address modal
                    fetch('/komes/address/create/') // maybe need to update to use hidden input to save url
                    .then(r=>r.text())
                    .then(html => {
                        const createAddressModalContainer = document.getElementById('create-address-modal-container')
                        createAddressModalContainer.innerHTML = html

                        const redirectUrl = document.getElementById('create-address-redirect-url')
                        redirectUrl.value = baseRedirectUrl.value

                        const createAddressForm = document.getElementById('create-address-form')
                        createAddressForm.addEventListener('submit', async(event) => {
                            event.preventDefault()
                            
                            // const csrfToken = .getElementById('')
                            console.log(createAddressForm.firstElementChild.value)

                            fetch('/komes/api-test/', {
                                method: 'POST',
                                body: JSON.stringify({
                                    'csrfmiddlewaretoken': createAddressForm.firstElementChild.value,
                                    'foo': 'this is the data'
                                })
                            })
                            .then(r => r.text())
                            .then(data => {
                                console.log('data' + data)
                            })
                        })
                        
                        // close modal function
                        const closeCreateAddressButton = document.getElementById('create-address-modal-close-button')
                        
                        closeCreateAddressButton.addEventListener('click', async() => {
                            console.log('close create address modal')

                            while (createAddressModalContainer.firstChild) {
                                createAddressModalContainer.removeChild(createAddressModalContainer.firstChild);
                            }

                        })
                    })


                })


                // close modal function
                const closeChangeAddressButton = document.getElementById('change-address-modal-close-button')
                
                closeChangeAddressButton.addEventListener('click', async() => {
                    console.log('close modal')

                    while (modalContainer.firstChild) {
                        modalContainer.removeChild(modalContainer.firstChild);
                    }

                })

                // const chosenAddressId = document.getElementById('chosen-address-id')

                // // change input hidden value for the latest div user clicked
                // chosenAddressId.value = 1

                // const chooseAddressUrl = document.getElementById('choose-address-url').value

                
                
                // const addressId = 1 // manual input
                // saveChosenAddressButton = document.getElementById('save-chosen-address-button')
                
                // const saveChosenAddressUrl = document.getElementById('save-chosen-address-url').value
                // console.log(saveChosenAddressUrl)


                // saveChosenAddressButton.addEventListener('click', async() => {
                //     fetch(saveChosenAddressUrl, {
                //         method: 'POST',
                //         body: JSON.stringify({
                //             // last clicked address id
                //             address_id: addressId,
                //         })
                //     })
                //         .then(response => {
                //             console.log(response.status)
                //         })
                // })


                // change action url for choose address form
                const chooseAddressForm = document.getElementById('choose-address-form')

                console.log(chooseAddressForm.action)
                const baseUrl = chooseAddressForm.action.split('/')
                baseUrl.length = baseUrl.length-2

                console.log(baseUrl)
                chooseAddressForm.action = baseUrl.join('/') + '/1/'

                // Highlight box animation and get id for choosing latest address
                // Get all div elements with the class 'box'
                const divs = document.querySelectorAll('.address-option-container');

                // Add click event listener to each div
                divs.forEach(div => {
                    div.addEventListener('click', () => {
                        // Update form action
                        chooseAddressForm.action = baseUrl.join('/') + '/'+ div.id +'/'

                        // Remove highlight from all divs
                        divs.forEach(d => d.classList.remove('highlight'));
                        
                        // Add highlight to the clicked div
                        div.classList.add('highlight');
                    });
                });

                // get delete click event

                const deleteButtons = document.querySelectorAll('#delete-address-button')

                deleteButtons.forEach(deleteButton => {
                    console.log(deleteButton.href)

                    deleteButton.addEventListener('click', async(e) => {
                        e.preventDefault()
                        
                        fetch(deleteButton.href)
                        .then(r => r.text())
                        .then(html => {
                            const deleteConfirmationContainer = document.getElementById('delete-address-confirmation-container')
                            deleteConfirmationContainer.innerHTML = html
                            
                            // Get delete form element
                            const deleteForm = document.getElementById('delete-address-confirmation-form')
                            deleteForm.addEventListener('submit', async(e) => {
                                // Send dummy form data
                                e.preventDefault()
                                
                                // Create FormData object to store form data
                                const formData = new FormData();
    
                                // Get form csrf middleware token
                                const csrf = deleteForm.firstElementChild.value
                                console.log(csrf)
                                formData.append('csrfmiddlewaretoken', csrf)
    
                                // Send the form data to the server using fetch
                                try {
                                    const response = await fetch(deleteForm.action, {
                                    method: 'POST',
                                    body: formData,
                                    });
    
                                    if (response.ok) {
                                    // Handle success
                                    const result = await response.json();
                                    console.log('Success:', result);
                                    } else {
                                    // Handle server error
                                    console.error('Error:', response.statusText);
                                    }
                                } catch (error) {
                                    console.error('Error:', error);
                                }
                                // remove injected element
                                while (deleteConfirmationContainer.firstChild) {
                                    deleteConfirmationContainer.removeChild(deleteConfirmationContainer.firstChild);
                                }
                                // remove deleted element
                                const id = deleteButton.href.split('/').at(-2)
                                const div = document.getElementById(id)
                                div.remove()
                            })


    
                        })
                    })
                })

                
            })

        
        
    })

    
})