<?php
$slugName = "LuckyStamps1";
$GAME_PRICE = 5;


function getUserIdByJwt($jwt) {
    // JWT token to be sent in the API call

    // API endpoint URL
    // $endpoint = "https://services-beta.kata.games/pvp/user/jwt?jwt=" . urlencode($jwt);
$endpoint = "https://cms-beta.kata.games/content/plugins/facade/user/jwt?jwt=" . urlencode($jwt);

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

		curl_close($curl);  // Close cURL session
        return null;
    }

	// API call successful
	$http_status_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
	if ($http_status_code != 200) {
		// Handle non-200 HTTP response
		echo "HTTP Error: $http_status_code";
		curl_close($curl);  // Close cURL session
		return null;
    }

	// Parse and process the API response
	$data = json_decode($response, true);
	// var_dump($data);
	if ($data['reply_code']!=200){
		echo "WARNING: was impossible to find the UserId tied to the Jwt provided: $jwt";
		return null;
	}
	// Access the user_id from the response
	$user_id = $data['user_id'];

	curl_close($curl);  // Close cURL session
	return $user_id;
}


if (isset($_GET['jwt'])) {

    $token = $_GET['jwt'];
    $userId = getUserIdByJwt($token);
	if ($userId==NULL){
		var_dump($userId);
		die("no valid JWT, no userId found" );
	}
    // Send parameters as part of the URL 
    $urlPourTestLuck = 'https://' . $_SERVER['HTTP_HOST'] . "/game-servers/$slugName/testluck.php";
    $params = http_build_query(['user_id' => $userId, 'game_price' => $GAME_PRICE, 'jwt' => $token]);

    // $jsonObj = json_decode(file_get_contents($url . '?' . $params), true);
    header('Content-Type: application/json');
    echo file_get_contents($urlPourTestLuck . '?' . $params);
} else {

    echo '!!! No JWT sent';
}
