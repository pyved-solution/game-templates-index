<?php
// // Sur la deuxième page (site 2)
// if(isset($_COOKIE["username"])) {
//     $cookieValue = $_COOKIE["username"];
//     echo "PHP : Le cookie a été reçu sur le site 2 : " . $cookieValue;
// } else {
//     echo "PHP : Le cookie n'est pas présent sur le site 2.";
// }

$apiUrl = "https://t-api-beta.kata.games"; // Fill in your API URL
$userId = "1"; // Fill in the user ID
$gameId = "2"; // Fill in the game ID
$gamePrice = "10"; // Fill in the game price

// Check if the necessary parameters are set
if (!empty($apiUrl) && !empty($userId) && !empty($gamePrice)) {
    $canPayGameFeeUrl = $apiUrl . "/games/canPayGameFee?userId=$userId&gamePrice=$gamePrice";
    $response = file_get_contents($canPayGameFeeUrl);
    print_r($response);
    $response = json_decode($response, true); // Decode JSON response

    print_r($response);
    if ($response && $response['success']) {
        echo "PHP: User can pay game fee: " . ($response['canPay'] ? 'Yes' : 'No');
    } else {
        echo "PHP: Error checking if user can pay game fee.";
    }
} else {
    echo "PHP: Missing parameters to check if user can pay game fee.";
}
?>
<script src="https://beta.kata.games/connectorV.js"></script>

<!-- HTML Buttons -->
<button id="payGameFeeBtn">Pay Game Fee</button>
<button id="getPaidBtn">Get Paid</button>

<script>
    const userId = "1"; // Fill in the user ID
    const gameId = "11"; // Fill in the game ID
    const gamePrice = "10"; // Fill in the game price
    const amountWon = "5"
    let token = null

    document.getElementById('payGameFeeBtn').addEventListener('click', function() {
        const payload = {
            userId: userId,
            gameId: gameId,
            gamePrice: gamePrice
        };

        fetch(`${apiUrl}/games/payGameFee`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            token = data.tokenCode
            console.log('Pay Game Fee Response:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    document.getElementById('getPaidBtn').addEventListener('click', function() {
        const payload = {
            userId: userId,
            gameId: gameId,
            amount: amountWon, // Assuming you want to use the gamePrice as the amount
            token: token
        };

        fetch(`${apiUrl}/games/getPaid`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Get Paid Response:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
</script>

<script>
    // Fonction pour récupérer la valeur d'un cookie
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for(let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if(cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}

// Récupération du cookie défini sur le site 1
const cookieValue = getCookie('username');
console.log(document)
if(cookieValue !== null) {
    console.log("Le cookie a été reçu sur le site 2 : " + cookieValue);
} else {
    console.log("Le cookie n'est pas présent sur le site 2.");
}

</script>
