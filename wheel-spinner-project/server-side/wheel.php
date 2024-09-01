<?php
include('dbconnection.php');
include('low_level.php');

$API_HOST ='https://services.kata.games';
$HOST2 = 'https://cms.kata.games/content/plugins/facade';

// Récupère l'ID de l'utilisateur par son nom d'utilisateur
function getUserIdByJwt($jwt) {
	global $API_HOST,$HOST2;
    // JWT token to be sent in the API call

    // API endpoint URL
    $endpoint = $HOST2."/user/jwt?jwt=" . urlencode($jwt);

    // Initialize cURL session
    $curl = curl_init();

    // Set cURL options
    curl_setopt_array($curl, [
        CURLOPT_URL => $endpoint, // Set the endpoint URL
        CURLOPT_RETURNTRANSFER => true, // Return response as a string
        CURLOPT_FOLLOWLOCATION => true, // Follow redirects if any
        CURLOPT_MAXREDIRS => 10, // Limit the number of redirects
        CURLOPT_TIMEOUT => 30, // Set the maximum execution time for the cURL session
        CURLOPT_HTTPGET => true, // Use HTTP GET method
        CURLOPT_SSL_VERIFYPEER => false, // Disable SSL verification (only for testing)
    ]);

    // Execute the cURL session
    $response = curl_exec($curl);

    // Check for errors
    if (curl_errno($curl)) {
        $error_message = curl_error($curl);
        // Handle cURL error
        echo "Error: $error_message";
        return null;
    } else {
        // API call successful
        $http_status_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
        if ($http_status_code === 200) {
            // Parse and process the API response
            $data = json_decode($response, true);
            // Access the user_id from the response
            $user_id = $data['user_id'];
            // Return the user ID
            return $user_id;
        } else {
            // Handle non-200 HTTP response
			echo "when calling: $endpoint ...";
            echo "HTTP Error: $http_status_code";
            return null;
        }
    }

    // Close cURL session
    curl_close($curl);
}


// Vérifie si l'utilisateur a déjà utilisé son spin aujourd'hui
function hasUsedSpin($userId) {
    $conn = dbConnection();
    $today = date('Y-m-d');
    $stmt = $conn->prepare("SELECT last_spin_date FROM users_spin WHERE user_id = :userId");
    $stmt->execute(['userId' => $userId]);
    $lastSpinDate = $stmt->fetch(PDO::FETCH_ASSOC)['last_spin_date'] ?? null;
    
    return $lastSpinDate === $today;
}

// Créer fonction pour insert dans user_spins
// Update l'inventaire en credits (Faire un endpoint victory ou quelque chose du genre, qui ensuite ajoute les crédits)

function updateSpinAndCreditsIfWon($userId, $hasWon, $hasWonTwice, $creditsToAdd,$game_id, $tokenCode) {
	global $API_HOST;
    $conn = dbConnection();
    $today = date('Y-m-d');
    
    // Update the last_spin_date in the users_spin table
    
	// tom: disabled code below,
	//as we again wish to allow several plays, not only 1 per day
	
	//$stmt = $conn->prepare("INSERT INTO users_spin (user_id, last_spin_date) VALUES (:userId, :today) ON DUPLICATE KEY UPDATE last_spin_date = :today");
    //$stmt->execute(['userId' => $userId, 'today' => $today]);

    if ($tokenCode && $hasWon) {
		
        $url = $API_HOST."/pvp/games/getPaid?user_id={$userId}&game_id={$game_id}&token={$tokenCode}&amount={$creditsToAdd}&description=luck_game";
		$response = std_curl_call($url);

    } else {
        // Token code not available
        // Log the error or handle as needed
        // For now, let's return a message
        return ['success' => false, 'message' => 'Token code not available'];
    }
    // Determine the number of spins won based on hasWon and hasWonTwice flags
    $spinsWon = 0;
    if ($hasWon) {
        $spinsWon = $hasWonTwice ? 2 : 1;
    }

    // Save spin results to spins_history table
    $stmt = $conn->prepare("INSERT INTO spins_history (date, spins_won, credits, user_id) VALUES (:today, :spinsWon, :creditsToAdd, :userId)");
    $stmt->execute(['today' => $today, 'spinsWon' => $spinsWon, 'creditsToAdd' => $creditsToAdd, 'userId' => $userId]);
}

// Génère le spin et renvoie les résultats
function generateSpin($userId, $game_id, $tokenCode) {

    // Génère deux numéros pour l'utilisateur et le serveur
    $userNumber1 = random_int(1, 6); // Premier numéro utilisateur
    $serverNumber1 = random_int(1, 6); // Premier numéro serveur
    $userNumber2 = random_int(1, 6); // Second numéro utilisateur
    $serverNumber2 = random_int(1, 6); // Second numéro serveur

    $creditsToAdd = 0;
    $hasWon = false;
    $hasWonTwice = false;

	// default msg and values
    $message = "Better luck next time!";

    // Vérifie les conditions de victoire
	// 6 => means you've won!
    if (6 == $serverNumber1) {
		$hasWon = true;
		$creditsToAdd = 10; // Utilisateur gagne 10 crédits
		$hasWonTwice = false;

        if (6 == $serverNumber2) {
            $creditsToAdd = 500; // Utilisateur gagne 500 crédits
            $hasWonTwice = true;
            $message = "Congratulations, you won 500 credits!";
        } else {
            $message = "Close! You've won 10 credits.";
        }
    }

    updateSpinAndCreditsIfWon($userId, $hasWon, $hasWonTwice, $creditsToAdd, $game_id, $tokenCode);

    return [
        'success' => true,
        //'userNumber1' => $userNumber1,
        'serverNumber1' => $serverNumber1,
        //'userNumber2' => $userNumber2,
        'serverNumber2' => $serverNumber2,
        'wonFirst' => $hasWon,
        'wonSecond' => $hasWonTwice,
        'message' => $message
    ];
}


// Helper function to call can_pay_game_fee endpoint
function call_can_pay_game_fee($jwt, $game_price) {
	global $API_HOST;
	// Replace with your actual endpoint
    $url = $API_HOST."/pvp/games/canPayGameFee?jwt=$jwt&game_price=$game_price"; 

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type:application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $response = curl_exec($ch);
    curl_close($ch);

    return json_decode($response, true);
}

// Helper function to call pay_game_fee endpoint
function call_pay_game_fee($jwt, $game_id, $game_price) {
	global $API_HOST;
	// Replace with your actual endpoint
	$url = $API_HOST."/pvp/games/payGameFee?jwt=$jwt&game_id=$game_id&game_price=$game_price"; 

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type:application/json']);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $response = curl_exec($ch);
    curl_close($ch);

    return json_decode($response, true);
}


// Modification de handleSpinRequest pour utiliser la nouvelle structure de réponse
function handleSpinRequest() {
    
	// why?
	// $input = json_decode(file_get_contents('php://input'), true);
	
	$input=$_REQUEST;
    $jwt = $input['jwt'] ?? '';
    $game_id = 10;

    $game_fee = 1;
    if (empty($jwt)) {
        http_response_code(400);
        echo json_encode(['status' => 'fail', 'message' => 'Please provide a JWT']);
        return;
    }

    $canPayResult = call_can_pay_game_fee($jwt, $game_fee); // Assuming game fee is 1
    if ($canPayResult['reply_code'] === 200 && $canPayResult['can_pay'] == $game_fee) {
        $userId = getUserIdByJwt($jwt);
        if (!$userId) {
            http_response_code(404);
            echo json_encode(['status' => 'fail', 'message' => 'User not found']);
            return;
        }
        $hasUsedSpin = hasUsedSpin($userId);
        if ($hasUsedSpin) {
            http_response_code(400);
            echo json_encode(['status' => 'fail', 'message' => 'Spin already used today']);
            return;
        }

        // Pay the game fee
        $payGameFeeResult = call_pay_game_fee($jwt, $game_id, 1); // Assuming game fee is 1 and $game_id is available
        if ($payGameFeeResult['reply_code'] === 200 && isset($payGameFeeResult['token_code']) ) {
            // Proceed to generate spin
            $result = generateSpin($userId, $game_id, $payGameFeeResult['token_code']);
            http_response_code(200);
            echo json_encode($result);
            return;
        } else {
            http_response_code(400);
            echo json_encode(['status' => 'fail', 'message' => $payGameFeeResult['message']]);
            return;
        }
    } else {
        http_response_code(400);
        echo json_encode(['status' => 'fail', 'message' => $canPayResult['message']]);
        return;
    }
    
    // $userId = getUserIdByUsername($jwt);
    // if (!$userId) {
    //     http_response_code(404);
    //     echo json_encode(['status' => 'fail', 'message' => 'User not found']);
    //     return;
    // }
    // $hasUsedSpin = hasUsedSpin($userId);
    // if ($hasUsedSpin) {
    //     return ['success' => false, 'message' => "Spin already used today"];
    // }else{
    //     $result = generateSpin($userId);
    // }

    // http_response_code(200);
    // echo json_encode($result);
}

header('Content-Type: application/json; charset=utf-8');
handleSpinRequest();  // prints out json content
