const clientKey = document.getElementById("ck").innerHTML;

async function initialize() {
    try {
        const paymentMethods = await dispatcher("/api/getPaymentMethods");
        const config = {
            paymentMethodsResponse: paymentMethods,
            clientKey: clientKey,
            environment: "test",
            paymentMethodsConfiguration: {
                card: {
                    hasHolderName: true,
                    holderNameRequired: true,
                    amount: {
                        value: 1500,
                        currency: "SGD"
                    }
                }
            },
            onSubmit: (state, dropin) => {
                if (state.isValid) {
                    submitHandler(state, dropin, "/api/initiatePayment");
                }
            },
            onAdditionalDetails: (state, dropin) => {
                submitHandler(state, dropin, "/api/submitAdditionalDetails");
            }         
        };

        const checkout = new AdyenCheckout(config);
        checkout.create('dropin').mount(document.getElementById("dropin"));
    } catch (error) {
        console.error(error);
    }
}

async function dispatcher(url, data){
    const response = await fetch(url, {
        method: "POST",
        body: data ? JSON.stringify(data) : "",
        headers: {
            "Content-Type": "application/json"
        }
    });

    return await response.json();
}

async function submitHandler(state, dropin, url) {
    try {
        const response = await dispatcher(url, state.data);
        responseHandler(response, dropin);
    } catch (error) {
        console.error(error);
    }
}

function responseHandler(response, dropin) {
    if (response.action) {
        if (response.resultCode === "RedirectShopper") {
            localStorage.setItem('paymentData', response.action.paymentData);
        }
        dropin.handleAction(response.action);
    } else {
        switch (response.resultCode) {
            case "Authorised":
                window.location.href = "/result/success";
                break;
            case "Pending":
            case "Received":
                window.location.href = "/result/pending";
                break;
            case "Refused":
                window.location.href = "/result/failed";
                break;
            default:
                window.location.href = "/result/error";
                break;
        }
    }
}



initialize();